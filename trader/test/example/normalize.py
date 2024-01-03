import os
import pandas as pd
def normalize_df(code):
    """
        example:
            code:btc
            row:./data/row_btc.csv
            data:/data/data_btc.csv 
    """
    row_path = f'data{os.sep}row_{code}.csv'
    data_path = f'data{os.sep}data_{code}.csv'
    os.popen(f'cp {row_path} {data_path}').close()
    com = f"""sed -i '1s/^/start,open,high,low,close,volume,closed,quote asset volume,number of trades,\
    taker buy base asset volume,taker buy quote asset volume,ignore\\n/' {data_path}"""
    os.popen(com,"r",1).close()
    df = pd.read_csv(f'{data_path}')
    df["start"] = df["start"] / 1000
    df['start'] = pd.to_datetime(df['start'], unit='s')
    df.set_index('start', inplace=True)
    df.rename_axis('datetime', inplace=True)
    selected_columns = ['open', 'high', 'low', 'close', 'volume']
    df = df.loc[:, selected_columns]
    return df