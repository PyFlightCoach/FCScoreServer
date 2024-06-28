from flightanalysis import ma, ScheduleInfo, SchedDef, ManDef
from flightdata import State, Flight
from fastapi import Body, HTTPException, APIRouter
import pandas as pd
import fcscore.schemas as s
from typing import Any, Annotated
import traceback
from time import time
import logging
from fastapi.responses import FileResponse
import geometry as g
import numpy as np
from importlib.metadata import version
import git


logger = logging.getLogger(__name__)

router = APIRouter()

@router.post(
    "/calculate_direction",
    description="given a single datapoint in the flight coach json data work out if the plane is pointing to the left or right of the box"
)
async def calculate_direction(
    heading: Annotated[float, Body(description="Pilot heading to locate the box")],
    data: Annotated[s.FCJData, Body(description="A data point from the flight coach json data, usually the first point of the first manoeuvre")],
) -> s.Direction:
    rotation = g.Euler(np.pi, 0, heading + np.pi/2)
    att = rotation * g.Euldeg(data.r, data.p, data.yw)
    vel = att.inverse().transform_point(rotation.transform_point(
            g.Point(data.VN, data.VE, data.VD)
    ))
    return s.Direction(int(State.from_transform(g.Transformation(g.P0(), att), vel=vel).direction()[0]))

@router.post("/run_short_manoeuvre")
async def run_short_manouevre(
    id: Annotated[int, Body(description="The id of the manoeuvre, zero index")],
    direction: Annotated[s.Direction, Body(description="The direction the schedule is flown in, 1 for left to right, -1 for right to left")],
    sinfo: Annotated[ScheduleInfo, Body(description="The category and schedule, as per names in flight coach plotter ")], 
    site: Annotated[s.FCJOrigin, Body(description="Pilot position and heading to locate the box")],
    data: Annotated[list[s.FCJData], Body(description="A slice of the flight coach json data corresponding to this manoeuvre")], 
    optimise_alignment: Annotated[bool, Body(description="Should an alignment optimisation be performed? Aligmnent optimisation takes longer but gives kinder scores")], 
    long_output: Annotated[bool, Body(description="Control the data contained in the response. False for scores and splits only, True for all plotting infrmation.")]=False,
    els: Annotated[list[s.El], Body(description="Optional, list of element split information from a previous run")]=None,
    difficulty: Annotated[int | str, Body(description="Optional, the difficulty level of the manoeuvre, 1, 2 or 3, or 'all'")]='all',
    truncate: Annotated[bool | str, Body(description="Optional, truncate the downgrades before adding up, or 'both'")]=False
) -> s.ShortOutput | s.LongOutout:
    start = time()
    try:
        st = State.from_flight(Flight.parse_fcj_data(
            site.create(), 
            pd.DataFrame([d.__dict__ for d in data])
        ))
        mdef = SchedDef.load(sinfo.fcj_to_pfc())[id]

        if els is not None:
            df = pd.DataFrame([el.__dict__ for el in els])
            st = st.splitter_labels(df.to_dict('records'), target_col='element').label(manoeuvre=mdef.info.short_name)

        man = ma.Basic(
            id, mdef, st, -direction.value
        ).proceed().run_all(optimise_alignment, False)
        
        logger.info(f'run_short,{time()-start},{man.mdef.info.short_name},{man.scores.score()}')
        return s.LongOutout.build(man, difficulty, truncate) if long_output else s.ShortOutput.build(man, difficulty, truncate)
    except Exception as ex:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/run_long_manoeuvre")
async def run_long_manouevre(
    mdef: Annotated[dict[str, Any], Body()],
    direction: Annotated[int, Body()],
    id: Annotated[int, Body()],
    flown: list[s.State],
    optimise_alignment: Annotated[int, Body()],
    difficulty: Annotated[int | str, Body(description="Optional, the difficulty level of the manoeuvre, 1, 2 or 3, or 'all'")]=3,
    truncate: Annotated[bool | str, Body(description="Optional, truncate the downgrades before adding up, or 'both'")]=False
) -> s.LongOutout:
    start=time()
    try:
        
        man = ma.Basic(
            id, 
            ManDef.from_dict(mdef), 
            State(pd.DataFrame([fl.__dict__ for fl in flown])), 
            -direction, 
        ).proceed().run_all(optimise_alignment)

        logger.info(f'run_long,{time()-start},{man.mdef.info.short_name},{man.scores.score()}')
        return s.LongOutout.build(man, difficulty, truncate)
    except Exception as ex:
        logger.error(traceback.format_exc(ex))
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/version")
async def read_version() -> str:
    repo = git.Repo()
    tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    return str(tags[-1])

@router.get("/fa_version")
async def read_fa_version() -> str:
    return version('flightanalysis')


@router.get("/library_versions")
async def read_library_versions() -> s.LibraryVersions:
    return s.LibraryVersions.read()


@router.get("/telemetry", response_class=FileResponse)
async def read_telemetry():
    return 'logs/gunicorn.root.log'


