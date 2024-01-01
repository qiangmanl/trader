import asyncio
import pandas as pd

async def async_yield_dataframe_rows(df):
    for index, row in df.iterrows():
        await asyncio.sleep(0.001)
        yield row

async def async_main():

    data = {'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35]}
    df = pd.DataFrame(data)


    new_df = pd.DataFrame(columns=df.columns)


    async for row in async_yield_dataframe_rows(df):

        await asyncio.sleep(0.1)

        new_df = pd.concat([new_df, row.to_frame().T], ignore_index=True)


    print(new_df)


asyncio.run(async_main())




count = 0
import time
while True:
    count += 1
    x = 
    t1 = time.time()
    if count % (0.001 * (1 / count)) != 0:
        print("a")
        print(t1 - time.time())

d = {"a":[1,2,3],"b":[344,223]}
all_task = []
for value in d.values():
    all_task.extend(value)
[all_task.extend(value) for value in d.values()]



import inspect
def f():
    method = inspect.currentframe().f_code.co_name
    return method


class MyClass:
    @property
    def current_balance(self):
        method = inspect.currentframe().f_code.co_name
        raise NotImplementedError(f"{method} Not Implemented")

# 创建实例并调用属性
obj = MyClass()
obj.current_balance