import pandas as pd
from trader.utils.base import DictBase
from trader.assets import OrderBookPattern
from trader.utils.base import SymbolsPropertyDict


class _SymbolObject(DictBase):
    def __init__(self,name:str)->None:
        self.name = name
        self.balance = 0
        self.state = "open_account"
        self.history = None
        self.position = None
        self.property_dict = SymbolsPropertyDict()
        self.orderbook = pd.DataFrame(columns=OrderBookPattern.keys)

    def set_state(self, state):
        self.state = state


class SymbolsObject(DictBase):
    # s.update_symbol("a")
    #{'name': 'a', 'balance': 0, 'state': 'open_account'}
    def update_symbol(self, symbol_name:str) -> _SymbolObject:
        symbol_obj = _SymbolObject(name=symbol_name)
        self.__setattr__(symbol_name ,symbol_obj)
        return symbol_obj


class AccountObject:
    def __init__(self):
        super(AccountObject, self).__init__()

    def get_symbol_balance(self, symbol):
        symbol = self.get_symbol(symbol)
        if symbol:
            return symbol.balance
        return 
    
    def transfer_to_symbol(self, balance, symbol):
        symbol = self.get_symbol(symbol)
        if symbol:
            symbol.balance += balance
        return symbol.balance
    

class SymbolManager:

    def __init__(self):
        self.updated_symbols = SymbolsObject()
        super(SymbolManager, self).__init__()

    def symbol_exist(self, symbol_name:str):
        return  symbol_name in self.updated_symbols.keys() or False

    def add_symbol(self,symbol_name : str) -> None:
        if self.symbol_exist(symbol_name) == False:
            symbol_obj = self.updated_symbols.update_symbol(symbol_name)
            self.append(symbol_obj)
            setattr(self, symbol_obj.name, symbol_obj)
            return True
        return False
    
    def del_all_symbol(self):
        if self.length > 0:
            for _ in range(self.length):
                symbol = self.pop(0)
                self.updated_symbols.pop(symbol.name)

    def get_symbol(self, symbol_name) -> _SymbolObject:
        return self.updated_symbols.__getattr__(symbol_name, None) 

    def set_symbol_state(self, symbol_name, state):
        symbol = self.get_symbol(symbol_name)
        if symbol:
            symbol.set_state(state)


class DomainSymbols(AccountObject, SymbolManager, list):
    def __init__(self,domain_name) -> None:
        self.name = domain_name
        # self.ts = TradingSignals()
        super(DomainSymbols, self).__init__()







# class TasksAccount(HistoricalAccountBase):
#     name = "tasks_historical_account"

#     def __init__(self):
#         self.prepared = None
#         self.total_asset = None
#         self.transfer_fee = None
#         self.domain = None

#     @classmethod
#     def init_account(cls, domain, total_asset, transfer_fee):
#         success, err = account_init(domain, total_asset, transfer_fee)
#         if err:
#             logger.error(err)
#             exit()
#         self = cls()
#         self.prepared = True
#         self.total_asset = success.get("total_asset",None)
#         self.transfer_fee = success.get("transfer_fee",None)
#         self.domain = domain
#         return self

#     @classmethod
#     def load_account(cls, domain):
#         success, err = account_load(domain)
#         if err:
#             logger.error(err)
#             exit()
#         self = cls()
#         self.prepared = True
#         self.total_asset = success.get("total_asset",None)
#         self.transfer_fee = success.get("transfer_fee",None)
#         self.domain = domain
#         return self

#     def reload(self):
#         if self.prepared:
#             success, err = account_load(self.domain)
#             if err:
#                 logger.error(err)
#                 exit()
#             self.total_asset = success.get("total_asset",None)
#             self.transfer_fee = success.get("transfer_fee",None)
        

#     def transfer_from_account(self, domain, amount, symbol):
#         amount, err = account_transfer_to(domain, amount, symbol)
#         if amount:
#             return amount
#         else:
#             logger.error(err)
#             return None
        
#     def get_symbol_asset(self, domain, symbol):
#         #symbol不存在 需要相关处理逻辑
#         asset, err = account_get_symbol_asset(domain=domain, symbol=symbol) 
#         logger.debug(asset)
#         #获得tasks symbol asset之后更新本地，切不要从本地直接获得
#         if err:
#             logger.error(err)
#             return 
#         else:
#             return asset
        
#     # def get_total_asset(self):
#     #     total_asset, err = account_get_total_asset() 
#     #     #获得tasks symbol asset之后更新本地，切不要从本地直接获得
#     #     self.tasks_symbol_asset =  total_asset
#     #     if total_asset:
#     #         return total_asset
#     #     else:
#     #         logger.error(err)
#     #         return        
  