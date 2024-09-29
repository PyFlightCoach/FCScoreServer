from pathlib import Path
from flightanalysis import ScheduleAnalysis, ScheduleInfo, SchedDef
from flightdata import Flight, BinData, State, Origin

from loguru import logger
from fcscore.schemas import LongOutout
from json import load, dump


logger.enable("flightanalysis")
bd=BinData.parse_json(
        load(open("../FCScoreClient/static/example/example_bin_data.json", "r"))
    )
fl = Flight.from_log(bd)
fcj_path = Path("../FCScoreClient/static/example/example_fcjson.json")
fcj = load(fcj_path.open("r"))
sinfo = ScheduleInfo(*fcj["parameters"]["schedule"]).fcj_to_pfc()

st = State.from_flight(fl, Origin.from_fcjson_parameters(fcj["parameters"]))
dump(st.to_dict(), open("../FCScoreClient/static/example/example_state.json", "w"))

sa = ScheduleAnalysis.from_fcj(fcj,  fl, True)

sa = sa.run_all()
logger.info(sa.scores())

sa.append_scores_to_fcj(fcj, fcj_path)

for man in sa:
    print(man.mdef.info.short_name)
    with open(
        f"../FCScoreClient/static/example/{man.mdef.info.short_name}.json", "w"
    ) as f:
        f.write(LongOutout.build(man, "all").model_dump_json())
