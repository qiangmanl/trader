# from trader.utils.tools import gen_random_id
import pandas as pd


class DictBase(dict):
    """dict like object that exposes keys as attributes"""

    __slots__ = ()
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    # __setstate__ = dict.update


    def update(self, *args, **kwargs):
        """update and return self -- the missing dict feature in python"""
        super().update(*args, **kwargs)


columns = ["a","b"]
class A:
    def __init__(self):
        self.df = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})

    def f(self):
        for col in columns:
            setattr(self.__class__, col, property(lambda self, col=col: self.df[col]))

    def update(self,data):
        self.df.loc[len(self.df.index)] = data

a = A()
a.f()
a.update({"a":1,"b":"2"})




class A:
    def __init__(self) -> None:
        self.x = 1

    

class B(A):
    def __init__(self) -> None:
        pass
    
 
    def f(self):
        return self.x 
    
b = B()
b.x = 3


d = DictBase()

