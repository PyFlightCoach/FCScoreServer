from flightdata import Flight, State
from flightanalysis import ScheduleInfo
from json import load, dump
from app.funcs import fcj_to_states, align, score
from flightdata import NumpyEncoder

with open('../../data/manual_F3A_P23_22_05_31_00000350.json', 'r') as f:
    data = load(f)


mans = fcj_to_states(
    data, 
    ScheduleInfo.from_fcj_sch(data['parameters']['schedule']).__dict__
)

for mn, man in mans.items():

    alres = align(man['fl'], man['mdef'])
    man['al'] = alres['al']
    man['dist'] = alres['dist']
    res = score(man['al'], man['mdef'], -1)
    for k, v in res.items():
        man[k] = res[k]

    del man['fl']

    with open(f"../FCScoreClient/static/examples/{mn}.json", 'w') as f:
        dump(man, f, cls=NumpyEncoder)