import os
from typing import Dict, List, Tuple
from trader import const, local, logger, config
from trader.exception import DataIOError
from trader.heartbeat import looper
from trader.utils.tasks_function import \
    create_tasks_symbols, \
    get_domain, \
    get_task_symbols_with_length, \
    get_tasks_symbol_list \
    

def init_project() -> None:
    #从文件中获取symbol
    try:
        project_data_dir = local.domain_dir 
        project_data_dir_files = os.listdir(project_data_dir)
        if project_data_dir_files == []:
            raise DataIOError(f'{project_data_dir} is empty directory')
        for filename in project_data_dir_files:
            file_name_split = filename.split('.')
            if len(file_name_split) != 3:
                raise DataIOError(f'file {filename} is not a suitable name as symbol.tag.extension     \
                format. remove file and try again')
            symbol, tag, fmt = file_name_split
            if (len(file_name_split) == 3 and tag[0].isalpha() and fmt == "csv" )  == False:
                raise DataIOError(f'{filename} is not a suitable csv file')
            local.project_symbol_map[f'{tag}{symbol}'] = filename
            # if not config.update_tasks_domain:
            #     continue
            local.all_tasks_symbol.append(f'{tag}{symbol}')
    except Exception as e:
        logger.error(e.__repr__())
        exit()

def get_historical_config() -> Dict:
    historical_config = config.historical_config or {}
    logger.info(f"strategy initiated, node {local.node_id} start into historical model.")
    order_config = historical_config.get("historical_order",{})
    default_order_config = order_config.get("default",{})
    default_order_config.setdefault("balance",10000)
    default_order_config.setdefault("long_fee",0.000)
    default_order_config.setdefault("short_fee",0.000)
    default_order_config.setdefault("leverage",1)
    order_config["default"] = default_order_config
    historical_config["historical_order"] = order_config
    return historical_config

def get_strategy_heartbeat_config() -> Tuple[int | float]:
    strategy_heartbeat_config = config.setdefault("strategy_heartbeat", {})
    config.strategy_heartbeat.setdefault("print_interval",60)
    config.strategy_heartbeat.setdefault("interval",0.1)
    config.strategy_heartbeat.setdefault("heartname","strategy")
    return strategy_heartbeat_config


def get_custom_columns(Strategy) -> None | List[str]:
    if config.column_only_close:
        ohlcv_columns    = getattr(Strategy,"ohlcv_columns", None) \
            or config.setdefault("ohlcv_columns",['close'])
        if len(ohlcv_columns) != 1:
            logger.error("ohlcv_columns set column only close model error")
            exit()
    else:
        ohlcv_columns    = getattr(Strategy,"ohlcv_columns", None) \
            or config.setdefault("ohlcv_columns",['open','high', 'low','close', 'vol'])
        if len(ohlcv_columns) != 5:
            logger.error("ohlcv_columns set error")
            exit()
    return ohlcv_columns


def get_task_symbols(node_id, node_domain) -> List[str]:
    if config.catch_new_tasks:
        symbol_list, err = get_task_symbols_with_length(node_id, node_domain, config.catch_new_tasks)
        if symbol_list:
            logger.debug(f'catch_new_tasks return:{symbol_list}')
            config.remove("catch_new_tasks",temporary=False)
            
        else:
            logger.error(f'catch_new_tasks error:{err}')

    elif config.tasks_symbols:

        symbol_list, err = get_tasks_symbol_list(node_id, node_domain, config.tasks_symbols)
        if symbol_list:
            logger.debug(f'get tasks symbols return:{symbol_list}')
        else:
            logger.error(f'get tasks symbols error:{err}')

    else:
        symbol_list = []
    if symbol_list == []:
        logger.error(f'can get any symbol to list. config.catch_new_tasks: {config.catch_new_tasks} \n \
          config.tasks_symbols:{config.tasks_symbols} \
        ')
        exit()
    else:
        config.update(temporary=False,tasks_symbols=symbol_list)    
    return symbol_list


def get_update_param(update_symbols_param : str | int | bool):
    if isinstance(update_symbols_param, str):
        if update_symbols_param.lower() == "new":
            is_new = True
        else:
            is_new = False
        update = True 

    elif isinstance(update_symbols_param, bool) or isinstance(update_symbols_param, int):
        update = bool(update_symbols_param)
        is_new = False
    else:
        return (None, None)
    return update, is_new


def no_domain_or_create():
    domain, _  = get_domain(local.node_domain) 
    if domain == None:
        logger.debug(f'create new domain  {local.node_domain} on tasks')
        create_tasks_symbols(domain_name=local.node_domain, task_symbols=local.all_tasks_symbol)
        return True
    else:
        logger.debug(f'domain  {local.node_domain} early on tasks')
    if config.create_new_domain == True:
        logger.warning(f"domain  {local.node_domain} early on tasks, config create_new_domain turn to false automatically")
    config.update(create_new_domain=False)
    return False


def run_strategy( Strategy,*args, **kwargs ) -> None:
    """
    Example:
    class MyStrategy(HistoricalStrategy):
        index_name="trade_time"
        ohlcv_columns=['open', 'high', 'low', 'close', 'vol']

    """
    if not config.make_data:
        init_project()

        
    #策略内定义优先
    strategy_heartbeat_config = get_strategy_heartbeat_config()

    custom_index_name = getattr(Strategy,"index_name", None) or \
        config.setdefault("strategy_index_name","trader_name")

    custom_ohlcv_columns = get_custom_columns(Strategy)

    strategy = Strategy(*args, **kwargs)

    #trading和historical通用的属性都在这里定义
    if strategy.model == "historical":
        #idea: check strategy healty here
        #历史数据使用长度
        #config historical_config
        historical_config = get_historical_config()

        histories_length = getattr(strategy,"histories_length", None) or \
            historical_config.setdefault("histories_length",20000)
    
        config.update(temporary=False,historical_config=historical_config)
        if config.create_new_domain and not config.node_stand_alone:
            no_domain_or_create()
        if config.node_stand_alone:
            # is_new = True
            logger.debug("strategy use node_stand_alone")
            symbol_list = config.tasks_symbols

        else:
            # if config.update_tasks_domain:
            no_domain_or_create()
            symbol_list = get_task_symbols(local.node_id, node_domain=local.node_domain)
            logger.debug(f'{get_domain(local.node_domain)}') 
        keep_window = config.keep_dataflow_window or 1
        strategy.before_start_define(
            column_only_close = config.column_only_close,
            symbol_list       = symbol_list,
            histories_length=histories_length,
            keep_window = keep_window,
            custom_index_name=custom_index_name,
            custom_ohlcv_columns=custom_ohlcv_columns,
            **historical_config["historical_order"]
        )
        
        #config.node_stand_alone 决定使用哪个account 对象

        strategy.init_symbol_objects()

    else:
        #real trading
        import pdb
        pdb.set_trace()
        # domain_get_trading_signals(local.node_domain) 

    # strategy.init_symbol_objects()
    # config.update(update_tasks_domain=False) 
    #在策略执行前定义

    if getattr(strategy,"init_custom",None):
        strategy.init_custom(*args, **kwargs)
        # 如果自定义还没有ta 则ta使用策略自带的ta
        if getattr(strategy, "ta",None) == None:
            from trader.strategy import TechnicalAnalyses
            strategy.create_ta(TechnicalAnalyses)
            
     #注册心跳
    looper.register(
        strategy.run,
        strategy=strategy,
        heartname=strategy_heartbeat_config["heartname"],
        interval=strategy_heartbeat_config["interval"],
        print_interval=strategy_heartbeat_config["print_interval"]
    )
    looper.start()





