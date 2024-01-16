from functools import wraps

def handle_signals_errors(func):
    @wraps(func)
    def wrapper(a, b):
        try:
            print(a)
            if b == 0:
                return func(a,b)
            else: 
                1/0
        except Exception as e:
            return '', f'from {func.__name__}:{e.__repr__()}'
    return wrapper

# 使用装饰器
@handle_signals_errors
def set_signals(a=1, b=0):
    print(a)
    print(b)
    return a,b
# 示例用法
result = set_signals(a=1,b=2)
print(result)