
import pandas as pd
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
                self._update_symbol_history(symbol)
                self._open_symbol_position(symbol)

    def update_symbol_object(self):
        for symbol in self.symbol_objects:
            #更新每个symbol 的history
            #更新每个symbol的history必须在更新symbol报价之前执行
            self._update_symbol_history(symbol)
            self._update_symbol_quota(symbol)

    def _set_symbol_object(self, symbol) -> None:
        #为了让strategy可以直接通过symbol获得symbol相关属性
        setattr(self, symbol, type("SymbolObject", (), {})())

    def _set_symbol_property(self, symbol ) -> None:
        #symbol的属性
        setattr(getattr(self, symbol),'history' , pd.DataFrame(columns=self.strategy_columns))
        setattr(getattr(self, symbol),'position' ,getattr(self.positions, symbol))
        setattr(getattr(self, symbol),'property_dict' , SymbolsPropertyDict())

    def _get_quotation(self, symbol:str):
        match self.price_reference:
            case "current_period_close":
                price = self.get_previous_history(symbol)["close"]
            case "next_period_open":
                price = self.get_current_history(symbol)["open"]
        return price

    def _update_symbol_history(self, symbol):
        getattr(self,symbol).history.loc[self.data_flows.period.name] = \
            getattr(self.data_flows.period, symbol)
    #

    def _update_symbol_quota(self, symbol):
            price = self._get_quotation(symbol)
            getattr(self,symbol).property_dict["quota"] = price

    def _open_symbol_position(self, symbol):
        price = self.get_current_history(symbol)["close"]
        getattr(self, symbol).position.openning(price)



















