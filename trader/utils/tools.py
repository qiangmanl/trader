import string
import random
from datetime import datetime

def gen_random_id(length:int=18) -> str:
    char = string.ascii_letters + string.digits
    return ''.join(random.choice(char) for _ in range(length))


def str_pd_datetime(dt)->str:
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_current_datetime_str(fmt:str="%Y-%m-%d %H:%M:%S") -> str:
    current_datetime = datetime.now()
    datetime = current_datetime.strftime(fmt)
    return datetime