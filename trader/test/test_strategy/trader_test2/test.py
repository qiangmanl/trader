


import asyncio
from trader.strategy import HistoricalStrategy
from trader.main import run_strategy

class MyStrategy(HistoricalStrategy):
    index_name="trade_time"
    strategy_columns=['open', 'high', 'low', 'close', 'vol']
    def __init__(self):
        self.x = 1
        pass


    def start(self):
        self.x += 1
        # if len(self.orderbook.order_flows) %100 == 0:
        print(self.orderbook.order_flows)
            # print(self.SZtest.history)
            # print(self.SZtest.position)
        # # print(self.current_window)
        # # print(self.data_flows.histories)
       
        # # print(time.time())
        
        # if self.SZtest.position.qty == 2:
        #     self.buy("SZtest",1)
        #     print(f'{self.current_datetime}buy')
        #     print(self.SZtest.position.qty)
        #     print(self.SZtest.position.latest_price)
        #     print(self.SZtest.position.profit)
        # else:
        #     self.sell("SZtest",1) 
        #     print(f'{self.current_datetime}sell')
        #     print(self.SZtest.position.qty)
        #     print(self.SZtest.position.latest_price)
        #     print(self.SZtest.position.profit)

        # import pdb
        # pdb.set_trace()
        # await asyncio.sleep(0)
        # import pdb
        # pdb.set_trace()
if __name__ == "__main__":
    run_strategy(MyStrategy) 



