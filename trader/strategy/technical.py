import math
import pandas as pd
import numpy as np
from typing import Union
import talib


# getattr(self.histories, symbol).loc[getattr(self.histories, symbol).index[-1],f"{name}_{tag}"] = 1
def is_decimal(num:Union[int, float, np.number, pd.core.series.Series]):
    return  bool(isinstance(num, Union[int, float, np.number]))

def is_series(series:Union[int, float, np.number, pd.core.series.Series]):
    return  bool(isinstance(series, pd.core.series.Series))

def analysis(name="ta"):
    def decorator(func):   
        def wrapper(self, symbol, **kwargs):
            # import pdb
            # pdb.set_trace()
            try:
                ta_value = func(self, symbol, **kwargs) 
                tag = '_'.join(map(str, kwargs.values()))
                history = getattr(self.symbols, symbol).history
                tag_name = f"{name}_{tag}" if tag else f"{name}"
                if is_decimal(ta_value):
                    history = getattr(self.symbols, symbol).history
                    history.loc \
                        [history.index[-1], tag_name] = ta_value
                elif is_series(ta_value):
                    history[tag_name] = ta_value
                return ta_value
            except Exception as e:
                return '', f'from {func.__name__}:{e.__repr__()}'
        return wrapper 
    return decorator


from .symbols import DomainSymbols

class TechnicalAnalyses:

    @classmethod
    def create(cls, symbols:DomainSymbols):
        self = cls()
        self.symbols = symbols
        return self

    def get_daily_data(self, symbol:str):
        history = getattr(self.symbols, symbol).history
        daily_data=history.resample('1D').agg \
            ({'open':'first','high':'max','low':'min','close':'last','vol':'sum'}).dropna()
        return daily_data

    @analysis(name="ema_daily")
    def EMAD(self, symbol, source="close", timeperiod=30) ->  Union[int, float, np.number, pd.core.series.Series]:
        data = self.get_daily_data(symbol)
        data = talib.EMA(data[source], timeperiod=timeperiod)
        return data
    
    @analysis(name="ema")
    def EMA(self, symbol, source="close", timeperiod=30) ->  Union[int, float, np.number, pd.core.series.Series]:
        data = talib.EMA(getattr(self.symbols, symbol).history[source], timeperiod=timeperiod)
        return data.iloc[-1]

    @analysis(name="ma")
    def MA(self, symbol, source="close", timeperiod=30) ->  Union[int, float, np.number, pd.core.series.Series]:
        data = talib.MA(getattr(self.symbols, symbol).history[source], timeperiod=timeperiod)
        return data.iloc[-1]

    @analysis(name="wma")
    def WMA(self, symbol, source="close", timeperiod=30) ->  Union[int, float, np.number, pd.core.series.Series]:
        data = talib.WMA(getattr(self.symbols, symbol).history[source], timeperiod=timeperiod)
        return data.iloc[-1]
    
    @analysis(name="kalman")
    def Kalman(self, symbol:str, source:str="close") ->  Union[int, float, np.number]:
        value = getattr(self.symbols, symbol).history[source]
        return kp.predict(symbol, value.iloc[-1])

class KalmanPool:
    def create_filter(self, symbol:str)->None:
        if getattr(self, symbol, None) == None:
            setattr(self, symbol, KalmanFilter())

    def predict(self, symbol:str, value:Union[int, float, np.number, pd.core.series.Series]):
        if getattr(self, symbol, None) == None:
            self.create_filter(symbol)
        return  getattr(self, symbol).predict(value) 

class KalmanFilter:
    def __init__(self)->None:
        self.x = 0
        self._pred_val = 0
        self.pred_cov = 0.1
        self.real_cov = 0.1
        self.kg = 0.0
        self.predict(0)
    def predict(self,val:int):
        self._pred_val = self._pred_val + self.kg * (val - self._pred_val)
        result = (math.pow(self.pred_cov, 2) + math.pow(self.real_cov, 2)) or 0.0000000001
        self.kg = math.sqrt(math.pow(self.pred_cov, 2) / result)
        self.pred_cov = math.sqrt(1.0 - self.kg) * self.pred_cov
        self.real_cov = math.sqrt(1.0 - self.kg) * self.real_cov
        return self._pred_val
    
    @property
    def pred_val(self):
        return self.pred_val

kp=KalmanPool()