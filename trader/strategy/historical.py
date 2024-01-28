import asyncio
import os
from typing import List
import pandas as pd
from trader.exception import  StrategyInitError, StrategyRunError
from trader.heartbeat import looper
# from trader.utils.tasks_function import  get_symbol_account_state, get_symbol_init_position, open_account_symbol
from trader.utils.tools import str_pd_datetime
from trader import logger, local
from trader.dataflows import HistoricalDataFlows
from trader.assets import Order, OrderBookPattern
from trader.assets.historical import HistoricalPosition, HistoricalPositionMap
from .base import StrategyBase, WindowPointCtrol
from .symbols import DomainSymbols


class HistoricalStrategy(StrategyBase):
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
            # is_new : bool,
            keep_window : int,
            histories_length:int,
            custom_ohlcv_columns :List[str],
            custom_index_name : str,
            **order_config
        ):
        self.has_signal = False
        self.index_name = 'trade_time'
        self.ohlcv_columns = ["open","high","low","close","vol"]
        #new_project_mode 决定初始化数据是否从tasks获取, is_new = config.update_tasks_domain=="new"
        #一但strategy.wpc.pace == 0且本地开始上传symbol数据到tasks，new将被重置成false
        # self.new_project_mode = is_new
        self.wpc = WindowPointCtrol(keep_window)
        self.column_only_close = column_only_close
        self.symbol_names = symbol_list
        self.symbols = DomainSymbols(domain_name=local.node_domain, symbols=self.symbol_names)
        self.trading_signals = dict()
        self.dataflows = self.get_historical_data_flows(
            histories_length, 
            custom_ohlcv_columns, 
            custom_index_name
        )
        self.positions = HistoricalPositionMap()
        self.init_asset(**order_config)

    def create_ta(self,TA):
        self.ta = TA.create(self.symbols)


    def get_historical_data_flows(self,
            histories_length,
            ohlcv_columns,
            index_name
        )->bool | None:
        """
            history file name:
                $symbol.$institution.csv
        """

        #wait check index_name 
        #wait check ohlcv_columns
        #config symbol_list有特定的执行任务列表

        try:
            histories = []
            for symbol in self.symbol_names:
                file_name = local.project_symbol_map[symbol]
                history = self.csv_to_history(file_name, ohlcv_columns, index_name)
                histories.append(history)
            histories_data = pd.concat(histories, axis=1, keys=self.symbol_names)
            real_histories_length = len(histories_data.index)
            if histories_length > real_histories_length:
                logger.warning(f"set real histories length {real_histories_length} replace config histories length")
                histories_length = real_histories_length
            if histories_length < self.wpc.keep_point_window  * 2:
                raise StrategyInitError(f"real histories length:{histories_length} need keep two times to point window:{self.wpc.keep_point_window }")
            # if self.new_project_mode == True:

            #     offset = 0 * keep_window
       
            # else:
            #     offset = 1 * keep_window
                # histories_data = 
            return HistoricalDataFlows(
                histories_data,
                length=histories_length,
                offset=self.wpc.keep_point_window 
            )

        except Exception as e:
            logger.error(e.__repr__())
            exit()          


    def init_asset(self, **order_config):
        default_order_config = order_config["default"]
        for symbol in self.symbol_names:
            # if orderconfig.get(symbol):
            # 如果symbol有了第一次获取asset资金来源则跳过， 只有通过执行open_account_symbol 才会满足symbol_account_is_open
            symbol_state = self.symbols.get_symbol_state(symbol_name=symbol)

            if symbol_state == "created":

                if order_config.get(symbol,None) == None:
                    symbol_order_config = order_config.setdefault(symbol, default_order_config)
                else:
                    symbol_order_config = order_config.get(symbol)
            # logger.debug(f'symbol {symbol} order config : {symbol_order_config}')
                balance = symbol_order_config.setdefault("balance", default_order_config["balance"])
                long_fee = symbol_order_config.setdefault("long_fee", default_order_config["long_fee"])
                short_fee = symbol_order_config.setdefault("short_fee", default_order_config["short_fee"])
                leverage = symbol_order_config.setdefault("leverage", default_order_config["leverage"])
                try:
                    if balance <= 0:
                        raise StrategyInitError(f"account set balance number too small")
                    if long_fee < 0 or long_fee >= 1:
                        raise StrategyInitError("account set long_fee number error")
                    if short_fee < 0 or  short_fee >= 1:
                        raise StrategyInitError("account set short_fee number error")
                    if leverage < 1  or isinstance(leverage, int)==False:
                        raise StrategyInitError("account set leverage  error")
                except Exception as e:
                    logger.error(f'error from init_asset:{e.__repr__()}')
                    exit()
                    
                self.symbols.transfer_to_symbol(balance,symbol=symbol)
                self.symbols.set_symbol_state(symbol_name=symbol,state="balanced")
                self.positions.add_position(symbol,
                    HistoricalPosition.init(symbol, balance, leverage, long_fee, short_fee)
                )
            
    def get_position(self,symbol):
        return self.positions.__getattr__(symbol,{})

    @property
    def histories_index(self):
        return self.dataflows.histories_index
    
    @property
    def domain(self):
        return local.node_domain

    def get_trading_quota(self, symbol:str):
        price = self.get_current_history(symbol)["open"]
        return price

    def get_current_ohlc(self,symbol):
        ohlc =  getattr(self.symbols, symbol).property_dict["ohlc"]
        return ohlc

    def _update_orders(self):
        """
            此时处理的订单价格是该symbol 前period的close 
        """
        # [{'symbol': 'SZ002212', 'direction': 1, 'action': 'buy', 'qty': 1, 'price': None, 'order_type': 'historical', 'status': 'pending', 'fil_qty': 0, 'qty_filled_rate': 0.9}]
        if self.has_signal == True:
            trade_time=self.dataflows.previous_datetime_str
            trading_signals = self.trading_signals.pop(trade_time, [])
            if len(trading_signals) > 0:
                for order in trading_signals:
                    price = self.get_trading_quota(order.symbol)
                    #type price is numpy float64
                    if ( price > 0) == False:
                        #此次交易信号作废
                        continue
                    position = self.get_position(order.symbol)
                    #回测直接成交
                    order.finish_historical_order()
                    #更新订单
                    #previous_period_close order.price 是上一period close的价格
                    position.update_order(order)
            self.has_signal = False 

    def _update_orderbook(self, current_datetime):
        current_datetime = current_datetime
        for symbol in self.symbol_names:
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
        self.update_symbol_objects()
        self._update_orders()
        self._update_orderbook(self.dataflows.current_datetime)


    def make_trading_signal(self,tradetime : str, order : Order):
        # 由于考虑同一时间节点存在多个买入信号，所以trading_signals 使用列表结构
        if self.trading_signals.get(tradetime):
            self.trading_signals[tradetime].append(order)
        else:
            self.trading_signals[tradetime] = []
            self.trading_signals[tradetime].append(order)
        self.has_signal = True


    def sell(self, symbol ,qty, islong=True):
        # tradetime_str = tradetime.strftime('%Y-%m-%d %H:%M:%S')
        if symbol in self.symbol_names:
            tradetime = self.dataflows.current_datetime_str
            order = Order(symbol=symbol, qty=qty, action="sell", order_type="historical", islong=islong)
            self.make_trading_signal(tradetime, order)
            logger.debug(f'current datetime:{tradetime}, symbol {symbol} make a {"long" if islong else "short"} sell \n \
                         trading signal for deal at {self.dataflows.next_period_index}')
        else:
            logger.warning(f'trading failed. symbol:"{symbol}" is not register in symbol task list:{self.symbol_names}')

    def buy(self, symbol ,qty, islong=True):
        if symbol in self.symbol_names:
            tradetime = self.dataflows.current_datetime_str
            order = Order(symbol=symbol, qty=qty, action="buy", order_type="historical", islong=islong)
            self.make_trading_signal(tradetime, order)
            logger.debug(f'current datetime:{tradetime}, symbol {symbol} make a {"long" if islong else "short"} buy \n \
                         trading signal for deal at {self.dataflows.next_period_index}')
        else:
            logger.warning(f'trading failed. symbol:"{symbol}" is not register in symbol task list{self.symbol_names}')

    async def run( self , **kwargs):
        try:
            await asyncio.sleep(0)
            self.dataflows.update()
            self.update()
            self.start()
        except Exception as e:
            logger.error(e.__repr__())
            looper.stop()
        if self.wpc.pace == 0:
            logger.debug(f"wpc active {self.wpc.cyclepoint}")
            self.dataflows.histories = self.dataflows.histories[self.wpc.keep_point_window : ]  
            
            # try:
            #     for symbol in self.symbol_names:
            #             history = getattr(self, symbol).history[:self.wpc.keep_point_window]
            #             history.index = history.index.astype("str")
            #             ohlcv=history.loc[:,history.columns[:5]]
            #             analyses = history.loc[:,history.columns[5:]]
            #             #合并方式:pd.concat([ohlcv,analyses],axis=1)# 支持一方合并空df 
            #             orderbook = getattr(self, symbol).orderbook[:self.wpc.keep_point_window]
            #             orderbook.index = orderbook.index.astype("str")
            #             domain_update_symbol_info(
            #                 domain=local.node_domain, 
            #                 symbol=symbol,
            #                 ohlcv=ohlcv.T.to_dict(orient='list'),
            #                 analyses = analyses.T.to_dict(orient='list'),
            #                 orderbook=orderbook.T.to_dict(orient="list")
            #             )
       
            # except Exception as e:
            #     logger.error(e.__repr__())
            #     exit()
            # if config.update_tasks_domain == "new":
            #     config.update(update_tasks_domain=False)
            #     looper.stop()
        #不做修改
        if self.dataflows.slided_end:
            try:
                self.positions.settlement_all_symbol()
                self.symbols.set_all_symbol_done()
                self.update()
                self.end()
                looper.stop()
            except Exception as e:
                logger.error(e.__repr__())
                looper.stop()