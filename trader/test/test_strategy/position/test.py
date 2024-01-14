
import os
import numpy as np
import pandas as pd
from trader.const import HOME_DIR, DATA_DIR
from trader import config,logger,local



df = pd.read_csv("symbol1.test.csv",index_col="datetime")
df.to_csv(f'{local.domain_dir}{os.sep}{"symbol1.test.csv"}',index=True)


from trader.strategy import HistoricalStrategy
from trader.main import run_strategy

class MyStrategy(HistoricalStrategy):
    index_name="datetime"
    ohlcv_columns=["close"]

    def __init__(self):
        pass

    def init_custom(self):
       pass

    def start(self):
        print(self.testsymbol1.history)
        self.buy("testsymbol1",1,islong=True)


    def end(self):
        print(self.testsymbol1.orderbook)
        import pdb
        pdb.set_trace()
        pass

#         # pdb.set_trace()
#     def end(self):
#         pass
if __name__ == "__main__":
    run_strategy(MyStrategy) 


