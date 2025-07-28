# Bởi vì giới hạn của excel chỉ được 1048576 dòng nên ta có thể bỏ đi những thí sinh có điểm thấp 
# (gần như không ảnh hưởng tới điểm chuẩn)
import pandas as pd

def func(row, khoi_thi):
    for khoi in khoi_thi:
        if row[khoi] >= 20:
            return True
    return False    

df = pd.read_csv('diem_thpt_2025_cac_khoi_thi.csv', index_col='SBD')
df_khoi = pd.read_csv('khoi_thi_dai_hoc.csv')

khoi_thi = []
for _, row in df_khoi.iterrows():
    khoi_thi.append(row['Khối'])
print(khoi_thi)

df = df[df.apply(lambda row: func(row,khoi_thi), axis = 1)]

print(df.head(1000))

df.to_csv('diem_thpt_2025_cut.csv', encoding='utf-8-sig')