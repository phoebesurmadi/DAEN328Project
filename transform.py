import pandas as pd
import os
import re


# load messy data
input_path = 'DAEN328_Project/data/Messy_Data.csv'
data = pd.read_csv(input_path)


# CLEAN DATA
def extract_violation_numbers(violations):
    if pd.isna(violations) or violations == "nan":
        return []
    return [str(int(num)) for num in re.findall(r'\b\d+\b', violations)] 



def clean(df):
    df['inspection_date'] = pd.to_datetime(df['inspection_date']).dt.strftime('%Y-%m-%d')

    # fix city
    df['city'] = df['city'].str.replace(r'(?i)chicago', 'CHICAGO', regex=True)

    # fix facility type
    df['facility_type'] = df['facility_type'].str.replace(r'(?i)(.*years.*|.*school.*|.*daycare.*|.*youth.*|.*shcool.*|.*charter.*|.*child.*|.*children.*|.*student.*)', 'Child or Student Facilities', regex=True)
    df['facility_type'] = df['facility_type'].str.replace(r'(?i)(.*store.*|.*pharmacy.*|.*shop.*|.*grocery.*|.*liquor.*|.*wholesale.*|.*mart.*|.*retail.*|.*service.*|.*gas.*)', 'Retail', regex=True)
    df['facility_type'] = df['facility_type'].str.replace(r'(?i)(.*restaurant.*|.*catering.*|.*diner.*|.*shared.*|.*kitchen.*|.*pantry.*|.*bakery.*|.*tavern.*|.*coffee.*|.*ice.*|.*deli.*|.*sushi.*|.*tea.*|.*bakery.*|.*bar.*|.*hookah.*)', 'Food Service', regex=True)
    df['facility_type'] = df['facility_type'].str.replace(r'(?i)(.*mobile.*)', 'Mobile', regex=True)
    df['facility_type'] = df['facility_type'].str.replace(r'(?i)(.*event.*|.*venue.*|.*banquet.*|.*church.*)', 'Event or Venue', regex=True)
    df['facility_type'] = df['facility_type'].str.replace(r'(?i)(.*nursing.*|.*elder.*|.*assisted.*|.*senior.*|.*care.*)', 'Elderly Living', regex=True)
    df['facility_type'] = df['facility_type'].where(
        df['facility_type'].isin(['Child or Student Facilities', 'Retail', 'Food Service', 'Mobile', 'Event or Venue', 'Elderly Living']),
        'Other'
    )

    # violations
    data['violations'] = data['violations'].apply(lambda x: ' '.join(extract_violation_numbers(str(x))))


    df = df.drop(columns=['dba_name', 'license_', 'city', 'state', 'location'])
    df = df[df['results'] != 'No Entry']
    df = df.dropna()
    return df


data = clean(data)


#print(f"Total rows: {len(data)}")

# save
output_path = 'DAEN328_Project/data/Clean_Data.csv'

os.makedirs(os.path.dirname(output_path), exist_ok=True)
data.to_csv(output_path, index=False)
