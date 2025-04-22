from dotenv import load_dotenv
import os
import psycopg2
import pandas as pd

df = pd.read_csv('DAEN328_Project/data/Clean_Data.csv')

load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_NAME = os.getenv("POSTGRES_NAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

conn = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    dbname=POSTGRES_NAME,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD
)

cur = conn.cursor()

# Create tables
cur.execute("""
CREATE TABLE IF NOT EXISTS businesses (
  business_id SERIAL PRIMARY KEY,
  dba_name VARCHAR(255),
  facility_type VARCHAR(100),
  risk VARCHAR(50)
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS locations (
  location_id SERIAL PRIMARY KEY,
  business_id INTEGER REFERENCES businesses(business_id),
  address VARCHAR(255),
  zip VARCHAR(10),
  latitude FLOAT,
  longitude FLOAT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS inspections (
  inspection_id INTEGER PRIMARY KEY,
  location_id INTEGER REFERENCES locations(location_id),
  inspection_date DATE,
  inspection_type VARCHAR(100),
  results VARCHAR(50)
);
""")

# Inserting with de-duplication
for _, row in df.iterrows():
    # 1. Insert/get business_id
    cur.execute("""
        SELECT business_id FROM businesses
        WHERE dba_name = %s AND facility_type = %s AND risk = %s
    """, (row['dba_name'], row['facility_type'], row['risk']))
    business = cur.fetchone()

    if business:
        business_id = business[0]
    else:
        cur.execute("""
            INSERT INTO businesses (dba_name, facility_type, risk)
            VALUES (%s, %s, %s) RETURNING business_id
        """, (row['dba_name'], row['facility_type'], row['risk']))
        business_id = cur.fetchone()[0]

    # 2. Insert/get location_id
    cur.execute("""
        SELECT location_id FROM locations
        WHERE business_id = %s AND address = %s AND zip = %s
          AND latitude = %s AND longitude = %s
    """, (business_id, row['address'], row['zip'], row['latitude'], row['longitude']))
    location = cur.fetchone()

    if location:
        location_id = location[0]
    else:
        cur.execute("""
            INSERT INTO locations (business_id, address, zip, latitude, longitude)
            VALUES (%s, %s, %s, %s, %s) RETURNING location_id
        """, (business_id, row['address'], row['zip'], row['latitude'], row['longitude']))
        location_id = cur.fetchone()[0]

    # 3. Insert inspection
    cur.execute("""
        INSERT INTO inspections (
            inspection_id, location_id, inspection_date, inspection_type, results
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (inspection_id) DO NOTHING
    """, (
        row['inspection_id'], location_id, row['inspection_date'],
        row['inspection_type'], row['results']
    ))

conn.commit()
cur.close()
conn.close()

conn.close()
