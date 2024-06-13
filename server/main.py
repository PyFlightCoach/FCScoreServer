import uvicorn
from flightanalysis import ma, ScheduleInfo, SchedDef, ManDef, Manoeuvre
from flightdata import State, Flight
from fastapi import FastAPI, Body, HTTPException
import pandas as pd
import server.schemas as s
import os
from typing import Any, Annotated
from fastapi.middleware.cors import CORSMiddleware
import traceback
from loguru import logger


app = FastAPI()

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/run_short_manoeuvre")
def run_short_manouevre(
    id: Annotated[int, Body(description="The id of the manoeuvre, zero index")],
    direction: Annotated[int, Body()],
    sinfo: ScheduleInfo, 
    origin: s.FCJOrigin,
    data: list[s.FCJData], 
    optimise_alignment: Annotated[bool, Body()], 
    long_output: Annotated[bool, Body()],
    els: Annotated[list[s.El], Body()]=None,
) -> s.ShortOutput | s.LongOutout:
    try:
        
        st = State.from_flight(Flight.parse_fcj_data(
            origin.create(), 
            pd.DataFrame([d.__dict__ for d in data])
        ))
        
        if els is not None:
            df = pd.DataFrame([el.__dict__ for el in els])
            df.columns = ['name', 'start', 'stop']
            st = st.splitter_labels(df.to_dict('records'), target_col='element').label(manoeuvre=data['name'])

        man = ma.Basic(
            id, 
            SchedDef.load(sinfo.fcj_to_pfc())[id], 
            st, 
            direction
        ).proceed(optimise_alignment).run_all(optimise_alignment, False)

        return s.LongOutout.build(man) if long_output else s.ShortOutput.build(man)
    except Exception as ex:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(ex))


@app.post("/run_long_manoeuvre")
def run_long_manouevre(
    mdef: Annotated[dict[str, Any], Body()],
    direction: Annotated[int, Body()],
    id: Annotated[int, Body()],
    flown: list[s.State],
    manoeuvre: Annotated[dict[str, Any], Body()],
    template: list[s.State],
    optimise_alignment: Annotated[int, Body()]
) -> s.LongOutout:
    try:    
    
        man = ma.Alignment(
            id, 
            ManDef.from_dict(mdef), 
            State(pd.DataFrame([fl.__dict__ for fl in flown])), 
            direction, 
            Manoeuvre.from_dict(manoeuvre), 
            State(pd.DataFrame([tp.__dict__ for tp in template]))
        ).run_all(optimise_alignment)
        return s.LongOutout.build(man)
        
    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))

@app.get("/version")
def read_version() -> str:
    ver = os.getenv("PUBLIC_VERSION")
    if ver is None:
        ver = "next"
    return ver

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)