from pydantic import BaseModel
from flightanalysis import ma
from flightanalysis import ScheduleInfo, ManDef, SchedDef, schedule_library
from flightdata import State as St
import geometry as g
from typing import Any
from enum import Enum
from importlib.metadata import version
from importlib.util import find_spec
from numbers import Number
import subprocess
import os
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


class Direction(Enum):
    LEFT_TO_RIGHT = 1
    RIGHT_TO_LEFT = -1
    INFER = 0

    @staticmethod
    def parse(s: str):
        try:
            lind = s.lower().index("l")
            rind = s.lower().index("r")
        except ValueError:
            return Direction.INFER
        return Direction.LEFT_TO_RIGHT if lind < rind else Direction.RIGHT_TO_LEFT


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
    u: float
    v: float
    w: float
    p: float
    q: float
    r: float
    du: float
    dv: float
    dw: float
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


class ShortOutput(BaseModel):
    els: list[El]
    results: list[Result]
    fa_version: str
    k: float

    @staticmethod
    def build(
        man: ma.Scored, difficulty: int | str = "all", truncate: bool | str = "all"
    ):
        difficulty = [difficulty] if isinstance(difficulty, Number) else [1, 2, 3]
        truncate = [truncate] if isinstance(truncate, bool) else [False, True]

        df = man.flown.label_ranges("element").iloc[:, :3]
        df.columns = ["name", "start", "stop"]
        return ShortOutput(
            els=[El(**v) for v in df.to_dict("records")],
            results=[
                Result(
                    score=Score(**man.scores.score_summary(diff, trunc)),
                    properties=ScoreProps(difficulty=diff, truncate=trunc),
                )
                for diff in difficulty
                for trunc in truncate
            ],
            fa_version=versions.flightanalysis,
            k=man.mdef.info.k,
        )


class LongOutout(ShortOutput):
    mdef: dict[str, Any]
    flown: list[State]
    manoeuvre: dict[str, Any]
    template: list[State]
    corrected: dict[str, Any]
    corrected_template: list[State]
    full_scores: ManResult

    @staticmethod
    def build(
        man: ma.Scored, difficulty: int | str = "all", truncate: bool | str = "all"
    ):
        return LongOutout(
            **ShortOutput.build(man, difficulty, truncate).__dict__,
            mdef=man.mdef.to_dict(True),
            flown=man.flown.to_dict(),
            manoeuvre=man.manoeuvre.to_dict(),
            template=man.template.to_dict(),
            corrected=man.corrected.to_dict(),
            corrected_template=man.corrected_template.to_dict(),
            full_scores=man.scores.to_dict(),
        )


class TLog(BaseModel):
    time: float
    name: str
    score: float
    duration: float
    optimised: bool


class ManDetails(BaseModel):
    name: str
    id: int
    k: float

