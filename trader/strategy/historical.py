import os
import pandas as pd
from trader.utils.tools import str_pd_datetime
from .base import StrategyBase, SymbolsProperty
from trader import logger, local
from trader.dataflows import HistoricalDataFlows
from trader.orderflows import Order, OrderBookPattern
from trader.positions import HistoricalPositionMap

def csv_to_history(index_name, file, strategy_columns)->bool:
    df = pd.read_csv(f'{local.domain_dir}{os.sep}{file}')
    df = normalize_index(df, index_name)
    df = df.loc[:, strategy_columns]

    return df

def normalize_index(df,isdatetime="datetime"):
    #set index from column named isdatetime, index name always "datetime"
    if isdatetime in df.columns:
        df[isdatetime] = pd.to_datetime(df[isdatetime])
        df.set_index(isdatetime, inplace=True)
        df.rename_axis('datetime', inplace=True)
        return df
    elif isdatetime == "index":
        df.index = pd.to_datetime(df.index)
        df.rename_axis('datetime', inplace=True)
        return df
    # need check datetime
    logger.debug(df)
    logger.error(f'datetime can\'t normalized with index {df.index.name}')
    exit()

class HistoricalStrategy(StrategyBase, SymbolsProperty):
    """
    price_reference :"current_period_close"|"next_period_open"
    """
    model = "historical"
    #策略运行时初始化一次，所有策略需要的配置都通过init传递

    def before_init_define(self,index_name, strategy_columns, symbol_list, price_reference):
        self.index_name = index_name
        self.strategy_columns = strategy_columns
        self.price_reference = price_reference
        symbol_object_list = []
        for task_symbol in symbol_list:
            symbol_object_list.append(f'{task_symbol}')
        self.symbol_objects = symbol_object_list

    def init_account(self, **order_config ):
        self.trading_signals = dict()
        self.positions = HistoricalPositionMap(self.symbol_objects ,**order_config)
     
    def init_data_flows(self, histories):
        histories_data = pd.concat(histories, axis=1, keys=self.symbol_objects)
        self.data_flows = HistoricalDataFlows(
            histories_data,
            length=self.histories_length
        )

    def init_strategy(self,
            histories_length,
            order_config = None,
        )->bool | None:
        """
            history file name:
                $symbol.$institution.csv
        """

        #wait check index_name 
        #wait check strategy_columns
        #config symbol_list有特定的执行任务列表
        self.histories_length = histories_length
        try:
            histories = []
            for symbol in self.symbol_objects:
                file_name = local.project_symbol_map[symbol]
                history = csv_to_history(self.index_name, file_name, self.strategy_columns)
                histories.append(history)

            self.init_data_flows(histories)
            self.init_account( **order_config )

        except Exception as e:
            import pdb
            pdb.set_trace()
            logger.error(e.__repr__())
            exit()          

    # local.data_flows.get_symbol_history("300878")
        return True

    def get_position(self,symbol):
        return self.positions.__getattr__(symbol,{})

    @property
    def histories_index(self):
        return self.data_flows.histories_index
    
    @property
    def domain(self):
        return local.node_domain

    def get_symbol_quota(self,symbol):
        price =  getattr(self,symbol).property_dict["quota"]
        if bool(price > 0) == False:
            price = 0.000001
        return price

    def update_account(self,trading_signals, trade_time):
        
        if len(trading_signals) > 0:
            for order in trading_signals:
                price = self.get_symbol_quota(order.symbol)
                if bool( price > 0) == False:
                    #此次交易信号作废
                    continue
                position = self.get_position(order.symbol)
                order.set_price(price)
                #回测直接成交
                order.finish_historical_order()
                #更新订单
                position.update_position(order.price,trade_time=str_pd_datetime(trade_time), qty=order.fil_qty, action=order.action)

        for symbol in self.symbol_objects:
            position = self.get_position(symbol)
            price = self.get_symbol_quota(symbol)
            position.update_position(price, trade_time=str_pd_datetime(trade_time))
            order_row = OrderBookPattern.create(position).orderbook
            self.get_symbol_orderbook(symbol).loc[trade_time] = order_row
            #nan data  bool(nan) == False
        # import pdb
        # pdb.set_trace()

    def get_trading_signal(self):
        trading_signals = self.trading_signals.pop(self.data_flows.current_datetime,[])
        return trading_signals
    
    def update(self)->bool:
        """
        """
        self.update_symbol_object()
        trading_signals = self.get_trading_signal()
        self.update_account(trading_signals, trade_time=self.data_flows.current_datetime)

    def make_trading_signal(self,tradetime, order):
        # 由于考虑同一时间节点存在多个买入信号，所以trading_signals 使用列表结构
        if self.trading_signals.get(tradetime):
            self.trading_signals[tradetime].append(order)
        else:
            self.trading_signals[tradetime] = []
            self.trading_signals[tradetime].append(order)

    def sell(self, symbol ,qty):
        tradetime = self.next_period_index
        # tradetime_str = tradetime.strftime('%Y-%m-%d %H:%M:%S')
        if symbol in self.symbol_objects:
            order = Order(symbol=symbol, qty=qty, action="sell", order_type="historical")
            self.make_trading_signal(tradetime, order)
            logger.debug(f'current datetime:{self.data_flows.current_datetime} make a trading signal at {tradetime}')
        else:
            logger.warning(f'symbol:"{symbol}" not on flows symbol {self.symbol_objects}')

    def buy(self, symbol ,qty):
        if symbol in self.symbol_objects:
            tradetime = self.data_flows.next_period_index
            order = Order(symbol=symbol, qty=qty, action="buy", order_type="historical")
            self.make_trading_signal(tradetime, order)
        else:
            logger.warning(f'symbol:"{symbol}" not on flows symbol {self.symbol_objects}')
