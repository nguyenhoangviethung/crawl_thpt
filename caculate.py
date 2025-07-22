import pandas as pd
import numpy as np
filepath = 'diem_thi_thpt_2025.csv'
khoi_filepath = 'khoi_thi_dai_hoc.csv'
maNN_filepath = 'ma_mon_ngoai_ngu.csv'

df = pd.read_csv(filepath, index_col = 'SBD')
df_khoi = pd.read_csv(khoi_filepath)
df_maNN = pd.read_csv(maNN_filepath)

ma_NN = dict(zip(df_maNN['Mã môn'], df_maNN['Tên môn']))

ten_NN = []
for ma, ten in ma_NN.items():
    ten_NN.append(ten)
    df[ten] = df.apply(
        lambda row: row['NN'] if row['MA_MON_NGOAI_NGU'] == ma else np.nan, axis = 1
    )

for _, row in df_khoi.iterrows():
    khoi = row['Khối']
    ds_mon  = row['Tổ hợp môn'].split(', ')
    df[khoi] = round(df[ds_mon].sum(axis = 1, skipna = True).fillna(0),ndigits=2)

df['Tổng điểm'] = df['TONGDIEM']
ten_NN.append('TONGDIEM')
df.drop(columns=ten_NN, inplace=True)

print(df.head())
df.to_csv('diem_thpt_2025_cac_khoi_thi.csv', encoding='utf-8-sig')