
from .base import StrategyBase

class TradeStrategy(StrategyBase):
    model = "trading"

    @property
    def flows_window(cls):
        return 

