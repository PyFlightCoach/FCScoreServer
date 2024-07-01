from pathlib import Path
from flightanalysis import ScheduleAnalysis
from loguru import logger
from fcscore.schemas.pfc import LongOutout

logger.enable('flightanalysis')
file = Path('~/projects/logs/2024_06_30/manual_F3A FAI_P25_24_06_30_00000169.json').expanduser()


sa = ScheduleAnalysis.from_fcj(file)
sa = sa.run_all()
logger.info(sa.scores())

sa.append_scores_to_fcj(file, '../FCScoreClient/static/example/example_p25.json')


for man in sa:
    with open(f'../FCScoreClient/static/example/{man.mdef.info.short_name}.json', 'w') as f:
        f.write(LongOutout.build(man, 'all').model_dump_json())