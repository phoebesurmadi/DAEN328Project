
#       EXTRACTION
import requests
import pandas as pd
import time
import os

data = pd.DataFrame()

for offset in range(0, 100000, 1000):
    url = f"https://data.cityofchicago.org/resource/4ijn-s7e5.csv?$limit=1000&$offset={offset}"
    success = False
    retries = 3
    
    while not success and retries > 0:
        try:
            response = requests.get(url)
            response.raise_for_status() 
            temp_data = pd.read_csv(url)
            data = pd.concat([data, temp_data], ignore_index=True)
            success = True
        except requests.exceptions.RequestException as e:
            print(f"error fetching data at offset {offset}: {e}")
            retries -= 1
            time.sleep(5)  
    
    if not success:
        print(f"failed to fetch data at offset {offset} after 3 retries.")




output_path = 'DAEN328_Project/data/Messy_Data.csv'

os.makedirs(os.path.dirname(output_path), exist_ok=True)
data.to_csv(output_path, index=False)

