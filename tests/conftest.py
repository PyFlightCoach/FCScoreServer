from json import load
from fastapi.testclient import TestClient
from pytest import fixture
from main import app
from flightanalysis import ma


@fixture(scope="module")
def client():
    with TestClient(app) as c:
      yield c

@fixture(scope='module')
def fcj() -> dict:
    with open('tests/data/manual_F3A FAI_F25_24_06_10_00000122.json') as f:
        return load(f)

@fixture(scope='module')
def short_manoeuvre(fcj: dict):
    return dict(
        id=0,
        direction=1,
        sinfo=dict(category='F3A FAI', name='F25'),
        site=dict(
            lat=fcj['parameters']['pilotLat'],
            lng=fcj['parameters']['pilotLng'],
            alt=fcj['parameters']['pilotAlt'],
            heading=fcj['parameters']['rotation'],
            move_north=fcj['parameters']['moveNorth'],
            move_east=fcj['parameters']['moveEast']
        ),
        data=fcj['data'][fcj['mans'][1]['start']:fcj['mans'][1]['stop']],
        optimise_alignment=False,
        long_output=False,
        difficulty='all',
        truncate='both'
    )


@fixture(scope='module')
def man():
    return ma.parse_dict(load(open('tests/data/sqL.json' ,'r')))

@fixture(scope='module')
def long_manoeuvre(man: ma.Scored):
    return dict(
        mdef=man.mdef.to_dict(),
        direction=1,
        id=2,
        flown=man.flown.to_dict(),
        optimise_alignment=False,
        difficulty='all',
        truncate='both'
    )