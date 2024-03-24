from flightanalysis import ScheduleInfo
from json import load, dump
from flightdata import State, NumpyEncoder
from flightanalysis import ManDef, ScheduleInfo, SchedDef, ma, ScheduleAnalysis
from flightdata import NumpyEncoder


sa = ScheduleAnalysis.from_fcj(load(open(
    '../../data/manual_F3A_P23_22_05_31_00000350.json', 
    'r'
))).run_all()

for man in sa:
    print(man.name)
    dump(
        man.to_dict(), 
        open(f"../FCScoreClient/static/examples/{man.name}.json", 'w'), 
        cls=NumpyEncoder
    )

        