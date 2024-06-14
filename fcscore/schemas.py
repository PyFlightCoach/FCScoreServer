from pydantic import BaseModel
from flightanalysis import ma
import geometry as g
from flightdata import Origin
from typing import Any

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


class El(BaseModel):
    element: str
    start: int
    end: int


class FCJOrigin(BaseModel):
    lat: float
    lng: float
    alt: float
    heading: float

    def create(self):
        return Origin('fcj', g.GPS(self.lat, self.lng, self.alt), self.heading)

class Score(BaseModel):
    intra: float
    inter: float
    positioning: float
    total: float
    k: float


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
    manoeuvre: str=None
    element: str=None

class ShortOutput(BaseModel):
    els: list[El]
    score: Score

    @staticmethod
    def build(man: ma.Scored):
        return ShortOutput(
            els=[El(**v) for v in man.flown.label_ranges('element').to_dict('records')],
            score = Score(
                intra=man.scores.intra.total,
                inter=man.scores.inter.total,
                positioning=man.scores.positioning.total,
                total=man.scores.score(),
                k=man.mdef.info.k
            )
        )

class LongOutout(ShortOutput):
    mdef: dict[str, Any]
    flown: list[State]
    manoeuvre: dict[str,Any]
    template: list[State]
    corrected: dict[str,Any]
    corrected_template: list[State]
    full_scores: ManResult

    @staticmethod
    def build(man: ma.Scored):
        return LongOutout(
            **ShortOutput.build(man).__dict__,
            mdef=man.mdef.to_dict(),
            flown=man.flown.to_dict(),
            manoeuvre=man.manoeuvre.to_dict(),
            template=man.template.to_dict(),
            corrected=man.corrected.to_dict(),
            corrected_template=man.corrected_template.to_dict(),
            full_scores=man.scores.to_dict()
        )


class TLog(BaseModel):
    time:float
    name:str
    score:float
    duration:float
    optimised:bool