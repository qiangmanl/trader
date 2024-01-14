class BaseCostomError(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)

class TasksRequestError(BaseCostomError):
    pass

class TasksAccountError(BaseCostomError):
    pass

class LocalAccountError(BaseCostomError):
    pass


class DataIOError(BaseCostomError):
    pass


# try:
#     1/0
# except Exception as e:
#     raise TasksRequestError(e)