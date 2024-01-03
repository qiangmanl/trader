


import pandas as pd



class A:
    def __init__(self):

        self.df  = pd.DataFrame(columns = ["portfolio"]) 
        self.price = 21
        self.qty = 0
        self.df.loc[0,["portfolio"]] = 100

   
    def buy_long(self,qty):
        self.qty += qty
        portfolio = self.df.portfolio[self.df.index[-1]]
        self.df.loc[self.df.index[-1]+1,["portfolio"]] = portfolio - self.price * qty

    def sell_long(self,qty):
        self.qty -= qty
        portfolio = self.df.portfolio[self.df.index[-1]]
        self.df.loc[self.df.index[-1]+1,["portfolio"]] = portfolio + self.price * qty


    def next(self,price):
        self.price = price
        portfolio = self.df.portfolio[self.df.index[-1]]
        return  portfolio + self.price * self.qty
    
a = A()
a.next(22)
a.next(23)
a.buy_long(1)
a.next(23)
a.next(24)
a.next(25)

class Position:
    def openning(self, price, commission, leverage, direction=1):
        self.buying_fee = commission
        self.selling_fee = commission
        self.leverage = leverage
        self.price = price
        self.price_change = 0
        self.set_status("openning")
        self.direction = direction
   

    @property
    def is_openning(self):
        return self.status == "openning"
    
    def set_status(self, status):
        self.status = status
    
    @property
    def due_selling_fee(self):
        return self.leverage * self.selling_fee

    def update(self,update_price):
        # 市场每一次变化都需要更新价格
        if self.is_openning:
            self.price_change = (update_price - self.price) / self.price
            self.update_value()

    def update_value(self):
        # 价格变化后的最终资产价值
        self.value = self.price  +  self.price * self.price_change * self.leverage * self.direction
        print(self.value)
        # if self.value - self.due_selling_fee <= 0:
        #     self.margin_call()

    @property
    def theory_value(self):
        return self.value - self.due_selling_fee


class Position:
    """0.0.1"""
    def __init__(self,commission, leverage=1, direction=1):
        self.buying_fee = commission
        self.selling_fee = commission
        self.leverage = leverage
        self.direction = direction

    def openning(self , qty , price):
        self.qty = qty
        self.price = price


    def update(self,update_price):
        # 市场每一次变化都需要更新价格
        price_change = (update_price - self.price) / self.price
        equity = self.price  +  self.price * price_change * self.leverage * self.direction
        self.value = self.qty * equity
        print(self.value)

    
from werkzeug.local import Local
local = Local() 
price = local("price")
local.price =  21



class Position:
    """0.0.2"""
    def __init__(self,commission, leverage=1, direction=1):
        self.buying_fee = commission
        self.selling_fee = commission
        self.leverage = leverage
        self.direction = direction
        self.price = local.price
        
    @property
    def update_price(self):
        return local.price

    def get_equity(self):
        # 一单的价差
        price_change = (self.update_price - self.price) / self.price
        equity = self.price  +  self.price * price_change * self.leverage * self.direction
        return equity


from collections import deque


from collections import deque
# from trader.utils.tools import gen_random_id
class DictBase(dict):
    """dict like object that exposes keys as attributes"""

    __slots__ = ()
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    # __setstate__ = dict.update


    def update(self, *args, **kwargs):
        """update and return self -- the missing dict feature in python"""

        super().update(*args, **kwargs)



    




class HistoricalPosition(DictBase):
    """v0.0.3
    p = HistoricalPosition()
    p.openning(21)
    p.increasing(1)
    p.update(22)
    p.profit

    """

    def __init__(self, balance=10000, leverage=1, commission=0 ,direction=1):
        #
        self.set_balance(balance)
        self.leverage = leverage
        self.increasing_fee = commission
        self.reducing_fee = commission
        self.direction = direction
        self.value = self.init_balance

    def openning(self, price):
        self.price = price
        self.latest_price = price
        self.equitys = deque(maxlen=2)
        self.equitys.append(self.get_equity())
        self.profit = 0
        self.qty = 0

    def set_balance(self, balance):
        self.init_balance = balance

    # def add_balance(self, balance):
    #     self.init_balance += balance

    # def reduce_balance(self, balance):
    #     # 扣除的保证金不能导致 爆仓
    #     assert  balance < self.value
    #     self.init_balance -= balance


    
    @property
    def profit_rate(self):
        # 利润比率
        return (self.init_balance + self.profit) / (self.init_balance + 0.000001)

    @property
    def is_positive(self):
        # 判断持仓利好
        return self.value > self.init_balance

    def increasing(self, qty):
        self.qty += qty
        self.init_balance -= self.increasing_fee * self.leverage * self.latest_price

    def reducing(self, qty):
        assert self.qty >= qty, f'reducing qty must be more than {self.qty}'
        self.qty -= qty 
        self.init_balance -= self.increasing_fee * self.leverage * self.latest_price
    
    def isin_margin_call(self):
        return self.profit + self.init_balance < 0
    
    def decide_margin_call(self):
        if self. isin_margin_call():
            self.profit = 0
            self.qty = 0
            self.init_balance = 0
 
    def get_equity(self):
        # 一单的价差
        price_change = (self.latest_price - self.price) / self.price
        equity = self.price  +  self.price * price_change * self.leverage * self.direction
        return equity

    def set_latest_price(self,price):
        self.latest_price = price

    def update(self, price,increasing=0,reducing=0):
        self.set_latest_price(price)
        self.equitys.append(self.get_equity())
        self.profit += (self.equitys[1] - self.equitys[0]) * self.qty 
        self.decide_margin_call()
        if increasing:
            self.increasing(increasing)
        elif reducing:
            self.reducing(reducing)
        self.value = self.init_balance + self.profit 

p = HistoricalPosition()
p.openning(21)


class HistoricalPosition(DictBase):
    """v0.0.4
    p = HistoricalPosition()
    p.openning(21)
    p.update(22,increasing=1)
    p.value
    """

    def __init__(self, balance=10000, leverage=1, commission=0 ,direction=1):
        #
        self.set_balance(balance)
        self.leverage = leverage
        self.increasing_fee = commission
        self.reducing_fee = commission
        self.direction = direction
        self.qty = 0


    def set_balance(self, balance):
        self.balance = balance

    def add_balance(self, balance):
        self.balance += balance

    def reduce_balance(self, balance):
        # 扣除的保证金不能导致 爆仓
        assert  balance < self.value
        self.balance -= balance

    @property
    def pledge(self):
        return self.qty * self.latest_price
    
    @property
    def value(self):
        #持仓价值
        return self.balance + self.pledge
    
    # @property
    # def profit_rate(self):
    #     # 利润比率
    #     return self.value / (self.balance + 0.000001)

    @property
    def is_positive(self):
        # 判断持仓利好
        return self.value > self.balance

    def increasing(self, qty):
        self.qty += qty
        self.balance -= self.increasing_fee * self.leverage * self.latest_price
        self.balance -= qty * self.latest_price


    def reducing(self, qty):
        assert self.qty >= qty, f'reducing qty must be more than {self.qty}'
        self.qty -= qty 
        self.balance -= self.increasing_fee * self.leverage * self.latest_price
        self.balance += qty * self.latest_price

    def isin_margin_call(self):
        return self.value < 0
    
    def decide_margin_call(self):
        if self. isin_margin_call():
            self.qty = 0
            self.balance = 0
 

    def set_latest_price(self,price):
        self.latest_price = price

    def update(self, price,increasing=0, reducing=0):
        self.set_latest_price(price)
        self.decide_margin_call()
        if increasing:
            self.increasing(increasing)
        elif reducing:
            self.reducing(reducing)



def get_profit(balance, leverage, commission, price_change, direction):
    # 价格变化后的最终资产价值
    final_balance = balance * (1 + price_change * direction * leverage) - leverage * commission
    profit = final_balance - initial_balance
    return profit


initial_balance = 1000  # 初始资金
leverage_ratio = 2     # 杠杆倍数
price_change_percentage = 5  # 价格变化百分比
direction = 1  # 1表示买涨，-1表示买跌
profit = get_profit(1000, 1, 0.003, 0.01, 1)

print(f"杠杆交易收益: {profit:.7f} 美元")



class c:
	def __init__(self):
		print("我是实例方法，我被调用了")
	def __del__(self):
		print("我是销毁方法，我被调用了")
          
l = []

l.append(c())
l.pop()



def take_given_domain_symbol(task_list):
    symbols = [1,2,23,4,5,6,7,78,8,8,9,9,9,0,111]
    for task in task_list:
        if task in symbols:
            symbols.remove(task)
        else:
            task_list.remove(task)

    return symbols,task_list