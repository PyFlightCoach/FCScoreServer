from json import load, dump
from flightdata import NumpyEncoder
from flightanalysis import ScheduleAnalysis
from loguru import logger
import sys

logger.enable('flightanalysis')
logger.remove()
logger.add(sys.stderr, level='INFO')

sa = ScheduleAnalysis.from_fcj(load(open(
    '../../data/manual_F3A_P23_22_05_31_00000350.json', 
    'r'
))).run_all()

for man in sa:
    dump(
        man.to_dict(), 
        open(f"../FCScoreClient/static/examples/{man.name}.json", 'w'), 
        cls=NumpyEncoder
    )