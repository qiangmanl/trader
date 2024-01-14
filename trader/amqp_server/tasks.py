from typing import Any, List, Literal, Tuple, Union, NoReturn
from celery import Celery
from trader import config,logger
from trader.utils.base import DictBase 
from trader.exception import TasksAccountError, TasksRequestError
# """
#     不要在此页执行可能阻塞的指令， 比如直接调用task函数
# """

config.setdefault("amqp_server",{})
# import pdb
# pdb.set_trace()
config.amqp_server.setdefault("broker",'amqp://guest@localhost//')
config.amqp_server.setdefault("backend" ,'rpc://')

app = Celery('trader_tasks' , broker=config.amqp_server["broker"],backend=config.amqp_server["backend"])
app.conf.update(
    include=['trader.amqp_server.tasks'],
    ACKS_LATE=True,  # 允许重试
    ACCEPT_CONTENT=['pickle', 'json'],
    TASK_SERIALIZER='json',
    RESULT_SERIALIZER='json',
    # 设置并发worker数量
    WORKER_CONCURRENCY=4, 
    # 每个worker最多执行500个任务被销毁，可以防止内存泄漏
    MAX_TASKS_PER_CHILD=500, 
    broker_heartbeat=0,  # 心跳
    TASK_TIME_LIMIT=12 * 30,  # 超时时间
    broker_connection_retry_on_startup=True,
    CELERY_ENABLE_UTC=True,
    TIMEZONE='Asia/Shanghai'
)

class _SymbolObject(DictBase):
    def __init__(self,name:str)->None:
        self.name = name
        self.node_id = None
        self.is_leisure = True
        self.balance = 0
        self.account_open = False
        self.transfer_log = [0,]
    def return_back(self, back:str)-> Any:
        match back:
            case "balance":
                return self.__getattr__("balance",None)
            case "amount":
                 return self.transfer_log[-1]
    @property
    def last_amount(self) -> Union[float , int]:
        return self.transfer_log[-1]
#update_local_symbols
class _UpdatedSymbolObjects(DictBase):

    def update_symbol(self, symbol_name:str) -> _SymbolObject:
        symbol_obj = _SymbolObject(name=symbol_name)
        self.__setattr__(symbol_name ,symbol_obj)
        return symbol_obj


class DomainSymbolObjects:

    def __init__(self):
        self.updated_symbols = _UpdatedSymbolObjects()
        super(DomainSymbolObjects, self).__init__()
    def symbol_exist(self, symbol_name:str):
        return  symbol_name in self.updated_symbols.keys() or False

    def add_symbol(self,symbol_name : str) -> None:
        if self.symbol_exist(symbol_name) == False:
            symbol_obj = self.updated_symbols.update_symbol(symbol_name)
            self.append(symbol_obj)
            return True
        return False
    
    def del_all_symbol(self):
        if self.length > 0:
            for _ in range(self.length):
                symbol = self.pop(0)
                self.updated_symbols.pop(symbol.name)


    
    def set_node_symbol_working(self,symbol,node_id) ->None:
        symbol_obj = self.get_symbol(symbol)
        if symbol_obj:
            symbol_obj.is_leisure = False
            symbol_obj.node_id = node_id

    def set_node_symbols_working(self,node_id, symbol_list : List[_SymbolObject]):
        for symbol in symbol_list:
            self.set_node_symbol_working(symbol.name, node_id)

    def set_node_symbol_leisure(self,symbol, node_id) -> None:

        symbol_obj = self.get_symbol(symbol)
        if symbol_obj:
            if symbol_obj.node_id == node_id:
                symbol_obj.is_leisure = True
                symbol_obj.node_id = None

    def get_symbol(self, symbol_name) -> _SymbolObject:
        return self.updated_symbols.__getattr__(symbol_name, None) 
    

class HistoricalAccount(DictBase):
    """

    """
    def __init__(self):
        self.total_asset = None
        self.transfer_fee = None
    #
    def init(self, total_asset, transfer_fee) -> None | NoReturn:
        if self.total_asset == None:
            self.transfer_fee = transfer_fee
            self.total_asset = total_asset
            self.initiated = True
        else:
            raise TasksAccountError("account init error:account existed")

    def check_transfer_to_amount(self, amount) -> bool:
        return amount * (1 + self.transfer_fee) <= self.total_asset
    
    def check_transfer_from_amount(self, symbol, amount) -> bool:
        return symbol.balance >= amount * (1 + self.transfer_fee)


class DomainAccountObjects:
    def __init__(self):
        self.account = HistoricalAccount()
        super(DomainAccountObjects, self).__init__()

    def get_symbol_balance(self, symbol):
        symbol = self.get_symbol(symbol)
        if symbol:
            return symbol.balance
        return 
    
    def set_symbol_account_open(self, symbol):
        symbol = self.get_symbol(symbol)
        if symbol:
            symbol.account_open = True
            return 
        return 
    
    def transfer_to_symbol(self, amount : Union[float, int],
                            symbol:str, 
                            back: Literal["balance"] | Literal["amount"]="balance"
                            ) -> bool | NoReturn:
        symbol  = self.get_symbol(symbol)
        amount_ok = self.account.check_transfer_to_amount(amount)
        if symbol and amount_ok:
            symbol.balance += amount
            self.account.total_asset -= amount * (1 + self.account.transfer_fee)
            symbol.transfer_log.append(amount)
        else:
            raise TasksAccountError(f"check symbol:{symbol.name} and \
                                    check_transfer_to_amount:{amount_ok}")
        
        return symbol.return_back(back)
    
    def transfer_from_symbol(self, amount : Union[float, int],
                            symbol:str, 
                            back: Literal["balance"] | Literal["amount"]="balance"
                            ) -> bool | NoReturn:
        symbol = self.get_symbol(symbol)
        amount_ok = self.account.check_transfer_from_amount(symbol, amount)
        if symbol and amount_ok:
            symbol.balance -= amount * (1 + self.account.transfer_fee)
            self.account.total_asset += amount
            symbol.transfer_log.append(amount)
        else:
            raise TasksAccountError(f"check symbol:{symbol.name} and \
                                    check_transfer_from_amount:{amount_ok}")
        return symbol.return_back(back)
    
    def init_account(self,total_asset, transfer_fee ) ->  None | NoReturn:
        self.account.init(total_asset, transfer_fee)

class DomainObjects(DomainSymbolObjects, DomainAccountObjects, list):
    def __init__(self,domain) -> None:
        self.name = domain
        super(DomainObjects, self).__init__()

    def set_node_all_symbol_leisure(self, node_id) -> None:
        for symbol in self.working_symbols:
            self.set_node_symbol_leisure(symbol.name, node_id)

    
    def get_node_symbols(self,node_id) -> List[_SymbolObject]:
        return  [symbol for symbol in self if symbol.node_id == node_id]


    def get_node_working_symbols(self, node) -> List[_SymbolObject]:
        return [symbol for symbol in self.working_symbols if symbol.node_id == node]
    
    @property
    def all_symbols(self) -> List[_SymbolObject]:
        return self

    @property
    def leisure_symbols(self) -> List[_SymbolObject]:
        return    [symbol for symbol in self if symbol.is_leisure == True]

    @property
    def working_symbols(self) -> List[_SymbolObject]:
        return  [symbol for symbol in self if symbol.is_leisure == False]

    @property
    def length(self)->int:
        return len(self.all_symbols)
    
class SymbolTaskPool(DictBase):
    # s  = SymbolTaskPool()
    # d = s.new_domain(DomainObjects("demain1"))
    # d.add_symbol("SZ000002")
    # d.add_symbol("SZ000003")
    # d.add_symbol("SZ000004")
    # d.set_node_symbol_working("SZ000002","a")
    # d.set_node_symbol_working("SZ000003","a")
    # d.set_node_symbol_working("SZ000004","b")
    # d.leisure_symbols
    # d.get_node_working_symbols("b")
    # d.set_node_symbol_leisure("SZ000002","a")
    # d.set_node_all_symbol_leisure("a")
    def new_domain(self,domain : DomainObjects):
        if self.__getattr__(domain.name, None) == None:
            self.__setattr__(domain.name, domain)
            return domain
        else:
            return None
        
    def get_domain(self,domain_name):
        return  self.__getattr__(domain_name, None)
    
    def del_domain(self,domain_name):
        domain = self.get_domain(domain_name)
        if domain:
            domain.del_all_symbol()
            self.__delattr__(domain_name)
            

symbol_task_pool = SymbolTaskPool()


@app.task
def update_pool_symbols(domain_name, task_symbols):
    # 有domain就更新symbol  没有就新建domain再添加   
    try:
        domain = symbol_task_pool.get_domain(domain_name)
        if  domain == None:
            # raise TasksRequestError("domain exist when update pool symbols, set update parameter to force mode if need forceful")
            domain = symbol_task_pool.new_domain(DomainObjects(domain_name))
        for task in task_symbols:
            domain.add_symbol(task)
        return True, None  
    except Exception as e:
        return '' , f'from task.update_pool_symbols:{e.__repr__()}'

@app.task
def create_pool_symbols(domain_name, task_symbols):
    # 删除旧的domain再添加domain，只有新建或者重建的时候
    try:
        symbol_task_pool.del_domain(domain_name)
        domain = symbol_task_pool.new_domain(DomainObjects(domain_name))
        for task in task_symbols:
            domain.add_symbol(task)
        return True, None  
    except Exception as e:
        return '' , f'from task.create_pool_symbols:{e.__repr__()}'


@app.task
def get_task_with_length(node_id, domain, length):
    try:
        domain = symbol_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError('symbol_task_pool do not have  domain named {domain}')
        domain.set_node_all_symbol_leisure(node_id)
        leisure_tasks_len = len(domain.leisure_symbols)
        if leisure_tasks_len == 0:
            raise TasksRequestError("domain do not have any leisure task")
        if length <= leisure_tasks_len:
            symbol_obj_list = domain.leisure_symbols[:length]
        else:
            symbol_obj_list = domain.leisure_symbols[:leisure_tasks_len]
        domain.set_node_symbols_working(node_id=node_id, symbol_list=symbol_obj_list)
        logger.warning(symbol_task_pool)
        
        return [symbol.name for symbol in symbol_obj_list], None
    except Exception as e:
        # return symbol_task_pool,str(e)
        logger.warning(e.__repr__())
        return '' , f'from task.get_task_with_length:{e.__repr__()}'

@app.task
def get_task_with_list(node_id, domain, symbol_list):
    try:
        domain = symbol_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbol_task_pool do not have  domain named {domain}')
        domain.set_node_all_symbol_leisure(node_id)
        
        if domain.get_node_symbols(node_id) != []:
            raise TasksRequestError(f'get_task_with_list domain.get_node_symbols(node_id) != []')
        
        for symbol in symbol_list:
            domain.set_node_symbol_working(symbol, node_id=node_id)
        symbols = domain.get_node_working_symbols(node_id)
        if symbols == []:
            raise TasksRequestError(f'{symbol_list} make empty task')
        return [symbol.name for symbol in symbols], None
    except Exception as e:
        # return symbol_task_pool,str(e)
        logger.warning(e.__repr__())
        return '' , f'from task.get_task_with_list:{e.__repr__()}'



# s  = SymbolTaskPool()
# d = s.new_domain(DomainObjects("demain1"))
# d.add_symbol("SZ000002")
# d.add_symbol("SZ000003")
# d.add_symbol("SZ000004")
# d.set_node_symbol_working("SZ000002","a")
# d.set_node_symbol_working("SZ000003","a")
# d.set_node_symbol_working("SZ000004","b")
# d.leisure_symbols
# d.get_node_working_symbols("b")
# d.set_node_symbol_leisure("SZ000002","a")
# d.set_node_all_symbol_leisure("a")
# d.init_account(100000,0)
# d.transfer_to_symbol(300,"SZ000002")
# d.transfer_from_symbol(1,"SZ000002")
# d.account


@app.task
def init_account(domain:str,
                  total_asset : Union[int,str], 
                  transfer_fee : Union[int,str]
                ) -> Tuple[None | str , HistoricalAccount | Literal[""]]:
    try:
        domain = symbol_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbol_task_pool do not have  domain named {domain}')
        if transfer_fee < 0 and transfer_fee >=1:
            raise TasksAccountError(f'transfer_fee number error when init account')
        domain.init_account(total_asset, transfer_fee)
        return domain.account, ''
    except Exception as e:
        return None ,f'from task.init_account:{e.__repr__()}'
    
@app.task
def get_tasks_account(domain:str) -> Tuple[None | str , HistoricalAccount | Literal[""]]:
    try:
        domain = symbol_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbol_task_pool do not have  domain named {domain}')
        if domain.account.initiated == True:
            return domain.account, ''
        else:
            raise TasksAccountError("domain account is not initiated")
    except Exception as e:
        return None ,f'from task.get_tasks_account:{e.__repr__()}'


@app.task
def account_transfer_to(
        domain:str, 
        amount: Union[int,float],
      symbol:str
    ) -> Tuple[ bool|None, Literal[""] | str]:
    try:
        domain = symbol_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbol_task_pool do not have  domain named {domain}')
        success = domain.transfer_to_symbol(amount, symbol, back="balance")
        if success:
            return success, ''
    except Exception as e:
        return None, f'from task.account_transfer_to:{e.__repr__()}'
    
@app.task
def open_account_symbol(
    #
        domain:str, 
        amount: Union[int,float],
      symbol:str
    ) -> Tuple[ bool|None, Literal[""] | str]:
    try:
        domain = symbol_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbol_task_pool do not have  domain named {domain}')
        success = domain.transfer_to_symbol(amount, symbol, back="balance")
        if success:
            domain.set_symbol_account_open(symbol)
            return success, ''
    except Exception as e:
        return None, f'from task.open_account_symbol:{e.__repr__()}'
    
    
@app.task
def account_transfer_from(
        domain:str,
        amount: Union[int,float],
        symbol:str
    ) -> Tuple[ bool | None, Literal[""] | str]:
    try:
        domain = symbol_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbol_task_pool do not have  domain named {domain}')
        success = domain.transfer_from_symbol(amount, symbol, back="balance")
        if success:
            return success, ''
    except Exception as e:
        return 0, f'from task.account_transfer_from:{e.__repr__()}'

@app.task   
def domain_get_symbol_info(domain:str, symbol:str) -> [ _SymbolObject | None, Literal[""] | str]:
    try:
        domain = symbol_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbol_task_pool do not have  domain named {domain}')
        symbol = domain.get_symbol(symbol)
        if symbol:
            return symbol, ''
        raise TasksRequestError("domain_get_symbol: symbol no exist")
    except Exception as e:
        return None, f'from task.domain_get_symbol_info:{e.__repr__()}'

@app.task   
def domain_get_symbol_attr(domain:str, symbol:str,attr:str) -> Tuple[Any, Literal[""] | str]:
    try:
        domain = symbol_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbol_task_pool do not have  domain named {domain}')
        symbol = domain.get_symbol(symbol)
        if symbol:
            return symbol.__getattr__(attr,None), ''
        raise TasksRequestError("domain_get_symbol: symbol no exist")
    except Exception as e:
        return None, f'from task.domain_get_symbol_attr:{e.__repr__()}'
