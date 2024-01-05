
import os
from trader import logger, local
import numpy as np
from trader.strategy import HistoricalStrategy
from trader.main import run_strategy

import pandas as pd

os.system(f'mkdir -p {local.domain_dir}')
index = pd.date_range(start='2014-01-01', end='2024-01-01', freq='30T')
close = np.random.choice([0, 1], size=len(index), p=[0.5, 0.5])
df = pd.DataFrame(data={'close': close}, index=index)
df.index.name = "trade_time"
df.to_csv(f'{local.domain_dir}{os.sep}parity.SZ.csv', index=True)

class MyStrategy(HistoricalStrategy):
    index_name="trade_time"
    strategy_columns=['close']
    def __init__(self):
        self.pace = 1

    @property
    def today_data(self):
        return self.SZparity.history[self.SZparity.history.index.date == self.data_flows.today]
    
    @property
    def yesterday_data(self):
        return self.SZparity.history[self.SZparity.history.index.date == self.data_flows.yesterday]
    

    def init_custom(self):
       self.SZparity.history['gaming'] = np.nan 


    def start(self):
        self.pace += 1
        if self.pace <= 60*24:
            return
        #1的概率
        x = 0.55
        if (self.yesterday_data.close.mean() > x) == True:
            if  self.SZparity.history.index[-1].date() == self.data_flows.today:
                self.SZparity.history.loc[self.SZparity.history.index[-1], 'gaming'] = 1 


        print(self.SZparity.history)

        # pdb.set_trace()
    def end(self):
        logger.info("historical strategy run end")
        logger.info(self.SZparity.history.dropna().close.mean())
        from matplotlib import pyplot as plt
        plt.plot(self.SZparity.history.gaming)
        plt.show()
if __name__ == "__main__":
    run_strategy(MyStrategy) 



