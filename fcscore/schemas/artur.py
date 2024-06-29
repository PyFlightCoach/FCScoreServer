from pydantic import BaseModel
from .pfc import Difficulty
from .fcj import FCJData, El


class FCScoreInfo(BaseModel):
    id: int
    userID: str

class CalcOptions(BaseModel):
    operation: str
    optimise: bool
    difficulty: Difficulty | str
    truncate: bool | str

class GPS(BaseModel):
    lat: float
    lng: float
    alt: float

class FlightInfo(BaseModel):
    file: str
    date: str
    pilotN: str
    pilotC: str
    pilotID: str
    location: str
    competitionID: str
    competitionName: str
    pilotP: GPS
    centerP: GPS
    originP: GPS
    style: str
    schedule: str
    direction: int


class SiteInfo(BaseModel):
    site: str
    rotation: float
    pilotdB: GPS
    centerdB: GPS
    move_east: float
    move_north: float

class ManoeuvreInData(BaseModel):
    id: int
    shortName: str
    k: float
    els: list[El] | None
    data: list[FCJData]


class ScoreData(BaseModel):
    difficulty:  int
    penalties: list[float]
    truncatedPenalties: list[float]
    score: float
    truncatedScore: float
    total: float
    truncatedTotal: float


class ManoeuvreOutData(BaseModel):
    id: int
    shortName: str
    k: float
    els: list[El]
    scores: list[ScoreData]
    

class ScoreManoeuvre(BaseModel):
    fcscore: FCScoreInfo
    request: CalcOptions
    flight: FlightInfo
    site: SiteInfo
    manoeuvre: ManoeuvreInData


class ScoreManoeuvreResponse(BaseModel):
    fcscore: FCScoreInfo
    request: CalcOptions
    flight: FlightInfo
    site: SiteInfo
    manoeuvre: ManoeuvreOutData