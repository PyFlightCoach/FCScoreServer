from pathlib import Path
import pandas as pd
from dataclasses import dataclass


def all_logs():
    return sorted(list(Path('logs').glob('*.log')))

def last_log():
    return all_logs()[-1]

cols = dict(
    request=['time', 'name', 'id', 'method', 'function', 'length'],
    response=['time', 'name', 'id', 'elapsed', 'length'],
    convert_fcj=['time', 'name', 'id', 'schedule', 'lat', 'long', 'alt'],
    good_analysis=['time', 'name', 'id', 'manoeuvre', 'score'],
    failed_analysis=['time', 'name', 'id', 'stage']
)


@dataclass
class TLog:
    data: dict[str, pd.DataFrame]

    @staticmethod
    def from_file(file: Path | str):
        with open(file, 'r') as f:
            data = f.readlines()
        data = [[l[:24]] + l[54:].strip().split(',') for l in data]
        groups = {}
        for line in data:
            if line[1] not in groups:
                groups[line[1]] = []
            groups[line[1]].append(line)
        return TLog({k: pd.DataFrame(v, columns=cols[k]) for k, v in groups.items()})
    
    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]
        raise AttributeError(f'{name} not available')
    
    
if __name__ == "__main__":
    tlog = TLog.from_file(last_log())
    pass