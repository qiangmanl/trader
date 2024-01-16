class A:
    def __init__(self):
        self.a = 1
        super(A, self).__init__()

class B:
    def __init__(self):
        self.b = 1
        super(B, self).__init__()
class C:
    def __init__(self):
        self.c= 1
        # super(C, self).__init__()
class D(A,B,C):
    def __init__(self):
        pass

d = D()
d.a
d.b
from trader.utils.base import DictBase

class A(DictBase):
    @classmethod
    def init(cls):
        self = cls()
        self.a = 1
        return self
    def c(self):
        self.a = 4

class B():
    def __init__(self):
        self.x = 1
    
    def add(self):
        self.x += 1
        return self.x
    

