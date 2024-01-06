from collections import deque
from trader.utils.base import DictBase

asset = 1000000

class Account:
    total_asset = asset

    def __init__(self):
        pass

   
    def assign_balance(self, symbol, balance):
        self.total_asset -= balance


class HistoricalLongPosition(DictBase):
    """v0.0.3
    p = HistoricalPosition()
    p.open(21)
    p.update(22,increasing=1)
    p.update(24)
    p.update(24,reducing=1)
    p.profit

    """

    def __init__(self, balance, leverage, buying_fee, selling_fee , **kwargs):
        #
        self.set_balance(balance)
        self.leverage = leverage
        self.increasing_fee = buying_fee
        self.reducing_fee   = selling_fee
        self.value = self.symbol_balance
        self.is_openning = False
        self.profit = 0
        self.qty = 0
        
    def open(self, price):
        self.price = price
        self.latest_price = price
        self.equitys = deque(maxlen=2)
        self.equitys.append(self.get_equity())
        self.is_openning = True
        
    def settlement_long(self):
        if self.long_qty != 0:
            self.long_reducing(self.long_qty)
        self.symbol_balance = self.value
        self.long_profit = 0


    def set_balance(self, balance):
        self.symbol_balance = balance

    # def add_balance(self, balance):
    #     self.symbol_balance += balance

    # def reduce_balance(self, balance):
    #     assert  balance < self.value
    #     self.symbol_balance -= balance


    
    @property
    def profit_rate(self):
        # 利润比率
        rate = (self.symbol_balance + self.profit) / (self.symbol_balance + 0.00000000000000001)
        return  rate

    @property
    def is_positive(self):
        # 判断持仓利好
        return self.value > self.symbol_balance

    def increasing(self, qty):
        self.qty += qty
        self.symbol_balance -= self.increasing_fee * self.leverage * self.latest_price

    def reducing(self, qty):
        assert self.qty >= qty, f'reducing qty must be more than {self.qty}'
        self.qty -= qty 
        self.symbol_balance -= self.increasing_fee * self.leverage * self.latest_price
    
    def isin_margin_call(self):
        return self.profit + self.symbol_balance < 0
    
    def decide_margin_call(self):
        if self. isin_margin_call():
            self.profit = 0
            self.qty = 0
            self.symbol_balance = 0
 
    def get_equity(self):
        # 一单的价差
        price_change = (self.latest_price - self.price) / (self.price + 0.00000000000000000001)
        equity = self.price  +  self.price * price_change * self.leverage * self.direction
        return equity
    
    def set_latest_price(self,price):
        self.latest_price = price

    def set_trade_time(self, trade_time):
        self.trade_time = trade_time

    def update_position(self, price, trade_time, qty=None, action=None):
        if trade_time == self.trade_time:
            return 
        
        self.set_trade_time(trade_time)
        if self.is_openning:
            self.set_latest_price(price)
            self.equitys.append(self.get_equity())
            self.profit += (self.equitys[1] - self.equitys[0]) * self.qty 
            self.decide_margin_call()
            self.value = self.symbol_balance + self.profit 
            match (action, self.direction):
                case ("sell",-1):
                    self.increasing(qty)
                case ("buy",1): 
                    self.increasing(qty)
                case ("sell",1): 
                    self.reducing(qty)
                case ("buy",-1): 
                    self.reducing(qty)
                # cast "sell":
        else:
            import pdb
            pdb.set_trace()


class TradingPosition(DictBase):
    pass

class HistoricalPositionMap(DictBase):
    def __init__(self,symbol_objects, **order_config):

        default_order_config = order_config["default"]
        for symbol in symbol_objects:
            # if orderconfig.get(symbol):
            symbol_order_config = order_config.setdefault(symbol, default_order_config)
            symbol_order_config.setdefault("buying_fee",default_order_config["buying_fee"])
            symbol_order_config.setdefault("selling_fee",default_order_config["selling_fee"])
            symbol_order_config.setdefault("balance",default_order_config["balance"])
            symbol_order_config.setdefault("leverage",default_order_config["leverage"])
            self.add_position(symbol ,HistoricalPosition(**symbol_order_config))

    def add_position(self, symbol, position:HistoricalPosition):
        self.__setattr__(symbol, position)
