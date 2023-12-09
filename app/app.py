from flask import Flask
from flask_cors import CORS
from flask import request, current_app
import simplejson as json
import numpy as np
from functools import wraps
import app.funcs as funcs
from pathlib import Path
from flightdata import NumpyEncoder
import os

app = Flask(__name__)
CORS(app)


def fcscore_route(name, methods=None):
    """decorator for routes to process response and return json string"""
    if methods is None:
        methods = ['GET']
    def outer(f):
        @app.route(name, methods=methods)
        @wraps(f)
        def innfun():
            return current_app.response_class(
                json.dumps(
                    f(**json.loads(request.data)), 
                    ignore_nan=True,
                    cls=NumpyEncoder
                ), 
                mimetype="application/json"
            )
        return innfun

    return outer

@fcscore_route("/convert_fcj", ['POST'])
def _fcj_to_states(fcj: dict, sinfo: dict):
    return funcs.fcj_to_states(fcj, sinfo)


@fcscore_route("/example", ['POST'])
def _example(man):
    with open(f'app/examples/{man}.json', 'r') as f:
        return json.load(f)

@fcscore_route("/align", ['POST'])
def _align(fl, mdef) -> dict:
    return funcs.align(fl, mdef)

@fcscore_route("/score", ['POST'])
def _score(al, mdef, direction) -> dict:
    return funcs.score(al, mdef, direction)

@fcscore_route("/example_manlist", ['POST'])
def example_mans() -> dict:
    return [p.stem for p in sorted(Path(("app/examples/")).glob("*.json"))]

@fcscore_route("/create_fc_json", ['POST'])
def _create_fcj(sts, mdefs, name, category) -> dict:
    return funcs.create_fc_json(sts, mdefs, name, category)

@fcscore_route("/version", ['POST'])
def _version() -> dict:
    ver = os.getenv("PUBLIC_VERSION")
    if ver is None:
        ver = "next"
    return dict(version=ver)

@fcscore_route("/standard_f3a_mps", ["POST"])
def _standard_f3a_mps():
    return funcs.standard_f3a_mps()


if __name__ == "__main__":
    app.run(debug=True)