import asyncio
import os
from typing import Dict, List, Tuple

from trader import const, local, logger, config
from trader.exception import DataIOError
from trader.heartbeat import looper
from trader.assets.historical import SingleNodeAccount, TasksAccount
from trader.utils.tasks_function import \
    get_task_symbols_with_length, \
    get_tasks_symbol_list, \
    update_task_symbols

def init_project() -> None:
    #从文件中获取symbol
    try:
        project_data_dir = f'{const.DATA_DIR}{os.sep}{local.node_domain}'
        project_data_dir_files = os.listdir(project_data_dir)
        if project_data_dir_files == []:
            raise DataIOError(f'{project_data_dir} is empty directory')
        for filename in project_data_dir_files:
            file_name_split = filename.split('.')
            symbol, tag, fmt = file_name_split
            if (len(file_name_split) == 3 and tag[0].isalpha() and fmt == "csv" )  == False:
                raise DataIOError(f'{filename} is not a suitable csv file')
            local.project_symbol_map[f'{tag}{symbol}'] = filename
            if not config.update_tasks_domain:
                continue
            local.all_tasks_symbol.append(f'{tag}{symbol}')
    except Exception as e:
        logger.error(e.__repr__())
        exit()

def get_historical_config() -> Dict:
    historical_config = config.historical_config or {}
    historical_config.setdefault("histoical_account_transfer_fee",0)
    historical_config.setdefault("histoical_account_total_asset",1000000)
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
    config.update(temporary=False,tasks_symbols=symbol_list)
    if symbol_list == []:
        logger.error("can get any symbol to list, have not set tasks_symbols or update_local_symbols in config?")
        exit()
    return symbol_list


def update_local_symbols(update: bool, is_new: bool) -> None:
    logger.debug(f'update_local_symbols paramater:  {local.node_domain}:{local.all_tasks_symbol}')
    if update:
        success, err = update_task_symbols(domain_name=local.node_domain, task_symbols=local.all_tasks_symbol, is_new=is_new)
        if success:
            logger.debug(f'update_task_symbols return :{success}')
        else:
            logger.error(err)
            exit()

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

# 
def run_strategy( Strategy,*args, **kwargs ) -> None:
    """
    Example:
    class MyStrategy(HistoricalStrategy):
        index_name="trade_time"
        ohlcv_columns=['open', 'high', 'low', 'close', 'vol']

    """
    if not config.make_data:
        init_project()



    async def run( strategy , **kwargs):
        await asyncio.sleep(0)
        strategy.data_flows.update()
        strategy.update()
        strategy.start()
        if strategy.wc.pace == 0:

            import pdb
            pdb.set_trace() 
        
        #不做修改
        if strategy.data_flows.slided_end:
            try:
                strategy.positions.settlement_all_symbol()
                strategy.update()
                strategy.end()
                looper.stop()
            except Exception as e:
                logger.error(e)
                exit()
        
    #策略内定义优先
    strategy_heartbeat_config = get_strategy_heartbeat_config()

    index_name = getattr(Strategy,"index_name", None) or \
        config.setdefault("strategy_index_name","trader_name")

    ohlcv_columns = get_custom_columns(Strategy)

    strategy = Strategy(*args, **kwargs)

    #trading和historical通用的属性都在这里定义
    if strategy.model == "historical":
        #idea: check strategy healty here
        #历史数据使用长度
        #config historical_config
        historical_config = get_historical_config()
        # import pdb
        # pdb.set_trace()
        total_asset = getattr(strategy,"histoical_account_total_asset", None) \
            or  historical_config.get("histoical_account_total_asset")
        transfer_fee = getattr(Strategy,"histoical_account_transfer_fee", None) \
            or historical_config.get("histoical_account_transfer_fee")

        histories_length = getattr(strategy,"histories_length", None) or \
            historical_config.setdefault("histories_length",20000)
    
        config.update(temporary=False,historical_config=historical_config)
 
        #
        if config.node_stand_alone:
            is_new = True
            symbol_list = config.tasks_symbols
            account = SingleNodeAccount(total_asset=total_asset,transfer_fee=transfer_fee)  
        else:
            if config.update_tasks_domain:
                update, is_new = get_update_param(update_symbols_param=config.update_tasks_domain)
                if update == None:
                    logger.error(f'update_local_symbols paramater type error: {config.update_tasks_domain} ')
                    exit()
                else:
                    update_local_symbols(update=update, is_new=is_new)
            # logger.debug()
                if is_new == True:
                    account = TasksAccount.init_account(domain=local.node_domain, total_asset=total_asset, transfer_fee=transfer_fee)
                else:
                    account = TasksAccount.load_account(domain=local.node_domain)
            else:
                 is_new = False
                 account = TasksAccount.load_account(domain=local.node_domain)
            symbol_list = get_task_symbols(local.node_id, node_domain=local.node_domain)
        if account.prepared:
            logger.info(f"account {account.name} init success.")    
        else:
            logger.info(f"account {account.name} init failed.")  

        strategy.before_start_define(
            column_only_close = config.column_only_close,
            symbol_list       = symbol_list,
            is_new = is_new,
            keep_window = config.keep_dataflow_window
        )
        
        strategy.init_data_flows(
            histories_length,
            ohlcv_columns,
            index_name,
            config.keep_dataflow_window
        )
        #config.node_stand_alone 决定使用哪个account 对象
        strategy.init_asset(
            account,
            **historical_config["historical_order"]
        )

    else:
        #real trading
        import pdb
        pdb.set_trace()

    strategy.init_symbol_objects()
    # config.update(False,update_tasks_domain=False) 
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





