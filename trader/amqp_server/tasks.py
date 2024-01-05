from celery import Celery
from trader import config,logger
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

class LeisureTaskMap(DictBase):

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


class NodeTaskMap(DictBase):
    
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
        return self.pop(node_id)

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


class NodeMap(DictBase):

    def get_node(self,node_id):
        return self.__getattr__(node_id, None)
           
    def set_node(self, node_id, domain):
        self.__setattr__(node_id, domain)
        return domain

class SymbolTaskPool(DictBase):
    """
    Maps:
        {
            'node_task_map': {
                $node: [$task,...]
            },
            'leisure_tasks': {
                'domain': [$task,...]
            }
        }
    Example:
        
        symbol_task_pool.leisure_tasks.update_symbols("$domain",[$task,...])
        symbol_task_pool.leisure_tasks.add_symbol("$domain",$task)
        symbol_task_pool.leisure_tasks.add_symbol("$domain",[$task,...])
        symbol_task_pool.assign_by_length("$node",'$domain',$length)
        symbol_task_pool.assign_by_list("$node","$domain",[$task,...])
                
    """
    def __init__(self) -> None:
        self.node_task_map = NodeTaskMap()
        self.leisure_tasks = LeisureTaskMap()
        self.node_map = NodeMap()

    def all_pool_task(self):
        return self.node_task_map.task_on_nodes.extend(self.leisure_tasks.all_symbols)
    
    #管理员权限
    def update_leisure_tasks(self,**domain_map):
        for domain,symbols in domain_map.items():
            self.leisure_tasks.update_symbols(domain, symbols)

    def assign_by_length(self, node_id, node_domain, length) -> list:
        domain = self.node_map.get_node(node_id) or self.node_map.set_node(node_id, node_domain)
        if self.node_task_map.get_task(node_id) != []:
            node_task = self.node_task_map.pop_node_task(node_id)
            self.leisure_tasks.add_symbol(domain, node_task)
        self.node_map.set_node(node_id, node_domain)
        tasks = self.leisure_tasks.take_orderly_domain_symbol(node_domain,length=length)
        self.node_task_map.add_task(node_id,tasks)
        return tasks

    def assign_by_list(self, node_id, node_domain,task_list) -> list:
        domain = self.node_map.get_node(node_id) or self.node_map.set_node(node_id, node_domain)
        if self.node_task_map.get_task(node_id) != []:
            node_task = self.node_task_map.pop_node_task(node_id)
            self.leisure_tasks.add_symbol(domain, node_task)
        self.node_map.set_node(node_id, node_domain)
        tasks = self.leisure_tasks.take_given_domain_symbol(node_domain,task_list=task_list)
        self.node_task_map.add_task(node_id,tasks)
        return tasks

symbol_task_pool = SymbolTaskPool()

@app.task
def update_symbols(**domain_map):
    try:
        symbol_task_pool.update_leisure_tasks(**domain_map)
        return symbol_task_pool.leisure_tasks, None  
    except Exception as e:
        return '' , e

@app.task
def get_symbol_list_by_length(node_id, node_domain, length):
    try:
        symbol_list = symbol_task_pool.assign_by_length(node_id, node_domain, length)
        logger.warning(symbol_task_pool)
        return symbol_list, None
    except Exception as e:
        # return symbol_task_pool,str(e)
        logger.warning(e.__repr__())
        return '' , str(e)
    
@app.task
def get_symbol_list_by_list(node_id, node_domain, task_list):
    try:
        symbol_list = symbol_task_pool.assign_by_list(node_id, node_domain, task_list)
        logger.warning(symbol_task_pool)
        return symbol_list, None
    except Exception as e:
        # return symbol_task_pool,str(e)
        logger.warning(e.__repr__())
        return '' , str(e)




