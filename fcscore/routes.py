import logging
import os
import traceback
from time import time
from typing import Annotated

import geometry as g
import numpy as np
import pandas as pd
from fastapi import APIRouter, Body, HTTPException
from fastapi.responses import FileResponse
from flightanalysis import ManDetails, ManDef, ScheduleInfo, ma, schedule_library
from flightanalysis.definition.maninfo import Heading
from flightdata import BinData, Flight, State

import fcscore.schemas as s

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/calculate_direction",
    description="given a single datapoint in the flight coach json data work out if the plane is pointing to the left or right of the box",
)
async def calculate_direction(
    heading: Annotated[float, Body(description="Pilot heading to locate the box")],
    data: Annotated[
        s.State, Body(description="the first point of the first manoeuvre")
    ],
) -> s.Direction:
    rotation = g.Euler(np.pi, 0, np.radians(heading) + np.pi / 2)
    att = rotation * g.Euldeg(data.r, data.p, data.yw)
    vel = att.inverse().transform_point(
        rotation.transform_point(g.Point(data.VN, data.VE, data.VD))
    )
    return s.Direction(
        int(State.from_transform(g.Transformation(g.P0(), att), vel=vel).direction()[0])
    )


def rate_check(st: State):
    log_rate = len(st.data) / st.duration
    assert (
        abs(log_rate - 25) < 2
    ), f"FCScore expects a logging rate of {25}Hz, but the data provided is at {int(log_rate)}Hz"

    
def create_state_from_states(sts: list[s.State]) -> State:
    return State(pd.DataFrame([fl.__dict__ for fl in sts]).set_index("t", drop=False))


@router.post("/analyse_manoeuvre")
async def analyse_manoeuvre(
    name: Annotated[str, Body()],
    category: Annotated[str, Body()],
    schedule: Annotated[str, Body()],
    optimise_alignment: Annotated[bool, Body()],
    entry: Annotated[Heading, Body(description="The direction the manoeuvre should start in")],
    exit: Annotated[Heading, Body(description="The direction the manoeuvre should end in")],
    flown: Annotated[list[s.State], Body()],
) -> s.LongOutout:
    start = time()
    try:
        st = create_state_from_states(flown)
        rate_check(st)
        mdef = ManDef.load(ScheduleInfo(category, schedule), name)
        
        man = (
            ma.Basic(id, mdef, st, entry, exit)
            .proceed()
            .run_all(optimise_alignment)
        )
#
        logger.info(
            f"run_long,{time()-start},{man.mdef.info.short_name},{man.scores.score()}"
        )
        return s.LongOutout.build(man, "all", "both")
    except Exception as ex:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(ex))


@router.get("/version")
async def read_version() -> str:
    return os.environ["PUBLIC_VERSION"] if "PUBLIC_VERSION" in os.environ else "next"


@router.get("/fa_version")
async def read_fa_version() -> str:
    return s.versions.flightanalysis  # version("flightanalysis")


@router.get("/library_versions")
async def read_library_versions() -> s.LibraryVersions:
    return s.versions


@router.get("/telemetry", response_class=FileResponse)
async def read_telemetry():
    return "logs/gunicorn.root.log"


@router.post("/create_state")
def create_state(data: dict, site: s.FCJOrigin) -> list[dict]:
    fl = Flight.from_log(BinData.parse_json(data))

    return State.from_flight(fl, site.origin()).to_dict()


@router.post(
    "/create_state_fcj",
    description="Convert a list of FCJData to a list of State",
)
async def create_state_fcj(data: list[s.FCJData], site: s.FCJOrigin) -> list[dict]:
    return State.from_flight(
        Flight.parse_fcj_data(
            pd.DataFrame([d.__dict__ for d in data]), site.origin(), site.shift()
        )
    ).to_dict()


@router.post("/convert_schedule_info")
def convert_schedule_info(
    sinfo: Annotated[ScheduleInfo, Body()],
) -> ScheduleInfo:
    return sinfo.fcj_to_pfc()

@router.get("/categories")
def list_disciplines() -> list[str]:
    return list(set([s.category for s in schedule_library]))


@router.get("/{category}/schedules")
def list_schedules(category: str) -> list[str]:
    return [s.name for s in schedule_library if s.category == category]


@router.get("/{category}/{schedule}/manoeuvres")
def list_manoeuvres(category: str, schedule: str) -> list[ManDetails]:
    return ScheduleInfo(category, schedule).manoeuvre_details()
