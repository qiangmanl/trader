import numpy as np
from trader.utils.base import DictBase

class Order(DictBase):
    
    def __init__(self, symbol="", action="", qty=0, price=None, islong=True, order_type=""):
        """
        action: buy||sell
        status :["pending","partially_executed","finished","cancel"]
        order_type:"market" ||||| historical
        direction  1 : long, -1 : short
        """

        self.symbol = symbol
        self.direction =  int(islong) or -1
        self.action = action
        assert qty > 0.0000000001
        self.qty = qty
        self.price = price
        self.order_type = order_type
        self.status = 'pending'
        self.fil_qty = 0 
        self.qty_filled_rate = 0.9

    def finish_historical_order(self):
        self.filling_qty(self.qty)

    @property
    def locked(self):
        return self.status  in ["cancel","finished"]

    def set_price(self, price):
        if not self.locked and self.status == "pending":
            self.price = price 

    def set_status(self, status):
        if not self.locked:
            self.update(status=status) 

    def filling_qty(self, qty):
        #self.qty是目标完成的数量,self.fil_qty 是已经完成的数量,回测型策略订单直接fill self.qty的数量，以完成交易
        if qty > self.qty:
            return 
        if not self.locked:
            if (qty + self.fil_qty <= self.qty) and (self.qty_execute_rate < self.qty_filled_rate):
                self.fil_qty += qty
                if self.qty_execute_rate > self.qty_filled_rate:
                    self.set_status("finished")
                else:
                    self.set_status("partially_executed")
            else:
                self.set_status("finished")

    def cancel_order(self):
        if self.status == "pending":
            self.set_status("cancel")

    @property
    def qty_execute_rate(self):
        return self.fil_qty / self.qty


class OrderBookPattern:
    price    = np.nan
    long_qty = np.nan
    long_lost_change  = np.nan
    value    = np.nan
    short_qty= np.nan
    short_lost_change = np.nan
    @classmethod
    def create(cls,position):
        cls.price     = position.latest_price
        cls.long_qty  = position.long_qty
        cls.long_lost_change = position.long_lost_change
        cls.short_lost_change = position.short_lost_change
        cls.short_qty = position.short_qty
        cls.value     = position.value
        return cls
    
    @classmethod
    @property
    def orderbook(cls):
        orderbook = {
            "price"       : cls.price,
            "long_qty"    : cls.long_qty,
            "long_lost_change"  : cls.long_lost_change,
            "short_qty"   : cls.short_qty,
            "short_lost_change" : cls.short_lost_change,
            "value"       : cls.value
        }
        return orderbook

    @classmethod
    @property
    def keys(cls):
        return list(cls.orderbook.keys())