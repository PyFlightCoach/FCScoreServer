from flightanalysis import ma, ScheduleInfo, SchedDef, ManDef
from flightdata import State, Flight
from fastapi import Body, HTTPException, APIRouter
import pandas as pd
import fcscore.schemas as s
import os
from typing import Any, Annotated
import traceback
from loguru import logger
from time import time
from fcscore.logs import log_run



router = APIRouter()

@router.post("/run_short_manoeuvre")
async def run_short_manouevre(
    id: Annotated[int, Body(description="The id of the manoeuvre, zero index")],
    direction: Annotated[int, Body(description="The direction the schedule is flown in, 1 for left to right, -1 for right to left")],
    sinfo: Annotated[ScheduleInfo, Body(description="The category and schedule, as per names in flight coach plotter ")], 
    origin: Annotated[s.FCJOrigin, Body(description="Pilot position and heading to locate the box")],
    data: Annotated[list[s.FCJData], Body(description="A slice of the flight coach json data corresponding to this manoeuvre")], 
    optimise_alignment: Annotated[bool, Body(description="Should an alignment optimisation be performed? Aligmnent optimisation takes longer but gives kinder scores")], 
    long_output: Annotated[bool, Body(description="Control the data contained in the response. False for scores and splits only, True for all plotting infrmation.")],
    els: Annotated[list[s.El], Body(description="Optional, list of element split information from a previous run")]=None,
) -> s.ShortOutput | s.LongOutout:
    start = time()
    try:
        
        st = State.from_flight(Flight.parse_fcj_data(
            origin.create(), 
            pd.DataFrame([d.__dict__ for d in data])
        ))
        
        if els is not None:
            df = pd.DataFrame([el.__dict__ for el in els])
            df.columns = ['name', 'start', 'stop']
            st = st.splitter_labels(df.to_dict('records'), target_col='element').label(manoeuvre=data['name'])

        man = ma.Basic(
            id, 
            SchedDef.load(sinfo.fcj_to_pfc())[id], 
            st, 
            direction
        ).proceed().run_all(optimise_alignment, False)

        log_run(start, optimise_alignment, man)

        return s.LongOutout.build(man) if long_output else s.ShortOutput.build(man)
    except Exception as ex:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(ex))


@router.post("/run_long_manoeuvre")
async def run_long_manouevre(
    mdef: Annotated[dict[str, Any], Body()],
    direction: Annotated[int, Body()],
    id: Annotated[int, Body()],
    flown: list[s.State],
    optimise_alignment: Annotated[int, Body()]
) -> s.LongOutout:
    start=time()
    try:
        
        man = ma.Basic(
            id, 
            ManDef.from_dict(mdef), 
            State(pd.DataFrame([fl.__dict__ for fl in flown])), 
            direction, 
        ).proceed().run_all(optimise_alignment)

        log_run(start, optimise_alignment, man)

        return s.LongOutout.build(man)
    except Exception as ex:
        logger.error(traceback.format_exc(ex))
        raise HTTPException(status_code=500, detail=str(ex))

@router.get("/version")
async def read_version() -> str:
    ver = os.getenv("PUBLIC_VERSION")
    if ver is None:
        ver = "next"
    return ver


@router.get("/raw_telemetry")
async def read_raw_telemetry() -> list[s.TLog]:
    df = pd.read_csv('logs/run_history.log')
    return [s.TLog(**r) for r in df.to_dict('records')]


