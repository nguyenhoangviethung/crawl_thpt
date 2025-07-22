import requests
import pandas as pd
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
from dotenv import load_dotenv
load_dotenv()

def get_with_retry(url, retries=3, delay=1):
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data_json = response.json()
                if data_json.get('data'):
                    return data_json
        except Exception as e:
            pass
        time.sleep(delay + attempt * 0.5)
    return None

def crawl_range(ma_tinh_str, start_idx = 1, end_idx = 199999, list_missing = None):
    no_data_count = 0
    drop_cols = [
        'Id','file_name','modified_date','DM1','DM2','DM3','DM4','DM5',
        'DM6','DM7','DM8','DM9','DM10','DM11','DM12','DM13'
    ]

    df_tinh = pd.DataFrame()
    missing_sbd = []

    if list_missing:
        list_crawl = list_missing
    else:
        list_crawl = range(start_idx, end_idx + 1)

    for i in list_crawl:
        sbd = ma_tinh_str + f'{i:06d}'
        URL = os.getenv('URL')
        url = URL.replace('SBD',sbd)

        data_json = get_with_retry(url)

        if data_json is None or not data_json.get('data'):
            print(f'Không có dữ liệu cho {sbd}') #bỏ thi hoặc lỗi api
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
            df_tinh = pd.concat([df_tinh, pd.DataFrame([row])], ignore_index=True)
            print(f'{sbd} → {row}')
        except Exception as e:
            print(f'Lỗi xử lý {sbd}: {e}')
            continue

    os.makedirs('data_by_province', exist_ok=True)
    suffix = f'_{start_idx}_{end_idx}'
    df_tinh.to_csv(f'data_by_province/diem_{ma_tinh_str}{suffix}.csv', index=False, encoding='utf-8-sig')
    pd.DataFrame(missing_sbd, columns=['SBD']).to_csv(f'data_by_province/missing_{ma_tinh_str}{suffix}.csv', index=False, encoding='utf-8-sig')

    return f'{ma_tinh_str} ({start_idx}-{end_idx}) xong: {len(df_tinh)} dòng'

if __name__ == '__main__':
    max_threads = int(os.getenv('MAX_THREADS'))
    provinces = list(range(1, 65))
    provinces.sort()
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []

        if 1 in provinces: # bởi Sở Hà Nội có nhiều thí sinh nhất 
            futures.append(executor.submit(crawl_range, '01', 1, 60000))
            futures.append(executor.submit(crawl_range, '01', 60001, 199999))
            provinces.remove(1)
        for ma_tinh in provinces:
            ma_tinh_str = f'{ma_tinh:02d}'
            futures.append(executor.submit(crawl_range, ma_tinh_str, 1, 199999))
        for future in as_completed(futures):
            print(future.result())
            df_1 = pd.read_csv('data_by_province/diem_01_1_60000.csv')
            df_2 = pd.read_csv('data_by_province/diem_01_60001_199999.csv')
            pd.concat([df_1,df_2], ignore_index= True).to_csv('data_by_province/diem_01_1_199999.csv')
            os.remove('data_by_province/diem_01_1_60000.csv')
            os.remove('data_by_province/diem_01_60001_199999.csv')

            df_1 = pd.read_csv('data_by_province/missing_01_1_60000.csv')
            df_2 = pd.read_csv('data_by_province/missing_01_60001_199999.csv')
            pd.concat([df_1,df_2], ignore_index= True).to_csv('data_by_province/missing_01_1_199999.csv')
            os.remove('data_by_province/missing_01_1_60000.csv')
            os.remove('data_by_province/missing_01_60001_199999.csv')


