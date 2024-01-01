# from trader.utils.tools import gen_random_id
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
        return self


class SymbolsPropertyDict(DictBase):
    pass