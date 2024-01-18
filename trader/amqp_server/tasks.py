from typing import Any, Dict, List, Literal, Tuple, Union, NoReturn
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
# from functools import wraps

# def before_domain_exist(func):
#     @wraps(func)
#     def wrapper(domain_name, signals):
#         try:
#             domain = symbols_task_pool.get_domain(domain_name=domain_name)
#             if not domain:
#                 raise TasksRequestError(f'symbols_task_pool do not have  domain named {domain_name}')
#             else:
#                 return func(domain_name, signals)
#         except Exception as e:
#             return '' , f'from task.update_pool_symbols:{e.__repr__()}'


class TradingSignals:
    def __init__(self):
        self._signals = {}

    @property
    def signals(self):
        return self._signals
 
    def set_signals(self,signals):
        self._signals = signals

    def del_signals(self):
        self._signals = {}

@app.task
def domain_set_signals(domain_name, signals):
    try:
        domain = symbols_task_pool.get_domain(domain_name=domain_name)
        if not domain:
            raise TasksRequestError(f'symbols_task_pool do not have  domain named {domain_name}')
        else:
            domain.ts.set_signals(signals=signals)
            return True, ''
    except Exception as e:
        return '' , f'from task.update_pool_symbols:{e.__repr__()}'

@app.task
def domain_get_signals(domain_name):
    try:
        domain = symbols_task_pool.get_domain(domain_name=domain_name)
        if not domain:
            raise TasksRequestError(f'symbols_task_pool do not have  domain named {domain_name}')
        else:
            signals = domain.ts.signals
            domain.ts.del_signals()
            return signals, ''
    except Exception as e:
        return '' , f'from task.update_pool_symbols:{e.__repr__()}'

# {'2021-02-22 15:00:00': [{'symbol': 'SZ002212', 'direction': 1, 'action': 'buy', 'qty': 1, 'price': None, 'order_type': 'historical', 'status': 'pending', 'fil_qty': 0, 'qty_filled_rate': 0.9}],

class _SymbolObject(DictBase):
    def __init__(self,name:str)->None:
        self.name = name
        self.node_id = None
        self.is_leisure = True

#update_local_symbols
class _UpdatedSymbolsObject(DictBase):

    def update_symbol(self, symbol_name:str) -> _SymbolObject:
        symbol_obj = _SymbolObject(name=symbol_name)
        self.__setattr__(symbol_name ,symbol_obj)
        return symbol_obj


class DomainSymbolObject:

    def __init__(self):
        self.updated_symbols = _UpdatedSymbolsObject()
        super(DomainSymbolObject, self).__init__()
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
    

class DomainObjects(DomainSymbolObject, list):
    def __init__(self,domain) -> None:
        self.name = domain
        # self.ts = TradingSignals()
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
    
class SymbolsTaskPool(DictBase):
    # s  = SymbolsTaskPool()
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
            

symbols_task_pool = SymbolsTaskPool()

@app.task
def get_domain(domain_name):
    try:
        domain = symbols_task_pool.get_domain(domain_name=domain_name)
        if not domain:
            raise TasksRequestError(f'symbols_task_pool do not have  domain named {domain_name}')
        else:
            return domain_name,  ''
    except Exception as e:
        return '' , f'from task.update_pool_symbols:{e.__repr__()}'

@app.task
def update_pool_symbols(domain_name, task_symbols):
    # 有domain就更新symbol  没有就新建domain再添加   
    try:
        domain = symbols_task_pool.get_domain(domain_name)
        if  domain == None:
            # raise TasksRequestError("domain exist when update pool symbols, set update parameter to force mode if need forceful")
            domain = symbols_task_pool.new_domain(DomainObjects(domain_name))
        for task in task_symbols:
            domain.add_symbol(task)
        return True, None  
    except Exception as e:
        return '' , f'from task.update_pool_symbols:{e.__repr__()}'

@app.task
def create_pool_symbols(domain_name, task_symbols):
    # 删除旧的domain再添加domain，只有新建或者重建的时候
    try:
        symbols_task_pool.del_domain(domain_name)
        domain = symbols_task_pool.new_domain(DomainObjects(domain_name))
        for task in task_symbols:
            domain.add_symbol(task)
        return True, None  
    except Exception as e:
        return '' , f'from task.create_pool_symbols:{e.__repr__()}'


@app.task
def get_task_with_length(node_id, domain, length):
    try:
        domain = symbols_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError('symbols_task_pool do not have  domain named {domain}')
        domain.set_node_all_symbol_leisure(node_id)
        leisure_tasks_len = len(domain.leisure_symbols)
        if leisure_tasks_len == 0:
            raise TasksRequestError("domain do not have any leisure task")
        if length <= leisure_tasks_len:
            symbol_obj_list = domain.leisure_symbols[:length]
        else:
            symbol_obj_list = domain.leisure_symbols[:leisure_tasks_len]
        domain.set_node_symbols_working(node_id=node_id, symbol_list=symbol_obj_list)
        logger.warning(symbols_task_pool)
        
        return [symbol.name for symbol in symbol_obj_list], None
    except Exception as e:
        # return symbols_task_pool,str(e)
        logger.warning(e.__repr__())
        return '' , f'from task.get_task_with_length:{e.__repr__()}'

@app.task
def get_task_with_list(node_id, domain, symbol_list):
    try:
        domain = symbols_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbols_task_pool do not have  domain named {domain} or tasks function request a wrong way')
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
        # return symbols_task_pool,str(e)
        logger.warning(e.__repr__())
        return '' , f'from task.get_task_with_list:{e.__repr__()}'



# s  = SymbolsTaskPool()
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
def domain_get_symbol_object(domain:str, symbol:str) -> [ _SymbolObject | None, Literal[""] | str]:
    try:
        domain = symbols_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbols_task_pool do not have  domain named {domain} or tasks function request a wrong way')
        symbol = domain.get_symbol(symbol)
        if symbol:
            return symbol, ''
        raise TasksRequestError("domain_get_symbol: symbol no exist")
    except Exception as e:
        return None, f'from task.domain_get_symbol_object:{e.__repr__()}'

@app.task   
def domain_get_symbol_attr(domain:str, symbol:str,attr:str) -> Tuple[Any, Literal[""] | str]:
    try:
        domain = symbols_task_pool.get_domain(domain)
        if not domain:
            raise TasksRequestError(f'symbols_task_pool do not have  domain named {domain} or tasks function request a wrong way')
        symbol = domain.get_symbol(symbol)
        if symbol:
            return symbol.__getattr__(attr,None), ''
        raise TasksRequestError("domain_get_symbol: symbol no exist")
    except Exception as e:
        return None, f'from task.domain_get_symbol_attr:{e.__repr__()}'


# @app.task
# def get_domain(domain_name):

#             return domain_name,  ''
#     except Exception as e:
#         return '' , f'from task.update_pool_symbols:{e.__repr__()}'

