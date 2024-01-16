import os
import pandas as pd
from trader.exception import LocalAccountError
from trader.utils.tasks_function import  get_symbol_account_state, get_symbol_init_position, open_account_symbol
from trader.utils.tools import str_pd_datetime
from .base import StrategyBase, SymbolsProperty, WindowPointCtrol
from trader import logger, local
from trader.dataflows import HistoricalDataFlows
from trader.assets import Order, OrderBookPattern
from trader.assets.historical import HistoricalPosition, HistoricalPositionMap


class HistoricalStrategy(StrategyBase, SymbolsProperty):
    """
    """
    model = "historical"
    #策略运行时初始化一次，所有策略需要的配置都通过init传递


    def csv_to_history(self, file, ohlcv_columns, index_name)->bool:
        df = pd.read_csv(f'{local.domain_dir}{os.sep}{file}',index_col=index_name,parse_dates=[index_name])

        df.index.rename(self.index_name,inplace=True)
        #限定ohlcv5个column，名称由config 和策略定义,如果不存在列名报错
        try:
            df = df.loc[:, ohlcv_columns]
        except KeyError:
            logger.error(f'df do not have {ohlcv_columns} in columns')
            exit()
        if self.column_only_close:
            df.rename(columns={ohlcv_columns[0]: self.ohlcv_columns[3]},inplace=True)
        else:
            df.rename(
                columns={
                    ohlcv_columns[0]: self.ohlcv_columns[0],
                    ohlcv_columns[1]: self.ohlcv_columns[1],
                    ohlcv_columns[2]: self.ohlcv_columns[2],
                    ohlcv_columns[3]: self.ohlcv_columns[3],
                    ohlcv_columns[4]: self.ohlcv_columns[4]
                },
                inplace=True
            )
        return df

    def before_start_define(
            self,
            column_only_close : bool,
            symbol_list       :list,
            is_new : bool,
            keep_window : int 
        ):
        self.index_name = 'trade_time'
        self.ohlcv_columns = ["open","high","low","close","vol"]
        #new_project_mode 决定初始化数据是否从tasks获取, is_new = config.update_tasks_domain=="new"
        #一但strategy.wpc.pace == 0且本地开始上传symbol数据到tasks，new将被重置成false
        self.new_project_mode = is_new
        self.wpc = WindowPointCtrol(keep_window)
        self.column_only_close = column_only_close
        self.symbol_objects = symbol_list
        self.trading_signals = dict()


    def init_data_flows(self,
            histories_length,
            ohlcv_columns,
            index_name,
            keep_window
        )->bool | None:
        """
            history file name:
                $symbol.$institution.csv
        """

        #wait check index_name 
        #wait check ohlcv_columns
        #config symbol_list有特定的执行任务列表
        self.init_histories_length = histories_length
        try:
            if self.new_project_mode == True:
                self.histories_length = self.init_histories_length
                histories = []
                for symbol in self.symbol_objects:
                    file_name = local.project_symbol_map[symbol]
                    history = self.csv_to_history(file_name, ohlcv_columns, index_name)
                    histories.append(history)
                histories_data = pd.concat(histories, axis=1, keys=self.symbol_objects)
            else:
                import pdb
                pdb.set_trace()
                # self.histories_length = 
                # histories_data = 
    
            self.data_flows = HistoricalDataFlows(
                histories_data,
                length=self.histories_length,
                keep_window=keep_window
            )
        except Exception as e:
            # import pdb
            # pdb.set_trace()
            logger.error(e.__repr__())
            exit()          

    def _reload_position(self):
        
        for symbol in self.symbol_objects:
            position, err = get_symbol_init_position(local.node_domain, symbol)
            if err:
                logger.error(err)
                exit()
            balance = position.get("balance")
            leverage = position.get("leverage")
            long_fee = position.get("long_fee")
            short_fee = position.get("short_fee")
            self.positions.add_position(symbol,
                HistoricalPosition(symbol, balance, leverage, long_fee, short_fee)
            )
            # self.positions.add_position(symbol,
            #     HistoricalPosition(symbol, balance, leverage, long_fee, short_fee)
            # )

    def _init_position(self, order_config):
        default_order_config = order_config["default"]
        for symbol in self.symbol_objects:
            # if orderconfig.get(symbol):
            # 如果symbol有了第一次获取asset资金来源则跳过， 只有通过执行open_account_symbol 才会满足symbol_account_is_open
            symbol_account_is_open, _ = get_symbol_account_state(domain=local.node_domain, symbol=symbol)
            if symbol_account_is_open == True:
                continue
            if order_config.get(symbol,None) == None:
                symbol_order_config = order_config.setdefault(symbol, default_order_config)
            else:
                symbol_order_config = order_config.get(symbol)
            logger.debug(f'symbol {symbol} order config : {symbol_order_config}')
            amount = symbol_order_config.setdefault("balance", default_order_config["balance"])
            balance, err = open_account_symbol(domain=local.node_domain, amount=amount, symbol=symbol)
            long_fee = symbol_order_config.setdefault("long_fee", default_order_config["long_fee"])
            short_fee = symbol_order_config.setdefault("short_fee", default_order_config["short_fee"])
            leverage = symbol_order_config.setdefault("leverage", default_order_config["leverage"])
            try:
                if balance == None:
                    raise LocalAccountError(f"account set balance number error {err}")
                if balance <= 0:
                    raise LocalAccountError(f"account set balance number too small {err}")
                if balance < amount:
                    raise LocalAccountError("balance small than account preseted")
                if long_fee < 0 or long_fee >= 1:
                    raise LocalAccountError("account set long_fee number error")
                if short_fee < 0 or  short_fee >= 1:
                    raise LocalAccountError("account set short_fee number error")
                if leverage < 1  or isinstance(leverage, int)==False:
                    raise LocalAccountError("account set leverage  error")
            except Exception as e:
                logger.error(f'error from init_asset:{e.__repr__()}')
                logger.error(f'error from init_asset:account set symbol {symbol} balance')
                exit()
            self.positions.add_position(symbol,
                HistoricalPosition(symbol, balance, leverage, long_fee, short_fee)
            )
        self.account.reload()

    def init_asset(self, 
            account,
            **order_config
            ):
        self.account = account
        self.positions = HistoricalPositionMap()

        if self.new_project_mode:
            self._init_position(order_config)
        else:
            self._reload_position()
        return True

    def get_position(self,symbol):
        return self.positions.__getattr__(symbol,{})

    @property
    def histories_index(self):
        return self.data_flows.histories_index
    
    @property
    def domain(self):
        return local.node_domain

    def get_trading_quota(self, symbol:str):
        price = self.get_previous_history(symbol)["close"]
        return price

    def get_current_ohlc(self,symbol):
        ohlc =  getattr(self,symbol).property_dict["ohlc"]
        return ohlc

    def _update_orders(self):
        """
            此时处理的订单价格是该symbol 前period的close 或者是当前period的open
        """
        trade_time=self.data_flows.previous_datetime
        trading_signals = self.trading_signals.pop(trade_time,[])
        if len(trading_signals) > 0:
            for order in trading_signals:
                price = self.get_trading_quota(order.symbol)
                #type price is numpy float64
                if ( price > 0) == False:
                    #此次交易信号作废
                    continue

                position = self.get_position(order.symbol)
                order.set_price(price)
                #回测直接成交
                order.finish_historical_order()
                #更新订单
                #previous_period_close order.price 是上一period close的价格
                position.update_order(order)
        

    def _update_position(self, current_datetime):
        current_datetime = current_datetime
        for symbol in self.symbol_objects:
            position = self.get_position(symbol)
            ohlc = self.get_current_ohlc(symbol)
            position.update_position(ohlc, current_datetime=str_pd_datetime(current_datetime))
            order_row = OrderBookPattern.create(position).orderbook
            self.get_symbol_orderbook(symbol).loc[current_datetime, : ] = order_row
            #nan data  bool(nan) == False
        # import pdb
        # pdb.set_trace()
    
    def update(self)->bool:
        """
        """
        self.update_symbol_object()
        self._update_orders()
        self._update_position(self.data_flows.current_datetime)

    def make_trading_signal(self,tradetime, order):
        # 由于考虑同一时间节点存在多个买入信号，所以trading_signals 使用列表结构
        if self.trading_signals.get(tradetime):
            self.trading_signals[tradetime].append(order)
        else:
            self.trading_signals[tradetime] = []
            self.trading_signals[tradetime].append(order)

    def sell(self, symbol ,qty, islong=True):
        # tradetime_str = tradetime.strftime('%Y-%m-%d %H:%M:%S')
        if symbol in self.symbol_objects:
            tradetime = self.data_flows.current_datetime
            order = Order(symbol=symbol, qty=qty, action="sell", order_type="historical", islong=islong)
            self.make_trading_signal(tradetime, order)
            logger.debug(f'current datetime:{tradetime} make a trading signal for traded at {self.data_flows.next_period_index}')
        else:
            logger.warning(f'symbol:"{symbol}" not on flows symbol {self.symbol_objects}')

    def buy(self, symbol ,qty, islong=True):
        if symbol in self.symbol_objects:
            tradetime = self.data_flows.current_datetime
            order = Order(symbol=symbol, qty=qty, action="buy", order_type="historical", islong=islong)
            self.make_trading_signal(tradetime, order)
            logger.debug(f'current datetime:{tradetime} make a trading signal for traded at {self.data_flows.next_period_index}')
        else:
            logger.warning(f'symbol:"{symbol}" not on flows symbol {self.symbol_objects}')
