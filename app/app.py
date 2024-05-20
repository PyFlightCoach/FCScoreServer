from flask import Flask
from flask_cors import CORS
from flask import request, current_app
import simplejson as json
from functools import wraps
import os
from flightdata import State, NumpyEncoder
from flightanalysis import ManDef, SchedDef, ma, ScheduleAnalysis, ScheduleInfo
import pandas as pd
from pathlib import Path
from time import time
from uuid import uuid4
from loguru import logger
from datetime import datetime

app = Flask(__name__)
CORS(app)


logfile = Path(f'logs/{datetime.now().strftime("%Y_%m_%d_%H_%M_%S")}.log')
logfile.touch()


logger.remove()
logger.add(open(logfile, 'w'), level='INFO')

def log(*args):
    logger.info(",".join([str(v) for v in args]))

def fcscore_route(name, methods=None):
    """decorator for routes to process response and return json string"""
    if methods is None:
        methods = ['GET']
    def outer(f):
        @app.route(name, methods=methods)
        @wraps(f)
        def innfun():
            interaction_id = uuid4()
            start_time = time()
            log( 
                'request', 
                interaction_id,
                methods[0],
                name,
                request.content_length
            )

            response = current_app.response_class(
                json.dumps(
                    f(interaction_id, **json.loads(request.data)), 
                    ignore_nan=True,
                    cls=NumpyEncoder
                ), 
                mimetype="application/json"
            )
        
            log( 
                'response', 
                interaction_id,
                time() - start_time,
                response.content_length
            )

            return response
        return innfun

    return outer

@fcscore_route("/convert_fcj", ['POST'])
def _convert_fcj(id: str, fcj: dict, sinfo: dict):
    try:
        log('convert_fcj', id, sinfo['name'], fcj['parameters']['pilotLat'], fcj['parameters']['pilotLng'], fcj['parameters']['pilotAlt'])
    except Exception as e:
        print(e)
    return ScheduleAnalysis.from_fcj(fcj, ScheduleInfo(**sinfo)).to_dict()

def log_manoeuvre(id, result: ma.Scored):
    if isinstance(result, ma.Scored):
        log('good_analysis', id, result.mdef.info.short_name, result.scores.score())
    else:
        log('failed_analysis', id, result.mdef.info.short_name, result.__class__.__name__)

@fcscore_route("/analyse_manoeuvre", ['POST'])
def _analyse_manoeuvre(id: str, man: dict) -> dict:
    man: ma.Basic = ma.parse_dict(man)
    man.stage = min(man.stage, ma.AlinmentStage.SECONDARY)
    result = man.run_all()
    log_manoeuvre(id, result)
    return result.to_dict()

@fcscore_route("/score_manoeuvre", ["POST"])
def _score_manoevure(id: str, man: dict) -> dict:
    result = ma.parse_dict(man).run_all(False)
    log_manoeuvre(id, result)
    return result.to_dict()


@fcscore_route("/create_fc_json", ['POST'])
def _create_fcj(id: str, sts, mdefs, name, category) -> dict:
    return State(pd.DataFrame.from_dict(sts)).create_fc_json(
        SchedDef([ManDef.from_dict(mdef) for mdef in mdefs]), 
        name, 
        category
    )

@fcscore_route("/version", ['POST'])
def _version(id: str) -> dict:
    ver = os.getenv("PUBLIC_VERSION")
    if ver is None:
        ver = "next"
    return dict(version=ver)

@fcscore_route("/standard_f3a_mps", ["POST"])
def _standard_f3a_mps(id: str):
    from flightanalysis.definition.builders.manbuilder import f3amb
    return f3amb.mps.to_dict()


if __name__ == "__main__":
    app.run(debug=True)