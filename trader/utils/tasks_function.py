from trader.amqp_server import tasks

def update_task_symbols(domain_name, task_symbols ,is_new=False):
    """
        config set update_local_symbols will call this function
    """
    if is_new == False:
        success, err = tasks.update_pool_symbols.delay(domain_name, task_symbols).get()
    else:
        success, err = tasks.create_pool_symbols.delay(domain_name, task_symbols).get()
    if success:
        return success, ''
        # logger.debug(f"update_local_symbols :{success}")
        # config.update(False,update_local_symbols=False) 
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



def account_load(domain):
    success, err = tasks.get_tasks_account.delay(domain).get()
    if success:
        return success, ''
    else:
        # logger.error(err)
        return '' , err

def account_init(domain, total_asset, transfer_fee=0):
    success, err = tasks.init_account.delay(domain, total_asset, transfer_fee).get()
    if success:
        return success, ''
    else:
        # logger.error(err)
        return '' , err
    

def open_account_symbol(domain, amount, symbol):
    #返回账号余额
    success, err = tasks.open_account_symbol.delay(domain, amount=amount, symbol=symbol).get()
    if err:
        return None, err
    else:
        # logger.error(err)
        return success , err

def account_transfer_to(domain, amount, symbol):
    #返回账号余额
    success, err = tasks.account_transfer_to.delay(domain, amount=amount, symbol=symbol).get()
    if err:
        return None, err
    else:
        # logger.error(err)
        return success , err

def account_transfer_from(domain, amount, symbol):
    #返回账号余额
    success, err = tasks.account_transfer_from.delay(domain, amount=amount, symbol=symbol).get()
    if err:
        return None, err
    else:
        # logger.error(err)
        return success , err
   
def get_symbol_account_state(domain, symbol):
    state, err = tasks.domain_get_symbol_attr.delay(domain, symbol, attr="account_open").get()
    if err:
        return None, err
    else:
        # logger.error(err)
        return state, ''
  

def account_get_symbol_asset(domain, symbol, attr="balance"):
    success, err = tasks.domain_get_symbol_attr.delay(domain, symbol, attr).get()
    if err:
        return None, err
    else:
        # logger.error(err)
        return success , err
    

def account_get_total_asset():
    success, err = tasks.account_get_total_asset.delay().get()
    if err:
        return None, err
    else:
        # logger.error(err)
        return success , err