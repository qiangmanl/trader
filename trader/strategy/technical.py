import talib

from trader.utils.base import DictBase

def analysis(name="ta"):
    def decorator(func):   
        def wrapper(self, symbol, **kwargs):
            try:
                ta = func(self, symbol, **kwargs) 
                tag = '_'.join(map(str, kwargs.values()))
                getattr(self.histories, symbol)[f"{name}_{tag}"] = ta
                return ta.iloc[-1]
            except Exception as e:
                return '', f'from {func.__name__}:{e.__repr__()}'
        return wrapper 
    return decorator


class TechnicalAnalyses:

    @classmethod
    def create(cls, symbols):
        self = cls()
        self.histories = DictBase()
        for symbol in symbols:
            self.histories[symbol.name] = symbol.history
        return self

    @analysis(name="wma")
    def WMA(self, symbol, timeperiod=30):
        return talib.EMA(getattr(self.histories ,symbol)["close"], timeperiod=timeperiod)



