
import asyncio

class DataFlows:
    def __init__(self,max_window=200)->None:
        self.histories = None
        self.symbols_property = []
        #滑动最大窗口
        self.max_window = max_window
        self.initiated = False
        self.lastest_histories_index = None
        self.window_start_index = 0

    def start(self):
        raise NotImplementedError("not start implemented")

class HistoricalFlows(DataFlows):
    def __init__(self, max_window=200) -> None:
        super().__init__(max_window)
  
    def init_window(self, histories_data, domain, symbol_property_list, length=20000):
        """
        """
        self.symbols_property = symbol_property_list
        self.domain = domain
        self.initiated = True
        self.histories = histories_data[:length]
        self.lastest_histories_index = len(self.histories.index)
        if  self.lastest_histories_index > self.max_window:
            self._window_end_index = self.max_window
        else:
            self._window_end_index = self.lastest_histories_index

    @property
    def window_slided_end(self):
        return self.histories.index[self._window_end_index] == self.histories.index[-1]

    @property
    def _full_window_index(self):
        """
        """
        return self.histories.index[self.window_start_index:self._window_end_index]
    
    @property
    def current_window(self):
        """
        all strategy runing and calculate rely on current_window data 
        or singe symbol rely on get_current_symbol_window 
        """
        return self.histories.loc[ self.histories.index[ self._window_end_index -1 ] ]

    @property
    def next_flows_period(self):
        if self.window_slided_end == False:
            return self.histories.index[ self._window_end_index ]
        else:
            return self.histories.index[ self._window_end_index -1 ]
        
    @property
    def full_window(self):
        """
        all strategy runing and calculate rely on current_window data 
        or singe symbol rely on get_current_symbol_window 
        """
        return self.histories.loc[self._full_window_index]

    def window_sliding(self):
        self.histories.drop(self.histories.index[0],axis=0,inplace=True)
        # if getattr(self,"x",None)==None:
        #     self.x = 1
        # self.x +=1
        # print(self.x)


