import requests
import pandas as pd
import time
import os

# Initialize an empty DataFrame to store the data
data = pd.DataFrame()

# Loop to fetch 100000 rows of data in increments of 1000
for offset in range(0, 100000, 1000):
    url = f"https://data.cityofchicago.org/resource/4ijn-s7e5.csv?$limit=1000&$offset={offset}"
    success = False
    retries = 3
    
    while not success and retries > 0:
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check if the request was successful
            temp_data = pd.read_csv(url)
            data = pd.concat([data, temp_data], ignore_index=True)
            success = True
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data at offset {offset}: {e}")
            retries -= 1
            time.sleep(5)  # Wait for 5 seconds before retrying
    
    if not success:
        print(f"Failed to fetch data at offset {offset} after 3 retries.")


print(f"Total rows: {len(data)}")


output_path = 'DAEN328_Project/data/Messy_Data.csv'

os.makedirs(os.path.dirname(output_path), exist_ok=True)
data.to_csv(output_path, index=False)


