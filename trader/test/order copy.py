

from trader.utils.base import DictBase

class Order(DictBase):

    @classmethod
    def create(cls, symbol="", action="", qty=0, order_type=""):
        """
        action: buy||sell
        status :["pending","partially_executed","finished","cancel"]
        order_type:"market" ||||| historical
        direction  1 : long, -1 : short
        """
        cls.symbol = symbol
        cls.action = action
        cls.price = None
        cls.qty = qty or 0.00000000001
        cls.order_type = order_type
        cls.status = 'pending'
        cls.fil_qty = 0 
        cls.qty_filled_rate = 0.9

        return cls
    
    @classmethod
    def finish_historical_order(cls):
        cls.filling_qty(cls.qty)

    @classmethod
    @property
    def locked(cls):
        return cls.status  in ["cancel","finished"]
    
    @classmethod
    def set_price(cls, price):
        if not cls.locked and cls.status == "pending":
            cls.price = price 

    @classmethod
    def set_status(cls, status):
        if not cls.locked:
            cls.status=status 

    @classmethod
    def filling_qty(cls, qty):
        #cls.qty是目标完成的数量,cls.fil_qty 是已经完成的数量,回测型策略订单直接fill cls.qty的数量，以完成交易
        if qty > cls.qty:
            return 
        if not cls.locked:
            if (qty + cls.fil_qty <= cls.qty) and (cls.qty_execute_rate() < cls.qty_filled_rate):
                cls.fil_qty += qty
                if cls.qty_execute_rate() > cls.qty_filled_rate:
                    cls.set_status("finished")
                else:
                    cls.set_status("partially_executed")
            else:
                cls.set_status("finished")

    @classmethod
    def cancel_order(cls):
        if cls.status == "pending":
            cls.set_status("cancel")

    @classmethod
    def qty_execute_rate(cls):
        return cls.fil_qty / cls.qty


# class OrdersBook(dict):
#     # 有信号产生的订单，有可能未完成交易，也有可能存在多条订单,但这种情况一般只在实盘的时候存在
#     def __init__(self,order_list_type):
#         self.order_list_type = order_list_type
    
#     def add_new_order(self,order_id:str, order:Order):
#         self.update({order_id:[]})
#         self[order_id].append(order)

#     def add_order(self,order_id:str, order:Order):
#         self[order_id].append(order)

#     def update_order(self,order_id, order):
#         if order_id in self:
#             self.add_order(order_id, order=order)
#         else:
#             self.add_new_order(order_id,order=order)

#     def sell(self,order_id, price, qty, order_type):
#         order = Order(order_id, price=price,action="sell",qty=qty,order_type=order_type)
#         self.update_order(order)


#     def buy(self, order_id, price, qty, order_type):
#         order = Order(order_id, price=price,action="buy",qty=qty,order_type=order_type)
#         self.update_order(order)

#     def update_status(self, order_id, status):
#         if order_id in self:
#             order  =  self[order_id]
#             if not order.locked:
#                 order.set_status(status)




