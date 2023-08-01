
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

api = Blueprint('api', __name__)



@api.route("/test")
def test_server():
    print("testing")
    return dict(test="success")

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)
    

@api.route("/convert_fcj", methods=['POST'])
def fcj_to_states() -> dict:
    """Format the flight coach json in a more useful way so less data can be sent
    forwards and backwards in subsequent requests
    request data contains: dict(str: any)
    {
        "fcj": fcjson, 
        "sinfo": {
            "category": f3a, 
            "name": p23
    }}
    """
    data = loads(request.data)
    flight = Flight.from_fc_json(data['fcj'])

    box = Box.from_fcjson_parmameters(data['fcj']["parameters"])
    state = St.from_flight(flight, box).splitter_labels(data['fcj']["mans"])

    
    sdef = ScheduleInfo.build(*data['sinfo']) #get_schedule_definition(data['fcj']["parameters"]["schedule"][1])

    mans = {}
    for mdef in sdef:
        mans[mdef.info.short_name] = dict(
            mdef=mdef.to_dict(),
            fl=state.get_manoeuvre(mdef.info.short_name).to_dict()
        )
    return current_app.response_class(dumps(mans, cls=NumpyEncoder), mimetype="application/json")

@api.route("/align_manoevre")
def align(man: dict) -> dict:
    """Perform the Sequence Alignment"""

    st = St.from_dict(man['fl'])
    mdef = ManDef.from_dict(man['mdef'])

    manoeuvre, tp = MA.template(mdef, MA.initial_transform(mdef, st))
    al = MA.alignment(tp, manoeuvre, st)
    
    return al.to_dict()


@api.route("/edit_alignment")
def edit_alignment(almod: dict) -> dict:
    """shifts the end time of an element for an element"""
    return St.from_dict(almod['fl']).shift_labels("element", almod['elname'], almod['stp']).to_dict()


@api.route("/analyse_manoevre")
def analyse(man: dict) -> dict:

    aligned = St.from_dict(man['aligned'])
    mdef: ManDef = ManDef.from_dict(man['mdef'])
    itrans = MA.initial_transform(mdef, aligned)
    intended, int_tp = mdef.create(itrans).add_lines().match_intention(St.from_transform(itrans),aligned)
    corr = MA.correction(mdef, intended, int_tp, aligned)
    ma = MA(mdef, aligned, intended, int_tp, corr, corr.create_template(itrans, aligned))

    scores = ma.scores()

    res = ma.to_dict()

    res['scores'] = scores.to_dict()
    res['score_summary'] = scores.summary()
    res['score'] = scores.score()
    res['stage'] = 'results'
    return res

