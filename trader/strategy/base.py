import asyncio
import pandas as pd
from trader.utils.base import SymbolsPropertyDict

class StrategyBase:
    model = ""
    histories = None

    @property 
    def current_datetime(self):
        # 当前策略执行到的日期在window最后
        return self.histories.index[-1]

    @property
    def previous_datetime(self):
       return self.histories.index[-2] 

    @property
    def today(self):
        return self.current_datetime.date()

    @property
    def current_time(self):
        return self.current_datetime.time()

    @property
    def datetime_period(self):
        return self.current_datetime - self.histories.index[-2]
    
    @property
    def next_period(self):
        #时间序列下一个理论的周期时间单位
        return self.current_datetime + self.datetime_period
    
    @property
    def next_flows_period(self):
        raise NotImplementedError(" Not implemented next_flows_period")

    def get_previous_history(self, symbol:str) -> pd.core.series.Series:
        data = self.histories[f'{symbol}'].loc[self.previous_datetime]
        return data
    
    def get_current_history(self, symbol:str) -> pd.core.series.Series:
        data = self.histories[f'{symbol}'].loc[self.current_time]
        return data
    

class SymbolsPropertyBase:
    """
        call strategy.{symbol}.{attribute} to get strategy.{attribute}.{symbol} attribute.
    """
        
    def init_symbol_property(self, strategy_columns):
        self.current_window = SymbolsPropertyDict()
        for symbol in self.symbols_property:
            if getattr(self, symbol, None) == None:
                setattr(self, symbol, type("SymbolsProperty", (), {})())
                setattr(getattr(self, symbol),'order' , getattr(self.orderbook.orders ,symbol))
                setattr(getattr(self, symbol),'position' ,getattr(self.positions, symbol))
                setattr(getattr(self, symbol),'history' , pd.DataFrame(columns=strategy_columns))
                # setattr(getattr(self, symbol),'reference_price' ,getattr(self.orderbook.reference_price ,symbol))
                # setattr(getattr(self, symbol),'history' ,getattr(self.current_window ,symbol))


    def set_history(self):
        self.current_window.__setattr__("data",  self.data_flows.current_window)
        for symbol in self.symbols_property:
            getattr(self,symbol).history.loc[self.current_window["data"].name] = \
                getattr(self.data_flows.current_window,symbol)


# self.SZ000676.history

# self.set_latest_price("SZ000676",12.1)

# id(self.SZ000676.history)
# id(self.history.SZ000676)

# id(self.SZ000676.price)
# id(self.orderbook.reference_price.SZ000676)


















