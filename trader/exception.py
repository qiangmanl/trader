class BaseCostomError(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

class TasksRequestError(BaseCostomError):
    pass

class DataIOError(BaseCostomError):
    pass

class SymbolProcessError(BaseCostomError):
    pass

class StrategyInitError(BaseCostomError):
    pass

class StrategyRunError(BaseCostomError):
    pass
