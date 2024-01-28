class CustomTA(TechnicalAnalyses):
    @analysis(name="ema_daily")
    def EMAD(self, symbol, source="close", timeperiod=30) ->  Union[int, float, np.number, pd.core.series.Series]:
        data = self.get_daily_data(symbol)
        data = talib.EMA(data[source], timeperiod=timeperiod)
        return data
    
    @analysis(name="ema")
    def EMA(self, symbol, source="close", timeperiod=30) ->  Union[int, float, np.number, pd.core.series.Series]:
        data = talib.EMA(getattr(self.symbols, symbol).history[source], timeperiod=timeperiod)
        return data.iloc[-1]

class MyStrategy(HistoricalStrategy):
    index_name="trade_time"
    ohlcv_columns=['open','high','low','close','vol']


    
    def __init__(self):
        pass

    def init_custom(self):
        self.create_ta(CustomTA)