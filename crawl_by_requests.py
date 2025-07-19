import requests
import pandas as pd
import time, os
from dotenv import load_dotenv
load_dotenv()

def get_with_retry(url, retries=3, delay=1):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data_json = response.json()
                if data_json.get("data"):
                    return data_json
        except Exception as e:
            print(f"Lỗi retry lần {attempt+1} với URL {url}: {e}")
        time.sleep(delay + attempt * 0.5)
    return None


df = pd.DataFrame()
missing_sbd = []

for ma_tinh in range(1, 65):
    ma_tinh_str = f'{ma_tinh:02d}'
    i = 1
    no_data_count = 0  

    drop_cols = [
        'Id','file_name', 'modified_date', 'DM1', 'DM2', 'DM3', 'DM4',
        'DM5', 'DM6', 'DM7', 'DM8', 'DM9', 'DM10', 'DM11', 'DM12', 'DM13',
    ]

    while True:
        sbd = ma_tinh_str + f"{i:06d}"
        i += 1
        URL = os.getenv('URL')
        url = URL.replace('SBD',sbd)

        data_json = get_with_retry(url)

        if data_json is None or not data_json.get("data"):
            print(f"Không lấy được dữ liệu cho SBD {sbd}, thêm vào missing")
            missing_sbd.append(sbd)
            no_data_count += 1

            if no_data_count >= 20:
                break
            continue

        no_data_count = 0  

        try:
            row = data_json['data'][0]
            for col in drop_cols:
                row.pop(col, None)

            df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
            print(f"{sbd} → {row}")

            if i % 100 == 0:
                print(f"Tỉnh {ma_tinh_str}, đã lấy đến SBD: {sbd}")

        except Exception as e:
            print(f"Lỗi xử lý dữ liệu SBD {sbd}: {e}")
            continue

df.to_csv("diem_thi_thpt_2025.csv", index=False, encoding='utf-8-sig')
pd.DataFrame(missing_sbd, columns=['SBD']).to_csv('missing_sbd.csv', index=False, encoding='utf-8-sig')

print('xong')
