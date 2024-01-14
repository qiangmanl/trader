
import pandas as pd
from trader.assets import OrderBookPattern
from trader.assets import HistoricalPosition, TradingPosition
from trader.utils.base import SymbolsPropertyDict
from trader import logger
class WindowCtrol:
    def __init__(self,point_window):
        self.point = 1
        self.keep_point_window=point_window

    @property
    def pace(self):
        self.point += 1
        if self.point == self.keep_point_window:
            self.repoint()
        return self.point
    
    def repoint(self):
        self.point = 0

class StrategyBase:
    model = ""
    histories = None
    def start(self):
        raise NotImplementedError("not start implemented")

    def end(self):
        raise NotImplementedError("not end implemented")
    
    def init_strategy(self):
        raise NotImplementedError("not init_strategy implemented") 
    
    def get_previous_history(self, symbol:str) -> pd.core.series.Series:
        data = getattr(self,symbol).history.loc[self.data_flows.previous_datetime]
        return data
    
    def get_current_history(self, symbol:str) -> pd.core.series.Series:
        data = getattr(self,symbol).history.loc[self.data_flows.current_datetime]
        return data
    
    def get_symbol_period(self, symbol:str) -> pd.core.series.Series:
        return getattr(self.data_flows.period, symbol)
    
    def get_symbol_history(self, symbol:str) -> pd.core.frame.DataFrame:
        return getattr(self,symbol).history
    
    def get_symbol_position(self, symbol:str) -> HistoricalPosition | TradingPosition:
        return getattr(self, symbol).position

    def get_symbol_orderbook(self, symbol:str) -> pd.core.frame.DataFrame:
        return getattr(self, symbol).orderbook

class SymbolsProperty:
    """
        call strategy.{symbol}.{attribute} to get strategy.{attribute}.{symbol} attribute.
    """
   
    def init_symbol_objects(self):
        # self.property_dict = SymbolsPropertyDict()
        for symbol in self.symbol_objects:
            if getattr(self, symbol, None) == None:
                self._set_symbol_object(symbol)
                self._set_symbol_property(symbol)
                # self._update_symbol_history(symbol)
                self._set_symbol_account(symbol)
        
    def _set_symbol_object(self, symbol) -> None:
        #让strategy获得symbol相关属性
        setattr(self, symbol, type("SymbolObject", (), {})())

    def _set_symbol_property(self, symbol ) -> None:
        #symbol的属性

        setattr(getattr(self, symbol),'history' , self.data_flows.pre_data.pop(symbol).copy())
        setattr(getattr(self, symbol),'position' ,getattr(self.positions, symbol))
        setattr(getattr(self, symbol),'property_dict' , SymbolsPropertyDict())
        setattr(getattr(self, symbol),'orderbook' , pd.DataFrame(columns=OrderBookPattern.keys))


    def _set_symbol_account(self, symbol):
        position = self.get_symbol_position(symbol)
        price = self.get_current_history(symbol)["close"]
        position.open(price)
        orderbook = self.get_symbol_orderbook(symbol)
        orderbook.loc[self.data_flows.current_datetime] = \
        OrderBookPattern.create(position).orderbook
        logger.debug(f'{orderbook}')
        logger.debug(f'{position}')
    def _update_symbol_history(self, symbol):

        # self.get_symbol_history(symbol).loc[self.data_flows.current_datetime] = \
        #     self.get_symbol_period(symbol)
        
        self.get_symbol_history(symbol).loc[self.data_flows.current_datetime] = self.get_symbol_period(symbol)
        if self.column_only_close:
            df = self.get_symbol_history(symbol)
            close = df.loc[self.data_flows.current_datetime].close
            df.open = close
            df.high = close
            df.low = close
  
    def _update_symbol_quota(self, symbol):
            ohlcv = self.get_current_history(symbol)
            getattr(self,symbol).property_dict["ohlcv"] = ohlcv
            getattr(self,symbol).property_dict["ohlc"] = ohlcv[:-1]

    def update_symbol_object(self):
        for symbol in self.symbol_objects:
            #更新每个symbol 的history
            #更新每个symbol的history必须在更新symbol报价之前执行
            self._update_symbol_history(symbol)
            self._update_symbol_quota(symbol)
        


















