
from flightdata import Flight
from flightanalysis import (
    State as St, Box, 
    ManoeuvreAnalysis as MA, 
    ManDef, 
    ScheduleInfo
)

from flask import Blueprint, request, jsonify, current_app
from json import dumps, loads
import json 
import numpy as np
from functools import wraps
import api.funcs as funcs
from pathlib import Path

api = Blueprint('api', __name__)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return json.JSONEncoder.default(self, obj)
    

def fcscore_route(name, methods=None):
    """decorator for routes to process response and return json string"""
    if methods is None:
        methods = ['GET']
    def outer(f):
        @api.route(name, methods=methods)
        @wraps(f)
        def innfun():
            return current_app.response_class(
                dumps(
                    f(**loads(request.data)), 
                    cls=NumpyEncoder
                ), 
                mimetype="application/json"
            )
        return innfun

    return outer

@fcscore_route("/convert_fcj", ['POST'])
def _fcj_to_states(fcj: dict, sinfo: dict):
    return funcs.fcj_to_states(fcj, sinfo)


@fcscore_route("/convert_fcj_example", ['POST'])
def _fcj_to_states_example():
    return loads('api/examples/fcj_to_states.json')

@fcscore_route("/align", ['POST'])
def _align(fl, mdef) -> dict:
    return funcs.align(fl, mdef)

@fcscore_route("/align_example", ['POST'])
def _align_example(man) -> dict:
    return loads(f'api/examples/align_{man["man"]}.json')

@fcscore_route("/score", ['POST'])
def _score(al, mdef) -> dict:
    return funcs.score(al, mdef)

@fcscore_route("/score_example", ['POST'])
def _score_example(man) -> dict:
    return loads(f'api/examples/score_{man["man"]}.json')


@fcscore_route("/example_manlist", ['POST'])
def example_mans() -> dict:
    return [p.stem.split('_')[1] for p in sorted(Path(("api/examples/")).glob("align_*.json"))]
