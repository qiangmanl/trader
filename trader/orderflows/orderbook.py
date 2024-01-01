import pandas as pd
from trader.utils.base import SymbolsPropertyDict

class HistoricalOrderBook:
    """
        price action
    """
    def __init__(self, symbols_property):
        self.default_columns_data = {"price":[0], "qty":[0], "balance":[0]}
        self.symbols_property = symbols_property
        self.orders = SymbolsPropertyDict()
 
        for symbol in self.symbols_property:
            self.orders.__setattr__(symbol, SymbolsPropertyDict())
        
        #初始化订单 
    def build_order_flows(self, current_time)->list:
        df_l = []
        columns = list(self.default_columns_data.keys())
        for _ in range(len(self.symbols_property)):
            df = pd.DataFrame(self.default_columns_data, columns=columns).set_index(pd.Index([current_time]))
            df_l.append(df)
        order_flows = pd.concat(df_l, axis=1, keys=self.symbols_property)
        self.order_flows = order_flows

    def get_symbol_price(self,symbol):
        return self.orders[symbol]["price"]

    def set_latest_price(self ,symbol, price):
        self.orders.__getattr__(symbol).update({"price":price})

