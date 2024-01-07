from flightanalysis import ScheduleInfo
from json import load, dump
from app.funcs import fcj_to_states, f_analyse_manoeuvre
from flightdata import NumpyEncoder

with open('../../data/manual_F3A_P23_22_05_31_00000350.json', 'r') as f:
    data = load(f)


mans = fcj_to_states(
    data, 
    ScheduleInfo.from_fcj_sch(data['parameters']['schedule']).__dict__
)

for mn, man in mans.items():
    print(mn)
    alres = f_analyse_manoeuvre(man['fl'], man['mdef'], -1)
    
    with open(f"../FCScoreClient/static/examples/{mn}.json", 'w') as f:
        dump(alres, f, cls=NumpyEncoder)