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
                if data_json.get("data"):
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
        sbd = ma_tinh_str + f"{i:06d}"
        URL = os.getenv('URL')
        url = URL.replace('SBD',sbd)

        data_json = get_with_retry(url)

        if data_json is None or not data_json.get("data"):
            print(f"Không có dữ liệu cho {sbd}")
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
            print(f"{sbd} → {row}")

        except Exception as e:
            continue

    os.makedirs("data_by_province", exist_ok=True)
    output_file = f"data_by_province/diem_{ma_tinh_str}_1_199999.csv"
    if os.path.exists(output_file):
        try:
            df = pd.read_csv(output_file, encoding='utf-8-sig')
        except pd.errors.EmptyDataError:
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()

    df = pd.concat([df,df_tinh],ignore_index=True)
    df.drop_duplicates(subset=["SBD"], keep="first", inplace=True)
    df.sort_values(by="SBD", inplace=True)
    df.to_csv(f"data_by_province_res/diem_{ma_tinh_str}_res.csv", index=False, encoding='utf-8-sig') # chỉ cần 1 lần cào lại missing là xong
    
    pd.DataFrame(missing_sbd, columns=['SBD']).to_csv(f"data_by_province/missing_{ma_tinh_str}_1_199999.csv", index=False, encoding='utf-8-sig')

    return f"{ma_tinh_str} xong: {len(df_tinh)} dòng"

if __name__ == "__main__":
    max_threads = 7 
    provinces = list(range(1, 65))
    provinces.sort()
    folder_path = "data_by_province"

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = []

        for ma_tinh in provinces:
            ma_tinh_str = f"{ma_tinh:02d}"
            missing_file = os.path.join(folder_path, f"missing_{ma_tinh_str}_1_199999.csv")
            
            if os.path.exists(missing_file):
                try:
                    df_missing = pd.read_csv(missing_file)
                    list_missing = [int(sbd[-6:]) for sbd in df_missing['SBD'].dropna().astype(str)]
                    if list_missing:
                        futures.append(executor.submit(crawl_range, ma_tinh_str, 0, 0, list_missing))
                        print(len(list_missing))
                except Exception as e:
                    print(e)
            else:
                pass

        for future in as_completed(futures):
            print(future.result())



