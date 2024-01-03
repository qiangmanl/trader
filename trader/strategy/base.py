
import pandas as pd

from trader.utils.base import SymbolsPropertyDict

class StrategyBase:
    model = ""
    histories = None


    def start(self):
        raise NotImplementedError("not start implemented")


    def end(self):
        raise NotImplementedError("not end implemented")
    
    @property 
    def current_datetime(self):
        # 当前策略执行到的日期在window最后
        return self.data_flows.current_datetime_index

    @property
    def next_period_index(self):
        return self.data_flows.next_period_index

    @property
    def previous_datetime(self):
       return self.data_flows.previous_datetime_index

    @property
    def today(self):
        return self.current_datetime.date()
    
    @property
    def yesterday(self):
        return self.today - pd.Timedelta(days=1)


    @property
    def current_time(self):
        return self.current_datetime.time()
    
    
    def get_previous_history(self, symbol:str) -> pd.core.series.Series:
        data = getattr(self,symbol).history.loc[self.previous_datetime]
        return data
    
    def get_current_history(self, symbol:str) -> pd.core.series.Series:
        data = getattr(self,symbol).history.loc[self.current_datetime]
        return data
    

class SymbolsPropertyBase:
    """
        call strategy.{symbol}.{attribute} to get strategy.{attribute}.{symbol} attribute.
    """
   
    def init_symbol_property(self, strategy_columns):
        # self.property_dict = SymbolsPropertyDict()
        for symbol in self.symbols_property:
            if getattr(self, symbol, None) == None:
                self._set_symbol_object(symbol)
                self._set_symbol_property(symbol,strategy_columns)
                self._update_symbol_history(symbol)
                self._open_symbol_position(symbol)

    def update_symbol_property(self):
        for symbol in self.symbols_property:
            #更新每个symbol 的history
            #更新每个symbol的history必须在更新symbol报价之前执行
            self._update_symbol_history(symbol)
            self._update_symbol_quota(symbol)

    def _set_symbol_object(self, symbol) -> None:
        #为了让strategy可以直接通过symbol获得symbol相关属性
        setattr(self, symbol, type("SymbolObject", (), {})())

    def _set_symbol_property(self, symbol, strategy_columns) -> None:
        #symbol的属性
        setattr(getattr(self, symbol),'history' , pd.DataFrame(columns=strategy_columns))
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

# self.SZ000676.history

# self.set_latest_price("SZ000676",12.1)

# id(self.SZ000676.history)
# id(self.history.SZ000676)

# id(self.SZ000676.price)
# id(self.orderbook.price_reference.SZ000676)


















