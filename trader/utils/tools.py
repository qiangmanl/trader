import string
import random

import pandas as pd

def gen_random_id(length:int=18) -> str:
    char = string.ascii_letters + string.digits
    return ''.join(random.choice(char) for _ in range(length))

def str_pd_datetime(dt)->str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_current_strftime(fmt:str="%Y-%m-%d %H:%M:%S") -> str:
    current_datetime = datetime.now()
    datetime = current_datetime.strftime(fmt)
    return datetime

def strftime_to_index_datetime(strftime:str):
    return pd.to_datetime(strftime,format="%Y-%m-%d %H:%M:%S")

