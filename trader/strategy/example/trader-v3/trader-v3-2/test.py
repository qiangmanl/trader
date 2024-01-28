
import os
import numpy as np
import pandas as pd
from trader.const import HOME_DIR, DATA_DIR
from trader import config,logger,local

df = pd.read_excel('pool.xlsx', dtype={'证券代码': str})
symbols = df["证券代码"]
"000002" in symbols.values


raw_data = f'{HOME_DIR}{os.sep}Downloads{os.sep}history'
if os.path.exists(local.domain_dir) == False: 
    os.makedirs(local.domain_dir,exist_ok=True)
if config.make_data:
    index = []
    config.remove("make_data",temporary=False)
    done_task = 0
    for filename in os.listdir(raw_data):
        symbol = filename.split('.')[0]
        if symbol not in symbols.values:
            continue
        try:
            df = pd.read_csv(f'{raw_data}/{filename}',index_col='trade_time',parse_dates=['trade_time'])
            # 提取最新的
            df = df.dropna()
            if (df.index[0] > df.index[1]) == True:
                #倒序
                  rvs = 1
            else:
                  rvs = 0
            uni_date = list(np.unique(df.index.date))
            #保证uni_date倒序
            uni_date.reverse()
            if rvs == 0:
                df = df[::-1]
            day = 0
            while day <= 500:  
                date = uni_date.pop(0)
                # 如果date 当天交易长度不等于48，df 直接删除掉
                if len(df[df.index.date == date].index) == 48:
                    day += 1
                else:
                    break
            #被倒序过再反转
            if rvs == 0:
                df = df[::-1]
            df = df[df.index.date > date]
            if len(df.index) == 500 * 48:
                if not len(index):
                    index = df.index
            df.set_index(index)
            df.to_csv(f'{local.domain_dir}{os.sep}{filename}')

        except:
            pass
        done_task += 1
        print(done_task)
    logger.info("process data done")
    exit()






# from functools import wraps

# def ta(name="ta", source=["close"]):
#     def decorator(func):   
#         def wrapper(self, **kw):
#             try: 
#                 print(name, source)
#                 return func(self, **kw) 
#             except Exception as e:
#                 return '', f'from {func.__name__}:{e.__repr__()}'
#         return wrapper 
#     return decorator


import talib
from trader.strategy import HistoricalStrategy
from trader.strategy import TechnicalAnalyses, analysis
from trader.main import run_strategy


class CustomTA(TechnicalAnalyses):
    @analysis(name="wmacst")
    def WMA(self, symbol,source="close", timeperiod=30):
        data = talib.EMA(getattr(self.symbols, symbol).history[source], timeperiod=timeperiod)
        return data.iloc[-1]

class MyStrategy(HistoricalStrategy):
    index_name="trade_time"
    ohlcv_columns=['open','high','low','close','vol']


    def __init__(self):
        pass

    def init_custom(self):
        self.create_ta(CustomTA)
        pass

    def start(self): 
        print(self.dataflows.point)   
        if self.ta.WMA("SZ300287",timeperiod=10) > self.ta.WMA("SZ300287",timeperiod=30):
            self.buy("SZ300287",1,islong=True)
        if self.ta.WMA("SZ300287",timeperiod=10) < self.ta.WMA("SZ300287",timeperiod=30):
            qty = self.symbols.SZ300287.position.long_qty
            if qty > 0:
                self.sell("SZ300287", qty,islong=True)
       
        self.ta.Kalman("SZ300287")

        self.buy("SZ300287",1,islong=True)
        print(self.symbols.SZ300287.history)
     
    def end(self):
        print(self.symbols.SZ300287.orderbook)
        from matplotlib import pyplot as plt
        plt.plot(self.symbols.SZ300287.orderbook.long_change)
        plt.show()
        plt.plot(self.symbols.SZ300287.orderbook.value)
        plt.show()
#         # pdb.set_trace()
#     def end(self):
#         pass
if __name__ == "__main__":
    run_strategy(MyStrategy) 



