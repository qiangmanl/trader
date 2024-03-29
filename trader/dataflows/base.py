
import pandas as pd

from trader.utils.tools import str_pd_datetime


class DataFlows:
    def __init__(self)->None:
        self.histories = None
        self.initiated = False
        self.lastest_histories_index_num = None
        self.window_start_index = 0

    def _get_period(self):
        raise NotImplementedError("not _get_period_row implemented")

    @property
    def period(self):
        raise NotImplementedError("not period implemented")


    def preload(self,window):
        data = []
        for _ in range(window):
            data.append(self._get_period())
        return pd.DataFrame(data)

    # @property
    # def current_period_index(self)->pd.core.indexes.datetimes.DatetimeIndex:
    #     return self.period.name

class DatetimeProperty:
    @property 
    def current_datetime(self):
        # 当前策略执行到的日期在window最后
        return self.current_datetime_index

    @property
    def current_datetime_str(self):
        return str_pd_datetime(self.current_datetime)

    @property
    def next_period_index(self):
        raise NotImplementedError("not next_period_index implemented")

    @property
    def previous_datetime(self):
       return self.previous_datetime_index

    @property
    def previous_datetime_str(self):
       return str_pd_datetime(self.previous_datetime_index)

    @property
    def today(self):
        return self.current_datetime.date()
    
    @property
    def yesterday(self):
        return self.today - pd.Timedelta(days=1)

    @property
    def current_time(self):
        return self.current_datetime.time()