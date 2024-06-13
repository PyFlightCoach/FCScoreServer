from .conftest import fcj, man
import server.schemas as s
from flightanalysis import ScheduleInfo, ma, SchedDef


def test_sinfo(fcj: dict):
    sinfo = ScheduleInfo(*fcj['parameters']['schedule']).fcj_to_pfc()
    assert sinfo.category == 'f3a'
    assert sinfo.name == 'f25'


def test_fcjdata(fcj: dict):
    data = [s.FCJData(**d) for d in fcj['data'][100:200]]
    assert isinstance(data[0], s.FCJData)
    

def test_long_output(man: ma.Scored):
    res = s.LongOutout.build(man)
    assert isinstance(res, s.LongOutout)

