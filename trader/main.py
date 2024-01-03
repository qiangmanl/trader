import asyncio
import os
from trader.amqp_server import tasks
from trader.const import ADMIN_NODE_ID 
from trader import local, logger, config
from trader.const import ROW_DATA_DIR
from trader.heartbeat import looper

def gen_all_symbol()->bool:
    #从文件中获取symbol
    files = os.listdir(ROW_DATA_DIR)
    for file in files:
        symbol, domain, _ = file.split('.') 
        local.symbol_file_map[symbol] = file
        if not config.update_tasks_symbols:
            continue
        if local.symbol_domain_map.get(domain) == None:
            local.symbol_domain_map[domain] = []
        local.symbol_domain_map[domain].append(symbol)

def update_tasks_symbols(domain_map):

    if local.node_id == ADMIN_NODE_ID:
        success, err = tasks.update_symbols.delay(**domain_map).get()
        if success:
            logger.debug(f"update_tasks_symbols :{success}")
            config.update(False,update_tasks_symbols=False) 
        else:
            logger.error(err)
            exit()

def get_task_symbols_by_list(node_id, node_domain, symbol_list):
    success, err = tasks.get_symbol_list_by_list.delay(node_id, node_domain, symbol_list).get()
    if success:
        logger.debug(f'get_task_symbols_by_list success:{success}')
        return success
    else:
        logger.error(err)
        return []

def get_task_symbols_by_length(node_id, node_domain, length):
    success, err = tasks.get_symbol_list_by_length.delay(node_id, node_domain, length).get()
    if success:
        logger.debug(f'get_task_symbols_by_length success:{success}')
        return success
    else:
        logger.error(err)
        return []

def get_symbol_list(node_id, node_domain):
    if config.symbol_length:
        symbol_list = get_task_symbols_by_length(node_id, node_domain, config.symbol_length)
    elif config.symbol_list:
        symbol_list = get_task_symbols_by_list(node_id, node_domain, config.symbol_list)
    else:
        symbol_list = []
    config.update(temporary=False,symbol_list=symbol_list)
    if symbol_list == []:
        logger.error("can get any symbol to list, set admin or symbol_length or update_tasks_symbols?")
        exit()
    return symbol_list


def get_strategy_heartbeat_config()->tuple:
    strategy_heartbeat_config = config.setdefault("strategy_heartbeat", {})
    config.strategy_heartbeat.setdefault("print_interval",60)
    config.strategy_heartbeat.setdefault("interval",0.1)
    config.strategy_heartbeat.setdefault("heartname","strategy")
    return strategy_heartbeat_config

def translate_small_rate(word):
    if isinstance(word,(int,float)) and word < 1:
        return word
    elif isinstance(word,str):
        if word[-1] == "%":
            word = float(word[:-1])/100
            return word
        else:
            try:
                word = float(word)
                if word < 0:
                    return word
                else:
                    return
            except ValueError:
               return
            finally:
                return
    else:
        return


def translate_balance(balance):
    if isinstance(balance,(int,float)):
        return balance
    else:
        try:
            balance = float(balance) 
            return balance
        except ValueError:
            logger.error("translate_balance error")


#策略初始化配置
def get_historical_order_config()->tuple:
    """default 先只配置简单的默认配置， 适合例如在同一池内 统一做空或做多的symbol，
    统一手续费，统一回测资金，若需要自定义需在策略中按token定义
    @param direction (short | long) == (-1 | 1)  
    """
    default_config = config.historical_order.get("default",{})
    #current_period_close:  结算参考价格是当天的close
    default_config.setdefault("price_reference", "current_period_close")  
    default_config.setdefault("balance",1000000)
    default_config.setdefault("commission",0.003)
    default_config.setdefault("leverage",1)
    default_config.setdefault("direction",1)
    
    config.historical_order["default"] = default_config
    return config.historical_order

def run_strategy(Strategy,*args, **kwargs):
    """
    Example:
    class MyStrategy(HistoricalStrategy):
        index_name="trade_time"
        strategy_columns=['open', 'high', 'low', 'close', 'vol']

    """
    async def run( strategy, **kwargs):
        await asyncio.sleep(0)
        strategy.data_flows.update()
        strategy.update()
        strategy.start()
        #不做修改
        if strategy.data_flows.slided_end:
            try:
                strategy.end()
                looper.stop()
            except Exception as e:
                logger.error("e")
                exit()

    gen_all_symbol()
    if config.update_tasks_symbols:
        update_tasks_symbols(local.symbol_domain_map)
    symbol_list = get_symbol_list(local.node_id, node_domain=local.node_domain)
    #策略内定义优先

    index_name = getattr(Strategy,"index_name", None) or \
        config.setdefault("strategy_index_name","trader_name")
    
    strategy_columns    = getattr(Strategy,"strategy_columns", None) \
        or config.setdefault("strategy_columns",['open', 'high', 'low', 'close', 'vol'])

    strategy_price_reference = getattr(Strategy,"strategy_price_reference", None) \
        or config.setdefault("strategy_price_reference","current_period_close")
    


    if Strategy.model == "historical":
        #历史数据使用长度
        histories_length = getattr(Strategy,"histories_length", None) or \
            config.setdefault("histories_length",20000)
        logger.info(f"strategy initiated, node {local.node_id} start into historical model.")
        order_config = get_historical_order_config()
        strategy = Strategy(*args, **kwargs)
        strategy.init_history(
            index_name=index_name, 
            strategy_columns=strategy_columns,
            symbol_list=symbol_list,
            histories_length=histories_length,
            price_reference=strategy_price_reference,
            order_config = order_config
        )

    #         #注册心跳

    else:
        #real trading
        import pdb
        pdb.set_trace()

    strategy.init_symbol_property(strategy_columns)
    #在策略执行前定义
    if getattr(strategy,"init_custom",None):
        strategy.init_custom(*args, **kwargs)
    strategy_heartbeat_config = get_strategy_heartbeat_config()
    looper.register(
        run,
        strategy=strategy,
        heartname=strategy_heartbeat_config["heartname"],
        interval=strategy_heartbeat_config["interval"],
        print_interval=strategy_heartbeat_config["print_interval"]
    )
    looper.start()





