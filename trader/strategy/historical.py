
import pandas as pd
from trader.utils.tools import str_pd_datetime
from .base import StrategyBase, SymbolsPropertyBase
from trader.const import ROW_DATA_DIR
from trader import logger, local
from trader.dataflows.historical import HistoricalFlows
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
        
    def init_history(self,
            index_name:str="datetime",
            strategy_columns:list=['open', 'high', 'low', 'close', 'volume'],
            symbol_list:list=[],
            max_window=1000,
            histories_length=20000
        )->bool | None:
        """
            history file name:
                $symbol.$institution.csv
        """
        self.data_flows = HistoricalFlows(max_window=max_window)
        #wait check index_name 
        #wait check strategy_columns

        #config symbol_list有特定的执行任务列表
        try:
            if symbol_list:
                histories = []
                symbol_property_list = []
                for task_symbol in symbol_list:
                    symbol_property_list.append(f'{local.node_domain}{task_symbol}')
                    file = local.symbol_file_map[task_symbol]
                    history = csv_to_history(index_name, file, strategy_columns)
                    histories.append(history)
                histories_data = pd.concat(histories, axis=1, keys=symbol_property_list)
    
        except Exception as e:
            logger.error(e)
            exit()

        self.data_flows.init_window(histories_data, local.node_domain, symbol_property_list, length=histories_length)
    # local.data_flows.get_symbol_history("300878")
        return True 

    @property
    def next_flows_period(self):
        return self.data_flows.next_flows_period

    def get_position(self,symbol):
        return self.positions.__getattr__(symbol,{})

    @property
    def histories(self):
        return self.data_flows.full_window
    
    @property
    def domain(self):
        return self.data_flows.domain
    
    @property
    def symbols_property(self):
        return self.data_flows.symbols_property

    def calc_trading_price(self, symbol):
        if self.price_reference == "current_period_close":
            data = self.get_previous_history(symbol)
            price = data.close
        elif self.price_reference == "next_period_open":
            data = self.get_current_history(symbol)
            price = data.close
        else:
            logger.error("unknown  trading reference price")
            exit()
        return price

    def end(self):
        logger.info("historical strategy run end")
        # await asyncio.sleep(0)
        import pdb
        pdb.set_trace()
        exit()

    def set_orderbook_prices(self):
        for symbol in self.symbols_property:
            price = self.calc_trading_price(symbol)
            self.orderbook.set_latest_price(symbol, price)

    def update_account(self,trading_signals, trade_time):
        if len(trading_signals) > 0:
            for order in trading_signals:
                price = self.orderbook.get_symbol_price(order.symbol)
                if bool( price > 0) == False:
                    #此次交易信号作废
                    continue
                position = self.get_position(order.symbol)
                if position.is_openning == False:
                    position.openning(price)
                #更新订单
                position.update_position(price, order.fil_qty, order.action, trade_time=str_pd_datetime(trade_time))
        order_rows = []
        for symbol in self.symbols_property:
            position = self.get_position(symbol)
            price = self.orderbook.get_symbol_price(symbol)
            order_rows.extend([price, position.qty, position.value])
            #nan data  bool(nan) == False
        self.orderbook.order_flows.loc[trade_time] = pd.Series(order_rows)

    def update(self)->bool:
        """
        """
        # 信号触发 make_trading_signal

        self.set_history()
        # 更新订单前要先更新价格 因为 trading_signals是上一时刻产生的,此时的update是当前的时间
        self.set_orderbook_prices()
        trading_signals = self.get_trading_signal()
        self.update_account(trading_signals, trade_time=self.current_datetime)

    def get_trading_signal(self):
        trading_signals = self.trading_signals.pop(self.current_datetime,[])
        return trading_signals

    def make_trading_signal(self,tradetime, order):
        # 由于考虑同一时间节点存在多个买入信号，所以trading_signals 使用列表结构
        if self.trading_signals.get(tradetime):
            self.trading_signals[tradetime].append(order)
        else:
            self.trading_signals[tradetime] = []
            self.trading_signals[tradetime].append(order)

    def sell(self, symbol ,qty):
      
        tradetime = self.next_flows_period
        # tradetime_str = tradetime.strftime('%Y-%m-%d %H:%M:%S')
        if symbol in self.symbols_property:
            order = Order(symbol=symbol, qty=qty, action="sell", order_type="historical")
            self.make_trading_signal(tradetime, order)
            logger.debug(f'current datetime:{self.current_datetime} make a trading signal at {tradetime}')
        else:
            logger.warning(f'symbol:"{symbol}" not on flows symbol {self.symbols_property}')

    def buy(self, symbol ,qty):
        if symbol in self.symbols_property:
            tradetime = self.next_flows_period
            order = Order(symbol=symbol, qty=qty, action="buy", order_type="historical")
            self.make_trading_signal(tradetime, order)
        else:
            logger.warning(f'symbol:"{symbol}" not on flows symbol {self.symbols_property}')
