import numpy as np
from trader import logger
from trader.utils.base import DictBase
from trader.assets import Order
class HistoricalPosition(DictBase):
    """v0.0.3
    symbol = "sz000002"
    p = HistoricalPosition(symbol,20000,2,0,0)
    p.open(21)
    o = Order( symbol, action="sell", qty=1, price=21,islong=False, order_type="")
    o.finish_historical_order()
    p.update_order(o)

    p.update_position(24,"23-1-1")
    p.update_position(25,"23-1-1")
    p.update_position(25,"23-1-2")
    p.update_position(21,"23-1-3")
    p.update_position(22,"23-1-4")
    o = Order( symbol, action="buy", qty=1, price=22,direction=1, order_type="")
    p.update_position(23,"23-1-5")
    o = Order( symbol, action="sell", qty=2, price=22,direction=1, order_type="")
    p.update_order(o)
    p.update_position(24,"23-1-6")

    """
    

    # def __init__(self, symbol, balance, leverage, long_fee, short_fee):
    #     self.symbol = symbol
    #     self.symbol_balance = 0
    #     self.leverage = leverage
    #     self.set_balance(balance)
    #     self.long_fee = long_fee
    #     self.short_fee   = short_fee
    #     self.value = self.symbol_balance
    #     self.is_openning = False
    #     self.long_profit = 0
    #     self.short_profit = 0
    #     self.long_qty = 0
    #     self.short_qty = 0
    #     self.short_lost_change = np.nan
    #     self.long_lost_change = np.nan

    @classmethod
    def init(cls, symbol, balance, leverage, long_fee, short_fee):
        self = cls()
        self.symbol = symbol
        self.symbol_balance = 0
        self.leverage = leverage
        self.set_balance(balance)
        self.long_fee = long_fee
        self.short_fee   = short_fee
        self.value = self.symbol_balance
        self.is_openning = False
        self.long_profit = 0
        self.short_profit = 0
        self.long_qty = 0
        self.short_qty = 0
        self.short_lost_change = np.nan
        self.long_lost_change = np.nan
        return self

    @classmethod
    def load(cls, **position):
        self = cls()
        self.update(position)
        return self
        
    def open(self, price):
        self.price = price
        self.latest_price = price
        self.is_openning = True
        
    def settlement_all(self):
        if self.long_qty != 0:
            self.long_sell(self.long_qty, self.latest_price)
        self.long_profit = 0
        if self.short_qty != 0:
            self.short_buy(self.short_qty, self.latest_price)
        self.short_profit = 0

    def settlement_long(self):
        if self.long_qty != 0:
            self.long_sell(self.long_qty, self.latest_price)
        self.long_profit = 0

    def settlement_short(self):
        if self.short_qty != 0:
            self.short_buy(self.short_qty, self.latest_price)
        self.short_profit = 0

    def set_balance(self, balance):
        self.symbol_balance += balance

    # def add_balance(self, balance):
    #     self.symbol_balance += balance

    # def reduce_balance(self, balance):
    #     assert  balance < self.value
    #     self.symbol_balance -= balance

    def long_buy(self, qty, price):
        #buy direction 1
        self.long_qty += qty
        self.symbol_balance -= self.long_fee * self.leverage * price

    def long_sell(self, qty, price):
        assert self.long_qty >= qty, f'reducing qty must be more than {self.long_qty}'
        self.long_qty -= qty 
        self.symbol_balance -= self.long_fee * self.leverage * price
    
    def short_sell(self, qty, price):
        #buy direction 1
        self.short_qty += qty
        self.symbol_balance -= self.short_fee * self.leverage * price

    def short_buy(self, qty, price):
        assert self.short_qty >= qty, f'reducing qty must be more than {self.short_qty}'
        self.short_qty -= qty 
        self.symbol_balance -= self.short_fee * self.leverage * price

    def isin_margin_call(self):
    
        long_moment_profit = self.long_profit + (self.latest_low - self.latest_price)  * self.leverage *  1 * self.long_qty
        short_moment_profit = self.short_profit + (self.latest_high - self.latest_price)  * self.leverage * -1 * self.short_qty
        return long_moment_profit + short_moment_profit  + self.symbol_balance < 0
    
    def call_margin(self):
            self.long_profit = 0
            self.short_profit = 0
            self.longh_qty = 0
            self.short_qty = 0
            self.symbol_balance = 0
    
    @property
    def price_change(self):
        price_change = (self.latest_price - self.price) / (self.price + 0.00000000000000000001) * self.leverage
        return price_change

    def calc_max_lost_change(self):

        if self.latest_price < self.price:
            self.short_lost_change = np.nan
            if self.long_qty > 0:
                self.long_lost_change = (self.latest_low - self.price) / (self.price + 0.00000000000000000001) * self.leverage
            else:
                self.long_lost_change = np.nan
        else:
            self.long_lost_change = np.nan
            if self.short_qty > 0:
                self.short_lost_change = (self.latest_high - self.price) / (self.price + 0.00000000000000000001) * self.leverage
            else:
                self.short_lost_change = np.nan

    
    def set_latest_ohlc(self,ohlc):
        self.latest_price = ohlc.close
        self.latest_high = ohlc.high
        self.latest_low = ohlc.low

    def set_current_datetime(self, current_datetime):
        self.current_datetime = current_datetime

    def update_order(self,order: Order):
        qty = order.fil_qty
        price = order.price
        match (order.action,  order.direction):
            case ("sell",-1):
                self.short_sell(qty, price)
            case ("buy",1): 
                self.long_buy(qty, price)
            case ("sell",1): 
                self.long_sell(qty, price)
            case ("buy",-1): 
                self.short_buy(qty, price)
                # cast "sell":

    def update_position(self, ohlc, current_datetime):

        if current_datetime == self.current_datetime:
            return 
        self.set_current_datetime(current_datetime)
        if self.is_openning:
            self.set_latest_ohlc(ohlc)
            long_equity  =  (self.latest_price - self.price)  * self.leverage * 1
            short_equity =  (self.latest_price - self.price) * self.leverage * -1
            self.long_profit  += long_equity  * self.long_qty 
            self.short_profit += short_equity * self.short_qty 
            self.calc_max_lost_change()
            if self. isin_margin_call():
                self.call_margin()
            self.value = self.symbol_balance + self.long_profit + self.short_profit
            self.price = self.latest_price

class HistoricalPositionMap(DictBase):
    def add_position(self,symbol:str, position : HistoricalPosition):
        self.__setattr__(symbol, position)

    def settlement_all_symbol(self)->None:
        try:
            for position in self.values():
                position.settlement_all()
        except Exception as e:
            logger.error(f'HistoricalPositionMap settlement_all_symbol error because:{e}')