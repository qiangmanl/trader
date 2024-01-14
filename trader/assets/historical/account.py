from trader import logger
from trader.utils.base import DictBase
from trader.utils.tasks_function import \
    account_init, \
    account_load, \
    account_transfer_to, \
    account_get_symbol_asset, \
    account_get_total_asset

class HistoricalAccountBase(DictBase):

    def transfer_to_account(self):
        raise NotImplementedError(f'{self.__class__.__name__}:transfer_to')

    def transfer_from_account(self):
        raise NotImplementedError(f'{self.__class__.__name__}:transfer_to')

    def get_symbol_asset(self):
        raise NotImplementedError(f'{self.__class__.__name__}:get_symbol_asset')
    
    def get_total_asset(self):
        raise NotImplementedError(f'{self.__class__.__name__}:get_total_asset')

class SingleNodeAccount(HistoricalAccountBase):
    name = "single_node_historical_account"
    """
    Usage:
        a = SingleNodeAccount(total_asset=2000000,transfer_fee=0.00000)
        a.transfer_to(10000,"SZ000001")
        a.get_symbol_asset("SZ000001")#10000
    """

    def __init__(self, total_asset, transfer_fee):
        self.transfer_fee = transfer_fee
        self.total_asset = total_asset
        self.symbol_asset = DictBase()
        self.prepared = True
        
    def transfer_from_account(self, balance, symbol) -> float | None:
        if symbol  in self.symbol_asset:
            if (self.total_asset  > balance + balance * self.transfer_fee):
                self.total_asset -= balance + balance * self.transfer_fee
            else:
                balance = self.total_asset - self.total_asset * self.transfer_fee
                self.total_asset  = 0
            symbol_asset_balnce = self.symbol_asset.__getattr__(symbol)
            self.symbol_asset.__setattr__(symbol, balance + symbol_asset_balnce) 
            return balance
        return 0

    def get_symbol_asset(self, symbol):
        return self.symbol_asset.__getattr__(symbol)
    

class TasksAccount(HistoricalAccountBase):
    name = "tasks_historical_account"

    def __init__(self):
        self.prepared = None
        self.total_asset = None
        self.transfer_fee = None
        self.domain = None

    @classmethod
    def init_account(cls, domain, total_asset, transfer_fee):
        success, err = account_init(domain, total_asset, transfer_fee)
        if err:
            logger.error(err)
            exit()
        self = cls()
        self.prepared = True
        self.total_asset = success.get("total_asset",None)
        self.transfer_fee = success.get("transfer_fee",None)
        self.domain = domain
        return self

    @classmethod
    def load_account(cls, domain):
        success, err = account_load(domain)
        if err:
            logger.error(err)
            exit()
        self = cls()
        self.prepared = True
        self.total_asset = success.get("total_asset",None)
        self.transfer_fee = success.get("transfer_fee",None)
        self.domain = domain
        return self

    def reload(self):
        if self.prepared:
            success, err = account_load(self.domain)
            if err:
                logger.error(err)
                exit()
            self.total_asset = success.get("total_asset",None)
            self.transfer_fee = success.get("transfer_fee",None)
        

    def transfer_from_account(self, domain, amount, symbol):
        amount, err = account_transfer_to(domain, amount, symbol)
        if amount:
            return amount
        else:
            logger.error(err)
            return None
        
    def get_symbol_asset(self, domain, symbol):
        #symbol不存在 需要相关处理逻辑
        asset, err = account_get_symbol_asset(domain=domain, symbol=symbol) 
        logger.debug(asset)
        #获得tasks symbol asset之后更新本地，切不要从本地直接获得
        if err:
            logger.error(err)
            return 
        else:
            return asset
        
    def get_total_asset(self):
        total_asset, err = account_get_total_asset() 
        #获得tasks symbol asset之后更新本地，切不要从本地直接获得
        self.tasks_symbol_asset =  total_asset
        if total_asset:
            return total_asset
        else:
            logger.error(err)
            return        
  