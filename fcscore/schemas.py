from pydantic import BaseModel
from flightanalysis import ma
from flightdata import Origin
import datetime
import geometry as g
from typing import Any
from enum import Enum
from importlib.metadata import version
from importlib.util import find_spec
from numbers import Number
import subprocess
import os
import numpy as np
import pandas as pd


class LibraryVersions(BaseModel):
    flightanalysis: str
    flightdata: str
    pfc_geometry: str

    @staticmethod
    def get_version(lib: str):
        try:
            return (
                subprocess.run(
                    "git describe --tags",
                    shell=True,
                    check=True,
                    capture_output=True,
                    cwd=os.path.dirname(find_spec(lib.split("_")[-1]).origin),
                )
                .stdout.decode("utf-8")
                .strip()
            )
        except subprocess.CalledProcessError:
            return version(lib)


versions = LibraryVersions(
    **{
        k: LibraryVersions.get_version(k)
        for k in ["flightanalysis", "flightdata", "pfc_geometry"]
    }
)


class Difficulty(Enum):
    EASY = 1
    MEDIUM = 2
    HARD = 3


class Point(BaseModel):
    x: float
    y: float
    z: float

    @staticmethod
    def build(p: g.Point):
        return [Point(x=p.x[0], y=p.y[0], z=p.z[0]) for p in p]


class ManResult(BaseModel):
    intra: dict[str, Any]
    inter: dict[str, Any]
    positioning: dict[str, Any]
    summary: dict[str, float]
    score: float


class State(BaseModel):
    t: float
    dt: float
    x: float
    y: float
    z: float
    rw: float
    rx: float
    ry: float
    rz: float
    u: float = None
    v: float = None
    w: float = None
    p: float = None
    q: float = None
    r: float = None
    du: float = None
    dv: float = None
    dw: float = None
    manoeuvre: str = None
    element: str = None


class El(BaseModel):
    name: str
    start: int
    stop: int


class ScoreProps(BaseModel):
    difficulty: int
    truncate: bool


class Score(BaseModel):
    intra: float
    inter: float
    positioning: float
    total: float


class Result(BaseModel):
    score: Score
    properties: ScoreProps


class FCJData(BaseModel):
    VN: float
    VE: float
    VD: float
    dPD: float
    r: float
    p: float
    yw: float
    N: float
    E: float
    D: float
    time: int
    roll: float
    pitch: float
    yaw: float


class FCJOrigin(BaseModel):
    lat: float
    lng: float
    alt: float
    heading: float
    move_east: float
    move_north: float

    def origin(self):
        """Create a flightdata.Origin object from the FCJOrigin object."""
        return Origin(
            "fcj",
            g.GPS(self.lat, self.lng, self.alt).offset(
                g.Point(self.move_north, self.move_east, 0)
            ),
            np.radians(self.heading),
        )

    def shift(self):
        return self.origin().rotation.transform_point(
            g.Point(self.move_east, -self.move_north, 0)
        )


class FCJParameters(BaseModel):
    rotation: float
    start: int
    stop: int
    moveEast: float
    moveNorth: float
    wingspan: float
    modelwingspan: float
    elevate: float
    originLat: float
    originLng: float
    originAlt: float
    pilotLat: str
    pilotLng: str
    pilotAlt: str
    centerLat: str
    centerLng: str
    centerAlt: str
    schedule: list[str]


class FCJMan(BaseModel):
    name: str
    k: float
    id: str
    sp: int
    wd: float
    start: int
    stop: int
    sel: bool
    background: str


class FCJView(BaseModel):
    position: Point
    target: Point


class FCJManResult(BaseModel):
    score: Score
    els: list[El]


class FCSResult(BaseModel):
    fcs_version: str
    difficulty: float
    date: datetime.date
    manresults: list[FCJManResult]
    total: float


class FCJHumanResult(BaseModel):
    name: str
    date: datetime.date
    scores: list[float]


class FCJ(BaseModel):
    version: str
    comments: str
    name: str
    view: FCJView
    parameters: FCJParameters
    scored: bool
    scores: list[float]
    human_scores: list[FCJHumanResult]
    fcs_scores: list[FCSResult]
    mans: list[FCJMan]
    data: list[FCJData]
    jhash: int



class BinDataInput(BaseModel):
    bin_data: dict
    origin: FCJOrigin



class ShortOutput(BaseModel):
    els: list[El]
    results: list[Result] | None
    fa_version: str
    info: str

    @staticmethod
    def build(
        man: ma.Scored, difficulty: int | str = "all", truncate: bool | str = "all",
        msg: str = None
    ):
        difficulty = [difficulty] if isinstance(difficulty, Number) else [1, 2, 3]
        truncate = [truncate] if isinstance(truncate, bool) else [False, True]

        df = man.flown.label_ranges("element").iloc[:, :3]
        df.columns = ["name", "start", "stop"]
        
        if isinstance(man, ma.Scored):
            if not msg:
                msg = f"Analysis Finished at {pd.Timestamp.now().strftime("%H:%M:%S")}"
        else:
            msg = f"Analysis Failed at {pd.Timestamp.now().strftime("%H:%M:%S")}"
        return ShortOutput(
            els=[El(**v) for v in df.to_dict("records")],
            results=[
                Result(
                    score=Score(**man.scores.score_summary(diff, trunc)),
                    properties=ScoreProps(difficulty=diff, truncate=trunc),
                )
                for diff in difficulty
                for trunc in truncate
            ] if isinstance(man, ma.Scored) else None,
            fa_version=versions.flightanalysis,
            info=msg
        )


class LongOutout(ShortOutput):
    mdef: dict[str, Any]
    flown: list[State]
    manoeuvre: dict[str, Any]
    template: list[State]
    corrected: dict[str, Any] | None
    corrected_template: list[State] | None
    full_scores: ManResult | None

    @staticmethod
    def build(
        man: ma.Scored, difficulty: int | str = "all", truncate: bool | str = "all",
        msg: str=None
    ):
        return LongOutout(
            **ShortOutput.build(man, difficulty, truncate, msg).__dict__,
            mdef=man.mdef.to_dict(True),
            flown=man.flown.to_dict(),
            manoeuvre=man.manoeuvre.to_dict(),
            template=man.template.to_dict(),
            corrected= man.corrected.to_dict() if isinstance(man, ma.Scored) else None,
            corrected_template=man.corrected_template.to_dict() if isinstance(man, ma.Scored) else None,
            full_scores=ManResult(**man.scores.to_dict()) if isinstance(man, ma.Scored) else None,
        )


class TLog(BaseModel):
    time: float
    name: str
    score: float
    duration: float
    optimised: bool
