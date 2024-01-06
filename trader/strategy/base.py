
import pandas as pd
from trader.orderflows import OrderBookPattern
from trader.positions import HistoricalPosition, TradingPosition
from trader.utils.base import SymbolsPropertyDict


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
                self._set_symbol_history(symbol)
                self._set_symbol_account(symbol)

    def update_symbol_object(self):
        for symbol in self.symbol_objects:
            #更新每个symbol 的history
            #更新每个symbol的history必须在更新symbol报价之前执行
            self._set_symbol_history(symbol)
            self._set_symbol_quota(symbol)
        
    def _set_symbol_object(self, symbol) -> None:
        #为了让strategy可以直接通过symbol获得symbol相关属性
        setattr(self, symbol, type("SymbolObject", (), {})())

    def _set_symbol_property(self, symbol ) -> None:
        #symbol的属性
        setattr(getattr(self, symbol),'history' , pd.DataFrame(columns=self.strategy_columns))
        setattr(getattr(self, symbol),'position' ,getattr(self.positions, symbol))
        setattr(getattr(self, symbol),'property_dict' , SymbolsPropertyDict())
        setattr(getattr(self, symbol),'orderbook' , pd.DataFrame(columns=OrderBookPattern.keys))

    def _get_quotation(self, symbol:str):
        match self.price_reference:
            case "current_period_close":
                price = self.get_previous_history(symbol)["close"]
            case "next_period_open":
                price = self.get_current_history(symbol)["open"]
        return price

    def _set_symbol_history(self, symbol):
        self.get_symbol_history(symbol).loc[self.data_flows.current_period_index] = \
            self.get_symbol_period(symbol)
    #
    def _set_symbol_quota(self, symbol):
            price = self._get_quotation(symbol)
            getattr(self,symbol).property_dict["quota"] = price

    def _set_symbol_account(self, symbol):
        position = self.get_symbol_position(symbol)
        price = self.get_current_history(symbol)["close"]
        position.open(price)
        orderbook = self.get_symbol_orderbook(symbol)
        orderbook.loc[self.data_flows.current_period_index] = \
        OrderBookPattern.create(position).orderbook



















