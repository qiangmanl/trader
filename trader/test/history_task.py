class HistoricalTask:
    def __init__(self, history, forword=100):


        # print(history.dtypes)
        # history.index = pd.Categorical(history.index)
        self.last_trade_time = history.index[-1]
        self.remember = history.iloc[:forword].copy()
        history.drop(history.index[:forword], axis=0, inplace=True)

        self.remember['order_type'] = pd.Series(dtype='object')
        self.remember['order_qty'] = pd.Series(dtype='float64')
        # for column in history.columns:
        #     history[column] = pd.Categorical(history[column])


        print(history.memory_usage())
        print(history.dtypes)
        self.traing_index = history.index[0]
        self.futrue = history.iterrows()

    def __end(self):
        pass

    def not_latest_trading(self):
        return self.traing_index < self.last_trade_time
    
    def __gen_next_row(self):
        for indexed_row in self.futrue:
            yield indexed_row

    async def __get_trading_row(self,strategy):
        for _, row in  self.__gen_next_row():
            trading_row = row.to_frame().T
            self.remember = pd.concat([self.remember, trading_row])
            # await strategy.start() 
            # await asyncio.sleep(0)
    async def run_strategy(self , strategy , **kwargs):
        if  self.not_latest_trading():
            print(self.remember)
            await self.__get_trading_row(strategy) 
  
        else:
            self.__end()
            # logger.info("task stop with trade end")


import pandas as pd




