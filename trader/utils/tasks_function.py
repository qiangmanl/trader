
from trader.amqp_server import tasks
# from trader.assets import Order

def get_domain(domain_name):
    domain, err = tasks.get_domain.delay(domain_name).get()
    if domain:
        return domain, ''
    else:
        # logger.error(err)
        return None , err

def create_tasks_symbols(domain_name, task_symbols):
    # def update_task_symbols(domain_name, task_symbols ,is_new=False):
    """
        config set update_local_symbols will call this function
    """
    success, err = tasks.update_pool_symbols.delay(domain_name, task_symbols).get()
    if success:
        return success, ''
    else:
        # logger.error(err)
        return None , err

def get_tasks_symbol_list(node_id, node_domain, symbol_list):
    success, err = tasks.get_task_with_list.delay(node_id, node_domain, symbol_list).get()
    if success:
        # logger.debug(f'get_tasks_symbol_list success:{success}')
        return success, ''
    else:
        # logger.error(err)
        return [] ,err

def get_task_symbols_with_length(node_id, node_domain, length):
    success, err = tasks.get_task_with_length.delay(node_id, node_domain, length).get()
    if success:
        # logger.debug(f'get_task_with_length success:{success}')
        return success, ''
    else:
        # logger.error(err)
        return [] , err
    
def domain_get_symbol_info(symbol: str) ->dict:
    success, err = tasks.get_domain_symbol.delay(symbol).get()
    if success:
        # logger.debug(f'get_task_with_length success:{success}')
        return success, ''
    else:
        # logger.error(err)
        return [] , err

