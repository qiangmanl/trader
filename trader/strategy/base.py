
import pandas as pd
from trader.assets import OrderBookPattern
from trader.assets import HistoricalPosition, TradingPosition

class WindowPointCtrol:
    def __init__(self,point_window):
        self.point = 0
        self.keep_point_window=point_window
        self.cycle = 0

    @property
    def pace(self):
        self.point += 1
        if self.point == self.keep_point_window:
            self.repoint()
        return self.point
    
    def repoint(self):
        self.point = 0
        self.cycle += 1

    def cyclepoint(self):
        return (self.cycle,self.point)

class SymbolsProperty:
    """
        call strategy.{symbol}.{attribute} to get strategy.{attribute}.{symbol} attribute.
    """
   
    def init_symbol_objects(self):
        # self.property_dict = SymbolsPropertyDict()

        for symbol in self.symbol_names:
            ohlcv = self.dataflows.pre_data.pop(symbol).copy()
            symbol_obj = self.symbols.get_symbol(symbol)
            symbol_obj.history = ohlcv
            symbol_obj.position = getattr(self.positions, symbol)
            price = ohlcv.iloc[-1].close
            position = self.get_symbol_position(symbol)
            position.open(price)

    def _update_symbol_position(self, symbol):
        #self.dataflows.pre_data.pop(symbol).copy() in _set_symbol_property mean pre_data pop to history

        position = self.get_symbol_position(symbol)
        orderbook = self.get_symbol_orderbook(symbol)
        orderbook.loc[self.dataflows.current_datetime] = \
        OrderBookPattern.create(position).orderbook
        # logger.debug(f'{orderbook}')
        # logger.debug(f'{position}')

    def update_symbol_object(self):
        for symbol in self.symbol_names:
            #get_symbol_period 更快
            period = self.get_symbol_period(symbol)
            symbol_obj = getattr(self.symbols,symbol)
            #更新每个symbol 的history
            #更新每个symbol的history必须在更新symbol报价之前执行
            symbol_obj.history.loc[self.dataflows.current_datetime] = period
            if self.column_only_close:
                df = self.get_symbol_history(symbol)
                close = df.loc[self.dataflows.current_datetime].close
                df.open = close
                df.high = close
                df.low  = close
            symbol_obj.property_dict["ohlcv"] = period
            symbol_obj.property_dict["ohlc"] = period[:-1]   
            symbol_obj.orderbook.loc[self.dataflows.current_datetime] = \
                OrderBookPattern.create(symbol_obj.position).orderbook

            # self._update_symbol_position(symbol)
        # import pdb
        # pdb.set_trace()
        

class StrategyBase(SymbolsProperty):
    model = ""
    def start(self):
        raise NotImplementedError("not start implemented")

    def end(self):
        raise NotImplementedError("not end implemented")
    
    def init_strategy(self):
        raise NotImplementedError("not init_strategy implemented") 
    
    def get_previous_history(self, symbol:str) -> pd.core.series.Series:
        if (self.dataflows.previous_datetime):
            data = getattr(self.symbols,symbol).history.loc[self.dataflows.previous_datetime]
            return data
        return None
    
    def get_current_history(self, symbol:str) -> pd.core.series.Series:
        data = getattr(self.symbols,symbol).history.loc[self.dataflows.current_datetime]
        return data
    
    def get_symbol_period(self, symbol:str) -> pd.core.series.Series:
        return getattr(self.dataflows.period, symbol)
    
    def get_symbol_history(self, symbol:str) -> pd.core.frame.DataFrame:
        return getattr(self.symbols,symbol).history
    
    def get_symbol_position(self, symbol:str) -> HistoricalPosition | TradingPosition:
        return getattr(self.symbols, symbol).position

    def get_symbol_orderbook(self, symbol:str) -> pd.core.frame.DataFrame:
        return getattr(self.symbols, symbol).orderbook
















