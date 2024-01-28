import numpy as np
from trader import logger
from trader.utils.base import DictBase
from trader.assets import Order
class HistoricalPosition(DictBase):
    """v0.0.3
    symbol = "sz000002"
    p = HistoricalPosition.init(symbol,20000,20,0,0)
    price = 21
    p.open(price)
    o = Order( symbol, action="buy", qty=20, price=price,islong=True, order_type="")
    o.finish_historical_order()
    # 买入当前时间片 不更新持仓
    p.update_order(o)
    p.update_position(21,"23-1-1")
    p.get_margin()

    p.update_position(26,"23-1-3")

    o = Order( symbol, action="sell", qty=1, price=27,islong=True, order_type="")
    o.finish_historical_order()
    p.update_order(o)
    p.update_position(27,"23-1-4")

    """


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
        self.short_change = np.nan
        self.long_change = np.nan
        self.orders = []
        self.margin_ratio =0.05 
        return self

    def open(self, price):
        self.price = price
        self.latest_price = price
        self.is_openning = True

    def set_balance(self, balance):
        self.symbol_balance += balance

    # def add_balance(self, balance):
    #     self.symbol_balance += balance

    # def reduce_balance(self, balance):
    #     assert  balance < self.value
    #     self.symbol_balance -= balance
        
    def get_margin(self):

        return ( 
            (self.symbol_balance + self.long_profit)  \
               / self.symbol_balance,
            (self.symbol_balance + self.short_profit) \
                / self.symbol_balance
        )

    def long_buy(self, qty, price):
        #buy direction 1
        trade_vol = (self.long_qty + qty + self.long_fee) * price * self.leverage
        if (self.symbol_balance - trade_vol ) / trade_vol > self.margin_ratio:
            self.long_qty += qty
            self.symbol_balance -= self.long_fee * self.leverage * price
        else:
            logger.warning(f"{self.symbol} long_buy does not have sufficient funds to cover the margin")

    def long_sell(self, qty, price):
        assert self.long_qty >= qty, f'reducing qty must be more than {self.long_qty}'
        self.long_qty -= qty 
        self.symbol_balance -= self.long_fee * self.leverage * price
    
    def short_sell(self, qty, price):
        #buy direction 1
        if self.symbol_balance - (self.short_qty + qty + self.short_fee) \
              * price * self.leverage > self.margin_ratio:
            self.short_qty += qty
            self.symbol_balance -= self.short_fee * self.leverage * price
        else:
            logger.warning(f"{self.symbol} short_sell does not have sufficient funds to cover the margin")

    def short_buy(self, qty, price):
        assert self.short_qty >= qty, f'reducing qty must be more than {self.short_qty}'
        self.short_qty -= qty 
        self.symbol_balance -= self.short_fee * self.leverage * price

    def when_margin_call(self):
        if self.long_qty > 0:
            if (self.symbol_balance + self.long_profit) \
                / self.symbol_balance  < self.margin_ratio:
                self.long_sell(self.long_qty)
        if self.short_qty > 0:
            if (self.symbol_balance + self.short_profit) \
                / self.symbol_balance  < self.margin_ratio:
                self.short_buy(self.short_qty)
    
    @property
    def price_change(self):
        price = self.price or 0.0000000000001
        price_change = (self.latest_price - price) / price * self.leverage
        return price_change

    def calc_max_lost_change(self):
        price = self.price or 0.0000000000001
        if self.latest_price < price:
        #     self.short_change = np.nan
            if self.long_qty > 0:
                # 最大亏损点
                self.long_change = (self.latest_low - price) / price * self.leverage
            else:
                # 无订单无需计算
                self.long_change = np.nan
            if self.short_qty > 0:
                # 最低赢利点
                self.short_change = (self.latest_price - price) / price * self.leverage
            else:
                self.short_change = np.nan
        else:

            if self.long_qty > 0:
                self.long_change = (self.latest_price - price) / price * self.leverage
            else:
                self.long_change = np.nan

            if self.short_qty > 0:
                self.short_change = -(self.latest_high - price) / price * self.leverage
            else:
                self.short_change = np.nan

    
    def set_latest_ohlc(self,ohlc):
        self.latest_price = ohlc.close
        self.latest_high = ohlc.high
        self.latest_low = ohlc.low

    def set_current_datetime(self, current_datetime):
        self.current_datetime = current_datetime

    def update_order(self, order:Order):
        self.orders.append(order)

    def process_order(self,order: Order):
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
            self.when_margin_call()
            long_equity  =  (self.latest_price - self.price)  * self.leverage * 1
            short_equity =  (self.latest_price - self.price) * self.leverage * -1
            self.long_profit  += long_equity  * self.long_qty 
            self.short_profit += short_equity * self.short_qty 
            self.calc_max_lost_change()
            for _ in range(len(self.orders)):
                order = self.orders.pop(0)
                self.process_order(order)
            self.value = self.symbol_balance + self.long_profit + self.short_profit
            self.price = self.latest_price








# p = HistoricalPosition.init(symbol,20000,2,0,0)
# p.open(21)
# o = Order( symbol, action="sell", qty=1, price=21,islong=False, order_type="")
# o.finish_historical_order()
# # 买入当前时间片 不更新持仓
# p.update_order(o)
# p.update_position(24,"23-1-1")
# p.update_position(25,"23-1-2")


# o = Order( symbol, action="sell", qty=1, price=25,islong=False, order_type="")
# o.finish_historical_order()
# # 买入当前时间片 不更新持仓
# p.update_order(o)
# p.update_position(26,"23-1-3")
# p.update_position(27,"23-1-4")

# o = Order( symbol, action="buy", qty=6, price=27,islong=False, order_type="")
# o.finish_historical_order()
# # 买入当前时间片 不更新持仓
# p.update_order(o)
# p.update_position(28,"23-1-5")