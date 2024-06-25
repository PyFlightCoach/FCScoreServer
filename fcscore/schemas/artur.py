from pydantic import BaseModel
from enum import Enum
from fcscore.schemas.pfc  import Difficulty


class CalcOptions(BaseModel):
    operation: str
    difficulty: list[Difficulty]
    truncate: bool
    optimise: bool


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

class Manoeuvre(BaseModel)

class ScoreInput(BaseModel):
    requese: CalcOptions
    flight: FlightInfo