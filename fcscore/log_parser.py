from pathlib import Path
import pandas as pd
from dataclasses import dataclass
from .schemas import TLog
import numpy as np


cols = "result,schedule,manoeuvre,score,time,optimised".split(',')


def parse_tlog(file: str):
    with open(file, 'r') as f:
        data = f.readlines()
    

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
        dfs = {}
        for k, v in groups.items():
            dfs[k] = pd.DataFrame(v, columns=cols[k])
            dfs[k]['time'] = pd.to_datetime(dfs[k]['time'])
            dfs[k] = dfs[k].set_index('time')
        return TLog(dfs)
    
    def __getattr__(self, name):
        if name in self.data:
            return self.data[name]
        raise AttributeError(f'{name} not available')
    
    def count_concurrent(self):
        dfon = pd.DataFrame(index=self.response.index - pd.to_timedelta(self.response.elapsed.astype(float), unit="s" ), data=np.ones(len(self.response)))
        dfoff = pd.DataFrame(index=self.response.index, data=-np.ones(len(self.response)))
        return pd.concat([dfon,dfoff]).sort_index().cumsum().iloc[:,0].reset_index().set_axis(['time', 'processes'], axis=1).set_index('time')

    def data_in_out(self, name: str):
        df = pd.DataFrame(self.data[name].length.astype(int) / 1000)
        df = df.assign(total=df.length.cumsum())
        if name == 'response':
            df = df.assign(function=pd.merge(self.response, self.request, on='id').function.to_numpy())
        elif name == 'request':
            df = df.assign(function=self.data[name].function)
        else:
            raise ValueError(f'Invalid name: {name}')
        return df
    
    def data_in(self):
        return self.data_in_out('request')
    
    def data_out(self):
        return self.data_in_out('response')


if __name__ == "__main__":
    tlog = TLog.from_file("logs/telem.log")
    print(tlog.count_concurrent())
    print(tlog.data_in())
    print(tlog.data_out())
    pass