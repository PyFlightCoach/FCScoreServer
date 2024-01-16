from flightdata import Flight
from flightdata import State, Origin
from flightanalysis import (
    ManoeuvreAnalysis as MA, 
    ManDef, 
    ScheduleInfo,
    SchedDef,
    Manoeuvre
)
import numpy as np
import pandas as pd
from geometry import Transformation


def fcj_to_states(fcj: dict, sinfo: dict):
    """Format the flight coach json in a more useful way so less data can be sent
    forwards and backwards in subsequent requests
    request data contains: dict(str: any)
    {
        "fcj": {fcjson}, 
        "sinfo": {
            "category": f3a, 
            "name": p23
    }}
    """
    flight = Flight.from_fc_json(fcj).remove_time_flutter().butter_filter(4,5)

    box = Origin.from_fcjson_parmameters(fcj["parameters"])
    sdef = ScheduleInfo.build(**sinfo).definition() #get_schedule_definition(data['fcj']["parameters"]["schedule"][1])

    state = State.from_flight(flight, box).splitter_labels(
        fcj["mans"],
        [m.info.short_name for m in sdef]
    )

    mans = {}
    for mdef in sdef:
        mans[mdef.info.short_name] = dict(
            mdef=mdef.to_dict(),
            flown=state.get_manoeuvre(mdef.info.short_name).to_dict()
        )
    return mans


def analyse_manoeuvre(flown: State, mdef: ManDef, direction: int):
    res = align(flown, mdef, direction)
    return score_manoeuvre(**res) if res.pop('success') else res

def f_analyse_manoeuvre(flown, mdef, direction):
    flown = State.from_dict(flown)
    mdef = ManDef.from_dict(mdef)
    return {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in analyse_manoeuvre(flown, mdef, direction).items()}
    

def align(flown: State, mdef: ManDef, direction: int) -> dict:
    """Perform the Sequence Alignment"""
    itrans = Transformation(flown[0].pos, mdef.info.start.initial_rotation(direction))
    manoeuvre, tp = MA.basic_manoeuvre(mdef, itrans)
    dist, aligned = State.align(flown, tp, 10)
    try:
        manoeuvre, tp = manoeuvre.match_intention(tp[0], aligned)
        dist, aligned = State.align(aligned, tp, 10, mirror=False)
        manoeuvre, tp = manoeuvre.match_intention(tp[0], aligned)
        success = True
    except Exception as e:
        success = False
    return dict(success=success, mdef=mdef, manoeuvre=manoeuvre, aligned=aligned, direction=direction)


def score_manoeuvre(mdef: ManDef, manoeuvre: Manoeuvre, aligned: State, direction: int):
    istate = State.from_transform(Transformation(aligned[0].pos, mdef.info.start.initial_rotation(direction)))
    
    aligned = manoeuvre.optimise_alignment(istate, aligned)
    manoeuvre, template = manoeuvre.match_intention(istate, aligned) 
    
    mdef = ManDef(mdef.info, mdef.mps.update_defaults(manoeuvre), mdef.eds)
    corrected_manoeuvre = mdef.create(istate.transform).add_lines()
    
    manoeuvre = manoeuvre.copy_directions(corrected_manoeuvre)
    template = manoeuvre.el_matched_tp(istate, aligned)
    
    corrected_template = corrected_manoeuvre.create_template(istate, aligned)

    return dict(
        mdef=mdef,
        manoeuvre=manoeuvre,
        aligned=aligned,
        template=template,
        corrected=corrected_manoeuvre,
        corrected_template = corrected_template,
        score=MA(mdef, aligned, manoeuvre, template, corrected_manoeuvre, corrected_template).scores()
    )
    
def f_score_manoeuvre(mdef, manoeuvre, aligned, direction):
    mdef = ManDef.from_dict(mdef)
    manoeuvre = Manoeuvre.from_dict(manoeuvre)
    al = State.from_dict(aligned)
    return {k: v.to_dict() if hasattr(v, 'to_dict') else v for k, v in score_manoeuvre(mdef, manoeuvre, al, direction).items()}


def create_fc_json(sts, mdefs, name, category) -> dict:
    st = State(pd.DataFrame.from_dict(sts))
    return st.create_fc_json(
        SchedDef([ManDef.from_dict(mdef) for mdef in mdefs]), 
        name, 
        category
    )


def standard_f3a_mps() -> dict:
    from flightanalysis.definition.builders.manbuilder import f3amb
    return f3amb.mps.to_dict()
