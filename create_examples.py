from json import load, dump
from api.funcs import fcj_to_states, align, score
from api import NumpyEncoder

with open('api/examples/manual_F3A_P23_22_05_31_00000350.json', 'r') as f:
    fcj = load(f)

mans = fcj_to_states(fcj, dict(category="f3a", name="p23"))

with open('api/examples/fcj_to_states.json', 'w') as f:
    dump(mans, f, cls=NumpyEncoder)

for k, m in mans.items():

    al = align(fl=m['fl'], mdef=m['mdef'])

    with open(f'api/examples/align_{k}.json', 'w') as f:
        dump(m, f, cls=NumpyEncoder)

    _score = score(al=al, mdef = m['mdef'])

    with open(f'api/examples/score_{k}.json', 'w') as f:
        dump(_score, f, cls=NumpyEncoder)
