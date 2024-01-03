


from trader import logger
import numpy as np
from trader.strategy import HistoricalStrategy
from trader.main import run_strategy

import pandas as pd
import numpy as np

index = pd.date_range(start='2014-01-01', end='2024-01-01', freq='30T')
close = np.random.choice([0, 1], size=len(index), p=[0.5, 0.5])
df = pd.DataFrame(data={'close': close}, index=index)
df.index.name = "datetime"
df.to_csv('~/.trader/row/parity2.SZ.csv', index=True)


class MyStrategy(HistoricalStrategy):
    index_name="datetime"
    strategy_columns=['close']
    def __init__(self):
        self.pace = 1

    @property
    def today_data(self):
        return self.SZparity2.history[self.SZparity2.history.index.date == self.today]
    
    @property
    def yesterday_data(self):
        return self.SZparity2.history[self.SZparity2.history.index.date == self.yesterday]
    

    def init_custom(self):
       self.SZparity2.history['gaming'] = np.nan 


    def start(self):
        self.pace += 1
        if self.pace <= 60*24:
            return
        #1的概率
        x = 0.55
        if (self.yesterday_data.close.mean() > x) == True:
            if  self.SZparity2.history.index[-1].date() == self.today:
                self.SZparity2.history.loc[self.SZparity2.history.index[-1], 'gaming'] = 1 


        print(self.SZparity2.history)

        # pdb.set_trace()
    def end(self):
        logger.info("historical strategy run end")
        logger.info(self.SZparity2.history.dropna().close.mean())
        from matplotlib import pyplot as plt
        plt.plot(self.SZparity2.history.gaming)
        plt.show()
if __name__ == "__main__":
    run_strategy(MyStrategy) 



