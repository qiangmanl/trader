from datetime import timedelta
import pandas as pd

df1 = pd.DataFrame({'a': [1, 2], 'b': [3, 4]})
df2 = pd.DataFrame({'a': [5, 6], 'b': [7, 8]})
df3 = pd.DataFrame({'a': [4, 6], 'b': [71, 8]})
# 使用 concat 函数按列合并两个数据框，并保留组名
result = pd.concat([df1, df2], axis=1)

# 打印合并后的结果
print(result)



import pandas as pd
# 假设你有三个股票的数据，每个股票有'close'和'open'两列
stock1_data = {'close': [10, 11, 12], 'open': [9, 10, 11]}
stock2_data = {'close': [20, 21, 22], 'open': [19, 20, 21]}
stock3_data = {'close': [30, 31, 32], 'open': [29, 30, 31]}

# 创建三个DataFrame
df_stock1 = pd.DataFrame(stock1_data, columns=['close', 'open'])
df_stock2 = pd.DataFrame(stock2_data, columns=['close', 'open'])
df_stock3 = pd.DataFrame(stock3_data, columns=['close', 'open'])

# 合并三个DataFrame，并使用MultiIndex创建多级列
df = pd.concat([df_stock1, df_stock2, df_stock3], axis=1, keys=['stock1', 'stock2', 'stock3'])

# 打印结果
print(df)

import pandas as pd
# 假设你有三个股票的数据，每个股票有'close'和'open'两列
stock1_data = {'close': [10, 11, 12], 'open': [9, 10, 11]}
stock2_data = {'close': [20, 21, 22], 'open': [19, 20, 21]}
stock3_data = {'close': [30, 31, 32], 'open': [29, 30, 31]}

# 创建三个DataFrame
df_stock1 = pd.DataFrame(stock1_data, columns=['close', 'open'])
df_stock2 = pd.DataFrame(stock2_data, columns=['close', 'open'])
df_stock3 = pd.DataFrame(stock3_data, columns=['close', 'open'])

# 合并三个DataFrame，并使用MultiIndex创建多级列
df = pd.concat([df_stock1, df_stock2, df_stock3], axis=1, keys=['stock1', 'stock2', 'stock3'])

# 打印结果
print(df)


df_stock1 = pd.DataFrame({'price': [0], 'qty': [0], 'balance': [0]}, columns=['price', 'qty', 'balance'])
{'price': [0], 'qty': [0], 'balance': [0]}
['price', 'qty', 'balance']


class A:
    @classmethod
    def defx(cls,x):
        cls.x = x
        return cls
    
    @classmethod
    @property
    def addx(cls):
        cls.x += 1
        return cls.x

x1 = A.f(1)
x2 = A.f(2)
id(x1) == id(x2)

class B:
    def defx(self,x) -> None:
        self.x = x
        return self

b = B().defx(1)




import pandas as pd
index = pd.date_range(start="2023-05-10",end="2023-10-10",freq="5T")

x = index[0].date()



# index = pd.date_range(start="2023-05-10",end="2023-10-10",freq="5T")
window =10
x = 0
# l =  list(range(100))
# while l !=[]:
#     x +=1 
#     if x == window *2:
#         d = l[:x]
#         l = l[x:]
#         print(d)
#         x = 0

index = pd.date_range(start="2023-05-10",end="2023-10-10",freq="5T")
while len(index) !=0:
    x +=1 
    if x == window *2:
        d = index[:x]
        index =index[x:]
        print(d)
        x = 0