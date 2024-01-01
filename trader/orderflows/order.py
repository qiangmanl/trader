from trader.utils.base import DictBase

class Order(DictBase):
    def __init__(self, symbol="", action="", qty=0.001, price=0, order_type=""):
        """
        action: buy||sell
        status :["pending","partially_executed","finished","cancel"]
        order_type:"market" ||||| historical
        direction  1 : long, -1 : short
        """

        self.symbol = symbol
        self.action = action
        self.qty = qty
        self.price = price
        self.order_type = order_type
        self.status = 'pending'
        self.fil_qty = 0 
        self.qty_filled_rate = 0.9
        if order_type == "historical":
            self.finish_historical_order()

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




