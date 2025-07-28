import pandas as pd
import os, numpy as np
path = 'data_by_province_res'

df_res = pd.DataFrame()

for filename in os.listdir(path):
    filename = os.path.join(path, filename)
    df = pd.read_csv(filename)

    df.drop(columns=['STT', 'NGAY_SINH'], inplace=True)
    
    df_res = pd.concat([df_res, df], ignore_index=True)
    # print(df_res.shape)

df_res.replace(-1.0, np.nan, inplace=True)

df_ma_tinh = pd.read_csv('ma_tinh.csv')
df_res = pd.merge(df_res,df_ma_tinh, on='TinhId', how='left')

desired_order = [
    'SBD', 'TinhId','Tên tỉnh', 'MA_MON_NGOAI_NGU', 'TOAN', 'VAN', 'NGOAI_NGU','LI', 'HOA', 'SINH',
    'SU', 'DIA', 'GIAO_DUC_CONG_DAN', 'TIN_HOC', 'GDKT_PL','CN_CONG_NGHIEP', 'CN_NONG_NGHIEP',
    'TONGDIEM'
]

df_res = df_res[desired_order]

df_res.set_index('SBD',inplace=True)
df_res.index = df_res.index.map(lambda x: f'{x:08d}')

mon_map = {
    'TOAN': 'Toán',
    'LI': 'Vật lý',
    'HOA': 'Hoá học',
    'VAN': 'Ngữ văn',
    'SINH': 'Sinh học',
    'SU': 'Lịch sử',
    'DIA': 'Địa lý',
    'NGOAI_NGU': 'NN',  
    'GIAO_DUC_CONG_DAN': 'GDCD',
    'TIN_HOC': 'Tin học',
    'CN_CONG_NGHIEP': 'Công nghệ'
}

df_res.rename(columns=mon_map, inplace=True)
print(df_res.shape)
print(df_res.head(10))

df_res.to_csv('diem_thi_thpt_2025.csv', encoding='utf-8-sig')