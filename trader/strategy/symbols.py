import pandas as pd
from trader import logger
from trader.exception import SymbolProcessError
from trader.utils.base import DictBase
from trader.assets import OrderBookPattern
# from trader.utils.tasks_function import \
#     account_init, \
#     account_load, \
#     account_transfer_to, \
#     account_get_symbol_asset \
#     # account_get_total_asset
from trader.utils.base import SymbolsPropertyDict


class _SymbolObject(DictBase):
    def __init__(self,name:str)->None:
        self.name = name
        self.balance = 0
        self.state = "created"
        self.history = None
        self.position = None
        self.property_dict = SymbolsPropertyDict()
        self.orderbook = None

    def set_state(self, state):
        """
            {created,balanced}
        """
        self.state = state


class SymbolsObject(DictBase):
    # s.update_symbol("a")
    #{'name': 'a', 'balance': 0, 'state': 'created'}
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
        else:
            raise SymbolProcessError(f'SymbolManager add_symbol:{symbol_name} exist')



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

    def get_symbol_state(self,symbol_name):
        symbol = self.get_symbol(symbol_name)
        if symbol:
            return symbol.state

class DomainSymbols(AccountObject, SymbolManager, list):
    def __init__(self,domain_name, symbols) -> None:
        self.name = domain_name
        # self.ts = TradingSignals()
        super(DomainSymbols, self).__init__()
        for symbol in symbols:
            self.add_symbol(symbol)

    def set_all_symbol_done(self):
        for symbol_name in self.updated_symbols:
            self.set_symbol_state(symbol_name, "done")
