from simplejson import load, dump
from app.funcs import fcj_to_states, align, score
from app.app import NumpyEncoder

with open('api/examples/manual_F3A_P23_22_05_31_00000350.json', 'r') as f:
    fcj = load(f)

mans = fcj_to_states(fcj, dict(category="f3a", name="p23"))

for k, m in mans.items():
    print(m['mdef']['info']['short_name'])
    al = align(fl=m['fl'], mdef=m['mdef'])

    _score = score(al=al['al'], mdef = m['mdef'])

    with open(f'api/examples/{k}.json', 'w') as f:
        dump(dict(**al,busy=False,**_score,), f, cls=NumpyEncoder, ignore_nan=True)
    
