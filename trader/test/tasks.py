from typing import List
from trader.amqp_server import tasks
from trader import logger, local
from trader.exception import TasksAccountError
from trader.utils.base import DictBase

def update_task_symbols(domain_name, task_symbols):
    """
        config set update_local_symbols will call this function
    """

    success, err = tasks.update_pool_symbols.delay(domain_name, task_symbols).get()
    if success:
        return success, ''
        # logger.debug(f"update_local_symbols :{success}")
        # config.update(update_local_symbols=False) 
    else:
        # logger.error(err)
        return None , err

def get_tasks_symbol_list(node_id, node_domain, symbol_list):
    logger.debug(symbol_list)
    success, err = tasks.get_task_with_list.delay(node_id, node_domain, symbol_list).get()
    if success:
        # logger.debug(f'get_tasks_symbol_list success:{success}')
        return success, ''
    else:
        # logger.error(err)
        return [] ,err
    
symbol_list= [
    "SZ002212",
    "SH600578",
    "SH601958",
    "SZ002611",
    "SH600073",
    "SZ000029",
    "SZ002197",
    "SZ002038",
    "SH600928",
    "SZ002335",
    "SH601155",
    "SH600572",
    "SZ002080",
    "SZ300627",
    "SH600360"
]

logger.debug(get_tasks_symbol_list (local.node_id, local.node_domain 
, symbol_list))





s  = SymbolTaskPool()
d = s.new_domain(DomainObjects("demain1"))
d.add_symbol("SZ000002")
d.add_symbol("SZ000003")
d.add_symbol("SZ000004")
d.set_node_symbol_working("SZ000002","a")
d.set_node_symbol_working("SZ000003","a")
d.set_node_symbol_working("SZ000004","b")
d.leisure_symbols
d.get_node_working_symbols("b")
d.set_node_symbol_leisure("SZ000002","a")
d.set_node_all_symbol_leisure("a")
d.init_account(100000,0)
d.transfer_to_symbol(300,"SZ000002")
d.transfer_from_symbol(1,"SZ000002")
d.account