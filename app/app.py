from flask import Flask
from flask_cors import CORS
from flask import request, current_app
import simplejson as json
from functools import wraps
import os
from flightdata import State, NumpyEncoder
from flightanalysis import ManDef, SchedDef, ma, ScheduleAnalysis, ScheduleInfo
import pandas as pd
from loguru import logger
import sys

logger.enable("flightanalysis")
logger.remove()
logger.add(sys.stderr, level="DEBUG" )

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
def _convert_fcj(fcj: dict, sinfo: dict):
    return ScheduleAnalysis.from_fcj(fcj, ScheduleInfo(**sinfo)).to_dict()

@fcscore_route("/analyse_manoeuvre", ['POST'])
def _analyse_manoeuvre(man: dict) -> dict:
    man = ma.parse_dict(man)
    man.stage = min(man.stage, ma.AlinmentStage.SECONDARY)
    return man.run_all().to_dict()

@fcscore_route("/score_manoeuvre", ["POST"])
def _score_manoevure(man: dict) -> dict:
    return ma.parse_dict(man).run_all(False).to_dict()


@fcscore_route("/create_fc_json", ['POST'])
def _create_fcj(sts, mdefs, name, category) -> dict:
    return State(pd.DataFrame.from_dict(sts)).create_fc_json(
        SchedDef([ManDef.from_dict(mdef) for mdef in mdefs]), 
        name, 
        category
    )

@fcscore_route("/version", ['POST'])
def _version() -> dict:
    ver = os.getenv("PUBLIC_VERSION")
    if ver is None:
        ver = "next"
    return dict(version=ver)

@fcscore_route("/standard_f3a_mps", ["POST"])
def _standard_f3a_mps():
    from flightanalysis.definition.builders.manbuilder import f3amb
    return f3amb.mps.to_dict()


if __name__ == "__main__":
    app.run(debug=True)