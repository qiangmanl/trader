


from trader import historical_flows

from trader.strategy import HistoricalStrategy
from trader.main import run


class MyStrategy(HistoricalStrategy):
    index_name="trade_time"
    useful_column=['open', 'high', 'low', 'close', 'vol']
    async def start(self):
        print(self.flows_window)
        # print(time.time())
        self.sell("300735",1)
        print(historical_flows)
        # import pdb
        # pdb.set_trace()
if __name__ == "__main__":
    run(MyStrategy) 



