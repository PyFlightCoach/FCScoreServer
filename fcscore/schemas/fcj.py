from pydantic import BaseModel
import geometry as g
from flightdata import Origin
from .pfc import Point, Score, El
import datetime


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
            'fcj', 
            g.GPS(self.lat, self.lng, self.alt).offset(
                g.Point(self.move_north, self.move_east,0)
            ), 
            self.heading
        )

    def shift(self):
        return self.origin().rotation.transform_point(g.Point(
            self.move_east,
            -self.move_north,
            0
        ))

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