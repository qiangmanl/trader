



    
import pandas as pd

# 创建一个示例DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 22],
        'City': ['New York', 'San Francisco', 'Los Angeles']}

df = pd.DataFrame(data)

# 通过iterrows方法逐行生成DataFrame的数据
def dataframe_generator():
    for index, row in df.iterrows():
        yield row

# 另一个函数，接收生成器作为参数
def process_generated_data(generator):
    for data_row in generator():
        # 在这里可以对每一行的数据进行处理
        print(data_row)

# 调用另一个函数并传递生成器
process_generated_data(dataframe_generator)


class DataFrameGenerator:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.generator = self.dataframe_generator()

    def dataframe_generator(self):
        for index, row in self.dataframe.iterrows():
            yield index, row

    @property
    def get_next_row(self):
        return next(self.generator)

# 创建一个示例DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 22],
        'City': ['New York', 'San Francisco', 'Los Angeles']}

df = pd.DataFrame(data)

# 创建DataFrameGenerator实例
df_generator = DataFrameGenerator(df)



class DataFrameGenerator:
    def __init__(self, dataframe):
        self.dataframe = dataframe
        self.generator = self.dataframe_generator()

        

    def dataframe_generator(self):
        for index, row in self.dataframe.iterrows():
            yield index, row

    @property
    def get_next_row(self):
        return next(self.generator)

# 创建一个示例DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 22],
        'City': ['New York', 'San Francisco', 'Los Angeles']}

df = pd.DataFrame(data)

# 创建DataFrameGenerator实例
df_generator = DataFrameGenerator(df)
