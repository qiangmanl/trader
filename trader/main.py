import asyncio
import os

from trader import local, logger, config
from trader.heartbeat import looper
from trader.utils.tasks_function import \
    get_tasks_symbol_by_catch, \
    get_tasks_symbol_by_list, \
    update_tasks_symbols

def get_strategy_heartbeat_config()->tuple:
    strategy_heartbeat_config = config.setdefault("strategy_heartbeat", {})
    config.strategy_heartbeat.setdefault("print_interval",60)
    config.strategy_heartbeat.setdefault("interval",0.1)
    config.strategy_heartbeat.setdefault("heartname","strategy")
    return strategy_heartbeat_config

#策略初始化配置
def get_historical_order_config()->tuple:
    """default 先只配置简单的默认配置， 适合例如在同一池内 统一做空或做多的symbol，
    统一手续费，统一回测资金，若需要自定义需在策略中按token定义
    @param direction (short | long) == (-1 | 1)  
    """
    default_config = config.historical_order.get("default",{})
    #current_period_close:  结算参考价格是当天的close
    #开仓的金额会从总账里扣除，所以所有的标的余额加起来不能超过总账,默认是平均分配，也可以按标的设置
    default_config.setdefault("balance",10000)
    default_config.setdefault("commission",0.003)
    default_config.setdefault("leverage",1)
    default_config.setdefault("direction",1)
    config.historical_order["default"] = default_config
    return config.historical_order

def get_task_symbols(node_id, node_domain)->list:
    if config.catch_new_tasks:
        symbol_list, err = get_tasks_symbol_by_catch(node_id, node_domain, config.catch_new_tasks)
        if symbol_list:
            logger.debug(f'catch_new_tasks return:{symbol_list}')
            config.remove("catch_new_tasks",temporary=False)
        else:
            logger.error(f'catch_new_tasks error:{err}')

    elif config.tasks_symbols:
        symbol_list, err = get_tasks_symbol_by_list(node_id, node_domain, config.tasks_symbols)
        if symbol_list:
            logger.debug(f'get tasks_symbols return:{symbol_list}')
        else:
            logger.error(f'get tasks_symbols error:{err}')

    else:
        symbol_list = []
    config.update(temporary=False,tasks_symbols=symbol_list)
    if symbol_list == []:
        logger.error("can get any symbol to list, have not set tasks_symbols or update_local_symbols in config?")
        exit()
    return symbol_list

def update_local_symbols():
    logger.debug(f'update_tasks_symbols  local.symbol_domain_map:{local.symbol_domain_map}')
    success,err = update_tasks_symbols(local.symbol_domain_map)
    if success:
        logger.debug(f'update_tasks_symbols return :{success}')
        config.update(False,update_local_symbols=False) 
    else:
        logger.error(err)
        exit()
        
def run_strategy( Strategy,*args, **kwargs ) -> None:
    """
    Example:
    class MyStrategy(HistoricalStrategy):
        index_name="trade_time"
        strategy_columns=['open', 'high', 'low', 'close', 'vol']

    """
    async def run( strategy , **kwargs):
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

    if config.update_local_symbols:
        update_local_symbols()

    if config.node_stand_alone:
        symbol_list = config.tasks_symbols
    else:
        symbol_list = get_task_symbols(local.node_id, node_domain=local.node_domain)
    #策略内定义优先
    strategy_heartbeat_config = get_strategy_heartbeat_config()

    index_name = getattr(Strategy,"index_name", None) or \
        config.setdefault("strategy_index_name","trader_name")
    
    strategy_columns    = getattr(Strategy,"strategy_columns", None) \
        or config.setdefault("strategy_columns",['open', 'high', 'low', 'close', 'vol'])


    strategy_price_reference = getattr(Strategy,"strategy_price_reference", None) \
        or config.setdefault("strategy_price_reference","current_period_close")
    
    strategy = Strategy(*args, **kwargs)

    #trading和historical通用的属性都在这里定义
    strategy.before_init_define(
        index_name      = index_name, 
        strategy_columns= strategy_columns,
        symbol_list     = symbol_list,
        price_reference = strategy_price_reference

    )

    if strategy.model == "historical":
        #idea: check strategy healty here

        #历史数据使用长度
        histories_length = getattr(strategy,"histories_length", None) or \
            config.setdefault("histories_length",20000)
        logger.info(f"strategy initiated, node {local.node_id} start into historical model.")
        order_config = get_historical_order_config()
        
        strategy.init_strategy(
            histories_length,
            order_config = order_config
        )

    else:
        #real trading
        import pdb
        pdb.set_trace()

    strategy.init_symbol_objects()
    #在策略执行前定义
    if getattr(strategy,"init_custom",None):
        strategy.init_custom(*args, **kwargs)

     #注册心跳
    looper.register(
        run,
        strategy=strategy,
        heartname=strategy_heartbeat_config["heartname"],
        interval=strategy_heartbeat_config["interval"],
        print_interval=strategy_heartbeat_config["print_interval"]
    )
    looper.start()





