from celery import Celery
from trader import config
from trader.utils.base import DictBase 
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


class SymbolMap(DictBase):

    def add_domain(self,node_domain:str) -> None:
        self.__setattr__(node_domain,[])

    def add_symbol(self,node_domain, symbol: str | list) -> None:
        node_domain in self or self.add_domain(node_domain)
        if isinstance(symbol,str) and symbol not in self.all_symbols:
            self.__getattr__(node_domain).append(symbol)
        elif isinstance(symbol, list):
            for element in symbol:
                if element not in self.all_symbols and isinstance(element, str):
                    self.__getattr__(node_domain).append(element)


    def update_symbols(self,node_domain, symbols:list):
        node_domain not in  self or self.add_domain(node_domain)
        self.__setattr__(node_domain,symbols)


        # 通过node_domain 有序取出
    def take_orderly_domain_symbol(self,node_domain,length):
        symbols = self.__getattr__(node_domain, [])
        self.update_symbols(node_domain, symbols[length:])
        return symbols[:length]

    def take_given_domain_symbol(self,node_domain,task_list):
        takes = []
        symbols = self.__getattr__(node_domain, [])
        for task in task_list:
            print(task)
            if task in symbols:
                symbols.remove(task)
                takes.append(task)
        self.update_symbols(node_domain, symbols)
        return takes


    @property
    def all_symbols(self) -> list:
        all_symbols = []
        for _,symbols in list(self.items()):
            all_symbols.extend(symbols)
        return all_symbols








# from typing import List

class TaskMap(DictBase):
    
    def add_node(self,node_id:str) -> None:
        self.__setattr__(node_id,[])

    def del_node(self,node_id:str) -> None:
        self.__delattr__(node_id)

    def get_task(self,node_id:str) -> list:
        return self.__getattr__(node_id,[])

    def clean_idle_node(self) -> None:
        for node_id,task in list(self.items()):
          not task == [] or self.del_node(node_id)

    def pop_node_task(self, node_id) -> None:
        return symbol_task_pool.task_map.pop(node_id)

    def add_task(self,node_id, task: str | list) -> None:
        node_id in self or self.add_node(node_id)
        if isinstance(task,str) and task not in self.task_on_nodes:
            self.__getattr__(node_id).append(task)
        elif isinstance(task, list):
            for element in task:
                if element not in self.task_on_nodes and isinstance(element, str):
                    self.__getattr__(node_id).append(element)



    @property
    #所有在节点上的任务
    def task_on_nodes(self) -> list:
        task_on_nodes = []
        for _,task in list(self.items()):
            task_on_nodes.extend(task)
        return task_on_nodes
    
    @property
    def on_nodes_task_length(self) -> int:
        return len(self.task_on_nodes)




# s.add_node("a")
# s.add_node("b")
# s.add_task("c",1)
    
class NodeMap(DictBase):

    def get_node(self,node_id):
        return self.__getattr__(node_id, None)
           
    def set_node(self, node_id, domain):
        self.__setattr__(node_id, domain)
        return domain

class SymbolTaskPool(DictBase):
    def __init__(self) -> None:
        self.task_map = TaskMap()
        self.symbol_map = SymbolMap()
        self.node_map = NodeMap()

    @property
    def all_pool_task(self):
        return self.task_map.task_on_nodes.extend(self.symbol_map.all_symbols)
    
    #管理员权限
    def update_symbol_map(self,**domain_map):
        for domain,symbols in domain_map.items():
            self.symbol_map.update_symbols(domain, symbols)


    def assign_by_length(self, node_id, node_domain, length):
        domain = self.node_map.get_node(node_id) or self.node_map.set_node(node_id, node_domain)
        if self.task_map.get_task(node_id) != []:
            node_task = self.task_map.pop_node_task(node_id)
            self.symbol_map.add_symbol(domain, node_task)
        self.node_map.set_node(node_id, node_domain)
        tasks = self.symbol_map.take_orderly_domain_symbol(node_domain,length=length)
        self.task_map.add_task(node_id,tasks)
        return tasks


    def assign_by_list(self, node_id, node_domain,task_list):
        domain = self.node_map.get_node(node_id) or self.node_map.set_node(node_id, node_domain)
        if self.task_map.get_task(node_id) != []:
            node_task = self.task_map.pop_node_task(node_id)
            self.symbol_map.add_symbol(domain, node_task)
        self.node_map.set_node(node_id, node_domain)
        tasks = self.symbol_map.take_given_domain_symbol(node_domain,task_list=task_list)
        self.task_map.add_task(node_id,tasks)
        return tasks



symbol_task_pool = SymbolTaskPool()
# symbol_task_pool.symbol_map.update_symbols("sz",["0",'3','5','19','77','32','14','66','83','a1','33'])
# symbol_task_pool.symbol_map.add_symbol("sz","aa")

# symbol_task_pool.symbol_map.add_symbol("sz",["bb","cc"])
# symbol_task_pool.assign_by_length("a",'sz',3)
# symbol_task_pool.assign_by_list("b","sz",["34","32","12"])
# import pdb
# pdb.set_trace()
# {'task_map': {'a': ['0', '3', '5']},
#  'symbol_map': {'sz': ['19',
#    '77',
#    '32',
#    '14',
#    '66',
#    '83',
#    'a1',
#    '33',
#    'aa',
#    'bb',
#    'cc']}}



@app.task
def update_symbols(**domain_map):
    try:
        symbol_task_pool.update_symbol_map(**domain_map)
        return symbol_task_pool.symbol_map, None  
    except Exception as e:
        return '' , e

@app.task
def get_symbol_list_by_length(node_id, node_domain, length):
    try:
        symbol_list = symbol_task_pool.assign_by_length(node_id, node_domain, length)
        return symbol_list, None
    except Exception as e:
        # return symbol_task_pool,str(e)
        return '' , str(e)
    
@app.task
def get_symbol_list_by_list(node_id, node_domain, task_list):
    try:
        symbol_list = symbol_task_pool.assign_by_list(node_id, node_domain, task_list)
        return symbol_list, None
    except Exception as e:
        # return symbol_task_pool,str(e)
        return '' , str(e)


# node_id_to_symbol_pool = dict()

# @app.task
# def add_node(node_id, initiated=False)->tuple:
#     if initiated:
#         node_id_to_symbol_pool[node_id] = []
#         return True, ''
#     else:
#         if node_id_to_symbol_pool[node_id]:
#             return False, f'trading node_id_to_symbol_pool early has a node:{node_id}'
#         node_id_to_symbol_pool[node_id] = []
#     return True, ''


# @app.task
# def del_node(node_id, initiated=True)->tuple:
#     if initiated:
#         node_id_to_symbol_pool[node_id] = []
#         return True, ''
#     else:
#         if node_id_to_symbol_pool[node_id]:
#             return False, f'trading node_id_to_symbol_pool early has a node:{node_id}'
#         node_id_to_symbol_pool[node_id] = []
#     return True, ''


# @app.task
# def clean_idle_node()->list:
#     cleaned = []
#     for node_id, task in list(node_id_to_symbol_pool.items()):
#         if not task:
#             cleaned.append(node_id)
#             del node_id_to_symbol_pool[node_id]
#     if cleaned:
#         return cleaned
#     else:
#         return []
    

# @app.task
# def update_task(node_id, symbol)->tuple:
#     if node_id in node_id_to_symbol_pool:
#         if symbol in node_id_to_symbol_pool[node_id]:
#             return  True, f'trading node_id_to_symbol_pool had {symbol} early in a node:{node_id}'
#         else:
#             node_id_to_symbol_pool[node_id].append(symbol)
#         return True, ''
#     else:
#         return None, f'trading node_id_to_symbol_pool does not have a node:{node_id}'

# @app.task
# def get_node_tasks(node_id):
#     if node_id in node_id_to_symbol_pool:
#         task = node_id_to_symbol_pool.get(node_id,[])
#     return task

# @app.task
# def get_all_task()->list:
#     all_task = []
#     for value in node_id_to_symbol_pool.values():
#         all_task.extend(value)
#     return all_task
    



