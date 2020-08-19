import os
import pandas as pd
path = r'C:\Users\User\PycharmProjects\quant_ml\data\ticker_level2\data'
file = os.listdir(path)
df_all = pd.DataFrame()
for files in file:
    full_path = os.path.join(path, files)
    print (full_path)
    df = pd.read_csv(full_path, encoding='GBK')
    df_all = df_all.append(df)

print (df_all.head())
df_all.to_csv('test_ticker_data.csv')



