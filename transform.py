import pandas as pd
import os

# load messy data
input_path = 'DAEN328_Project/data/Messy_Data.csv'
data = pd.read_csv(input_path)


#       CLEANING

def clean(df):
    df['inspection_date'] = pd.to_datetime(df['inspection_date']).dt.strftime('%Y-%m-%d')
    df = df.drop(columns=['aka_name', 'license_', 'city', 'state', 'violations', 'location'])
    df = df[df['results'] != 'No Entry']
    df = df.dropna()
    return df

# clean
data = clean(data)

# save
output_path = 'DAEN328_Project/data/Clean_Data.csv'

os.makedirs(os.path.dirname(output_path), exist_ok=True)
data.to_csv(output_path, index=False)