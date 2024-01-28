
trading_signals1 = {}

tradetime= "A"
order = "B"
symbol = "C"
def make_trading_signal(tradetime, order , symbol):
    # 由于考虑同一时间节点存在多个买入信号，所以trading_signals 使用列表结构

    if trading_signals1.get(tradetime,None) == None:
        trading_signals1[tradetime] = dict()
        trading_signals1[tradetime][symbol] = [order]
        
    else:
        if trading_signals1[tradetime].get(symbol,None) == None:
                trading_signals1[tradetime][symbol] = [order]
        else:
            trading_signals1[tradetime][symbol].append(order)

trading_signals = {}
def make_trading_signal2(tradetime, order):
    if trading_signals.get(tradetime):
        trading_signals[tradetime].append(order)
    else:
        trading_signals[tradetime] = []
        trading_signals[tradetime].append(order)

%timeit make_trading_signal(tradetime, order , symbol)
%timeit make_trading_signal2(tradetime, order)