from trader.amqp_server import tasks

def update_tasks_symbols(domain_map):
    """
        config set update_local_symbols will call this function
    """
    success, err = tasks.update_symbols.delay(**domain_map).get()
    if success:
        return success, ''
        # logger.debug(f"update_local_symbols :{success}")
        # config.update(False,update_local_symbols=False) 
    else:
        # logger.error(err)
        return {} , err

def get_tasks_symbol_by_list(node_id, node_domain, symbol_list):
    success, err = tasks.get_symbol_list_by_list.delay(node_id, node_domain, symbol_list).get()
    if success:
        # logger.debug(f'get_tasks_symbol_by_list success:{success}')
        return success, ''
    else:
        # logger.error(err)
        return [] ,err

def get_tasks_symbol_by_catch(node_id, node_domain, length):
    success, err = tasks.get_symbol_list_by_length.delay(node_id, node_domain, length).get()
    if success:
        # logger.debug(f'get_tasks_symbol_by_catch success:{success}')
        return success, ''
    else:
        # logger.error(err)
        return [] , err