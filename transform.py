import pandas as pd
import os

# load messy data
input_path = 'DAEN328_Project/data/Messy_Data.csv'
data = pd.read_csv(input_path)


#       CLEANING
facility_mapping = {
    'AFTER SCHOOL PROGRAM': 'Child or Student Facilities',
    'School': 'Child or Student Facilities',
    "Children's Services Facility": 'Child or Student Facilities',
    'Daycare Above and Under 2 Years': 'Child or Student Facilities',
    'Daycare (2 - 6 Years)': 'Child or Student Facilities',
    'DINING HALL': 'Child or Student Facilities',
    'Mobile Food Preparer': 'Mobile',
    'Mobile Prepared Food Vendor': 'Mobile',
    'Mobile Frozen Desserts Vendor': 'Mobile',
    'Long Term Care': 'Elders Facilities',
    'SUPPORTIVE LIVING': 'Elders Facilities',
    'HERBALIFE': 'Supplemental Food',
    'Restaurant': 'Food Service',
    'Catering': 'Food Service',
    'Shared Kitchen': 'Food Service',
    'Shared Kitchen User (Long Term)': 'Food Service',
    'Bakery': 'Food Service',
    'Golden Diner': 'Food Service',
    'CHURCH KITCHEN': 'Food Service',
    'Grocery Store': 'Retail',
    'Liquor': 'Retail',
    'Wholesale': 'Retail',
    'Hospital': 'Institutional Businesses',
    'Movie Theater': 'Institutional Businesses',
    'REGULATED BUSINESS': 'Institutional Businesses'
}



def clean(df):
    df['inspection_date'] = pd.to_datetime(df['inspection_date']).dt.strftime('%Y-%m-%d')

    # fix city
    df['city'] = df['city'].str.replace('CCHICAGO', 'CHICAGO')
    df['city'] = df['city'].str.replace('Chicago', 'CHICAGO')


    df['facility_type'] = df['facility_type'].map(facility_mapping).fillna(df['facility_type'])

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
