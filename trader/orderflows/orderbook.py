import pandas as pd
from trader.utils.base import SymbolsPropertyDict

class HistoricalOrderBook:
    """
        price action
    """
    def __init__(self, symbol_objects):
        self.default_columns_data = {"price":[0], "qty":[0], "balance":[0]}
        self.symbol_objects = symbol_objects

        
        #初始化订单 
    def build_order_flows(self, current_time)->list:
        df_l = []
        columns = list(self.default_columns_data.keys())
        for _ in range(len(self.symbol_objects)):
            df = pd.DataFrame(self.default_columns_data, columns=columns).set_index(pd.Index([current_time]))
            df_l.append(df)
        self.order_flows = pd.concat(df_l, axis=1, keys=self.symbol_objects)
         





