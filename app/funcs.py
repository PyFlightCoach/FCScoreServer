from flightdata import Flight
from flightanalysis import (
    State as St, Box, 
    ManoeuvreAnalysis as MA, 
    ManDef, 
    ScheduleInfo,
    SchedDef
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
    flight = Flight.from_fc_json(fcj)

    box = Box.from_fcjson_parmameters(fcj["parameters"])
    sdef = ScheduleInfo.build(**sinfo).definition() #get_schedule_definition(data['fcj']["parameters"]["schedule"][1])

    state = St.from_flight(flight, box).splitter_labels(
        fcj["mans"],
        [m.info.short_name for m in sdef]
    )

    mans = {}
    for mdef in sdef:
        mans[mdef.info.short_name] = dict(
            mdef=mdef.to_dict(),
            fl=state.get_manoeuvre(mdef.info.short_name).to_dict()
        )
    return mans


def align(fl, mdef) -> dict:
    """Perform the Sequence Alignment"""
    st = St.from_dict(fl)
    mdef = ManDef.from_dict(mdef)

    manoeuvre, tp = MA.template(mdef, MA.initial_transform(mdef, st))
    res = MA.alignment(tp, manoeuvre, st)
    return dict(
        dist=res[0],
        al=res[1].to_dict()
    )
    

def score(al, mdef, direction) -> dict:
    aligned = St.from_dict(al)
    mdef: ManDef = ManDef.from_dict(mdef)

    #itrans = MA.initial_transform(mdef, aligned)
    itrans = Transformation(aligned[0].pos, mdef.info.start.initial_rotation(-direction))
    
    intended, int_tp = mdef.create(itrans).add_lines().match_intention(St.from_transform(itrans),aligned)
    corr = MA.correction(mdef, intended, int_tp, aligned)

    intended= intended.copy_directions(corr)
    
    int_tp = intended.el_matched_tp(int_tp[0], aligned)
    
    ma = MA(mdef, aligned, intended, int_tp, corr, corr.create_template(itrans, aligned))

    return dict(
        mdef=mdef.to_dict(),
        intended=ma.intended.to_dict(),
        intended_template = ma.intended_template.to_dict(),
        corrected=ma.corrected.to_dict(),
        corrected_template = ma.corrected_template.to_dict(),
        score=ma.scores().to_dict()
    )


def create_fc_json(sts, mdefs, name, category) -> dict:
    st = St(pd.DataFrame.from_dict(sts))
    return st.create_fc_json(
        SchedDef([ManDef.from_dict(mdef) for mdef in mdefs]), 
        name, 
        category
    )
