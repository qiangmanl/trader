
import pandas as pd
from trader.utils.tools import str_pd_datetime
from .base import StrategyBase, SymbolsPropertyBase
from trader.const import ROW_DATA_DIR
from trader import logger, local
from trader.dataflows import HistoricalDataFlows
from trader.orderflows import Order
from trader.positions import HistoricalPositionMap

def csv_to_history(index_name, file, strategy_columns)->bool:
    df = pd.read_csv(f'{ROW_DATA_DIR}/{file}')
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
    logger.error("datetime can't normalized")
    exit()

class HistoricalStrategy(StrategyBase, SymbolsPropertyBase):
    """
    price_reference :"current_period_close"|"next_period_open"
    """
    model = "historical"
    #策略运行时初始化一次，所有策略需要的配置都通过init传递

    def init_account(self, price_reference, **order_config ):
        self.price_reference = price_reference
        self.trading_signals = dict()
        # balance, commission, leverage, direction, price_reference,
        from trader.orderflows import HistoricalOrderBook
        self.orderbook = HistoricalOrderBook(
            symbols_property=self.symbols_property
        )
        self.positions = HistoricalPositionMap(self.symbols_property ,**order_config)
        self.orderbook.build_order_flows(self.current_datetime)
        
    def init_flows(self, histories, histories_length, keys):
        histories_data = pd.concat(histories, axis=1, keys=keys)
        self.data_flows = HistoricalDataFlows(
            histories_data,
            length=histories_length
        )

    def init_history(self,
            index_name:str="datetime",
            strategy_columns:list=['open', 'high', 'low', 'close', 'volume'],
            symbol_list:list=[],
            histories_length=20000,
            price_reference=None,
            order_config = None,
        )->bool | None:
        """
            history file name:
                $symbol.$institution.csv
        """
        
        #wait check index_name 
        #wait check strategy_columns

        #config symbol_list有特定的执行任务列表
        try:
            if symbol_list:
                histories = []
                symbol_property_list = []
                for task_symbol in symbol_list:
                    symbol_property_list.append(f'{self.domain}{task_symbol}')
                    file = local.symbol_file_map[task_symbol]
                    history = csv_to_history(index_name, file, strategy_columns)
                    histories.append(history)

                self.symbols_property = symbol_property_list
                self.init_flows(histories, histories_length, symbol_property_list)
                self.init_account( price_reference, **order_config )

        except Exception as e:
            logger.error(e)
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
    
    # def end(self):
    #     logger.info("historical strategy run end")
    #     # await asyncio.sleep(0)
    #     import pdb
    #     pdb.set_trace()
    #     exit()

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
            # symbols_property.remove(order.symbol)
        order_rows = []
        for symbol in self.symbols_property:
            position = self.get_position(symbol)
            price = self.get_symbol_quota(symbol)
            position.update_position(price, trade_time=str_pd_datetime(trade_time))
            order_rows.extend([price, position.qty, position.value])
            #nan data  bool(nan) == False
        self.orderbook.order_flows.loc[trade_time] = pd.Series(order_rows)

    def get_trading_signal(self):
        trading_signals = self.trading_signals.pop(self.current_datetime,[])
        return trading_signals
    
    def update(self)->bool:
        """
        """
        self.update_symbol_property()
        trading_signals = self.get_trading_signal()
        self.update_account(trading_signals, trade_time=self.current_datetime)


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
        if symbol in self.symbols_property:
            order = Order(symbol=symbol, qty=qty, action="sell", order_type="historical")
            self.make_trading_signal(tradetime, order)
            logger.debug(f'current datetime:{self.current_datetime} make a trading signal at {tradetime}')
        else:
            logger.warning(f'symbol:"{symbol}" not on flows symbol {self.symbols_property}')

    def buy(self, symbol ,qty):
        if symbol in self.symbols_property:
            tradetime = self.next_period_index
            order = Order(symbol=symbol, qty=qty, action="buy", order_type="historical")
            self.make_trading_signal(tradetime, order)
        else:
            logger.warning(f'symbol:"{symbol}" not on flows symbol {self.symbols_property}')
