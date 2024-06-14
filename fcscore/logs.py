from pathlib import Path

from loguru import logger
import sys
from flightanalysis import ma
from fcscore.schemas import TLog
from time import time

error_log = Path('logs/errors.log')
if not error_log.exists():
    error_log.touch()



logger.remove()
logger.add(open(error_log, 'a'), level='INFO')
logger.add(sys.stderr, level='INFO')

logger.info('Starting API')

run_log = Path('logs/run_history.log')
if not run_log.exists():
    run_log.touch()
    with open(run_log, 'a') as f:
        print(*TLog.model_fields.keys(),sep=',',file=f)


def log_run(start_time: float, optimised: bool, man: ma.Scored):
    tlog = TLog(
        time=time(),
        name=man.mdef.info.short_name,
        score=man.scores.score(),
        duration = time() - start_time,
        optimised=optimised
    )
    with open(run_log, 'a') as f:
        print(*tlog.__dict__.values(),sep=',',file=f)
