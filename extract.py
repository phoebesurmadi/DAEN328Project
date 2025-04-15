
#       EXTRACTION

import pandas as pd
import requests
import os


# fetch data from the API endpoint with a limit of 1000 rows
url = "https://data.cityofchicago.org/resource/4ijn-s7e5.csv?$limit=1000&$offset=0"
response = requests.get(url)

# load data into a pandas DataFrame from the response content
data = pd.read_csv(url)

# save
output_path = 'DAEN328_Project/data/Messy_Data.csv'

os.makedirs(os.path.dirname(output_path), exist_ok=True)
data.to_csv(output_path, index=False)

