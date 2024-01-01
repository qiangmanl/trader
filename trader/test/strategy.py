import pandas as pd
from trader.const import SEP
class StrategyBase:
    model = ""
    history = None

    @property 
    def current_datetime(self):
        # 当前策略执行到的日期在window最后
        return self.history.index[-1]

    @property
    def previous_datetime(self):
       return self.history.index[-2] 

    @property
    def today(self):
        return self.current_datetime.date()

    @property
    def current_time(self):
        return self.current_datetime.time()

    @property
    def datetime_period(self):
        return self.current_datetime - self.history.index[-2]
    
    @property
    def next_period(self):
        return self.current_datetime + self.datetime_period
    
    def get_previous_history(self, symbol:str) -> pd.core.series.Series:
        data = self.history[f'{symbol}'].loc[self.previous_datetime]
        return data
    
    def get_current_history(self, symbol:str) -> pd.core.series.Series:
        data = self.history[f'{symbol}'].loc[self.current_time]
        return data
    



    

class Position:
    def __init__(self):
        self.a = {}
        self.b = {}
        self.c = {}
# from trader.utils.tools import gen_random_id


class A(DictBase,StrategyBase):
    def __init__(self):
        self.p = Position()


class B(A):
    pass

b = B()
b.set_symbols()


