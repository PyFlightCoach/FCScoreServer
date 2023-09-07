from flask import Flask
from flask_cors import CORS
from flask import request, current_app
import simplejson
import numpy as np
from functools import wraps
import app.funcs as funcs
from pathlib import Path


app = Flask(__name__)
CORS(app)


class NumpyEncoder(simplejson.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        else:
            return simplejson.JSONEncoder.default(self, obj)
    


def fcscore_route(name, methods=None):
    """decorator for routes to process response and return json string"""
    if methods is None:
        methods = ['GET']
    def outer(f):
        @app.route(name, methods=methods)
        @wraps(f)
        def innfun():
            return current_app.response_class(
                simplejson.dumps(
                    f(**simplejson.loads(request.data)), 
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
        return simplejson.load(f)

@fcscore_route("/align", ['POST'])
def _align(fl, mdef) -> dict:
    return funcs.align(fl, mdef)

@fcscore_route("/score", ['POST'])
def _score(al, mdef) -> dict:
    return funcs.score(al, mdef)

@fcscore_route("/example_manlist", ['POST'])
def example_mans() -> dict:
    return [p.stem for p in sorted(Path(("app/examples/")).glob("*.json"))]


if __name__ == "__main__":
    app.run(debug=True)