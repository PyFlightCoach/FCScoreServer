from flightanalysis import ScheduleAnalysis, ma
from flightdata import State, Flight, Origin
from geometry import GPS
from .conftest import client, fcj, short_manoeuvre, long_manoeuvre
from fastapi.testclient import TestClient
import fcscore.schemas as s
import io

def test_version(client: TestClient):
    response = client.get('/version')
    assert response.status_code == 200, response.text
    assert response.json() == 'next'


def test_run_short_manoeuvre(client: TestClient, short_manoeuvre: dict):
    response = client.post('/run_short_manoeuvre', json=short_manoeuvre)
    assert response.status_code == 200, response.json()['detail']
    data = response.json()
    assert 'els' in data
    assert data['scores'][0]['positioning'] > 0


def test_run_long_manoeuvre(client: TestClient, long_manoeuvre: dict):
    response = client.post('/run_long_manoeuvre', json=long_manoeuvre)
    assert response.status_code == 200, response.json()['detail']
    data = response.json()
    assert 'full_scores' in data


def test_telemetry(client: TestClient):
    file = client.get('/telemetry')
    
    assert 'INFO' in io.StringIO(file.text).readline()