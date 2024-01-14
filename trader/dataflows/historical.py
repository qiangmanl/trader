from trader import logger
from .base import DataFlows, DatetimeProperty

class HistoricalDataFlows(DataFlows, DatetimeProperty):
    def __init__(self,histories_data, length, keep_window) -> None:
        super().__init__()  
        self.initiated = True
        self.histories = histories_data[:length]
        self.histories_generator = self._gen_histories_generator()
        #为了时间同步,也为了尽早更新recently_period
        self.period_row = None
        self.pre_data = self.preload(window=keep_window +1)
        logger.debug(f'DataFlows initiate: \n {self.pre_data }'
                    )

        self.histories_index = self.histories.index[keep_window : ]
        self.lastest_histories_index_num = len(self.histories_index)
        self._histories_end_index_num = 0

    def _gen_histories_generator(self):
        for _, histories_period in self.histories.iterrows():
            yield histories_period

    def _get_period(self):
        return next(self.histories_generator)

    @property
    def slided_end(self):
        return self.histories_index[self._histories_end_index_num] == self.histories_index[-1]

    @property
    def period(self):
        """
        all strategy runing and calculate rely on current_window data 
        or singe symbol rely on  
        """
        return self.period_row

    @property
    def current_datetime_index(self):
        return self.histories_index[self._histories_end_index_num]

    @property
    def previous_datetime_index(self):
        return self.histories_index[self._histories_end_index_num -1]

    @property
    def next_period_index(self):
        if self.slided_end == False:
            return self.histories_index[ self._histories_end_index_num + 1]
        else:
            #用在最后一次结算,当时买入当时卖出
            return self.histories_index[ self._histories_end_index_num ]

    def update(self):
        self._histories_end_index_num += 1
        self.period_row = self._get_period()
        # if self._histories_end_index_num == 19:

        # self.histories.drop(self.histories.index[0],axis=0,inplace=True)
        # if getattr(self,"x",None)==None:
        #     self.x = 1
        # self.x +=1
        # print(self.x)


