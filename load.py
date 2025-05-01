import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv
df = pd.read_csv("DAEN328_Project/data/Clean_Data.csv")

# Load environment variables from .env file
load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_NAME = os.getenv("POSTGRES_NAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# Connect to PostgreSQL
conn = psycopg2.connect(
  host=POSTGRES_HOST,
  port=POSTGRES_PORT,
  dbname=POSTGRES_NAME,
  user=POSTGRES_USER,
  password=POSTGRES_PASSWORD
)

cur = conn.cursor()

# Create the table if it doesn't exist
create_table_query = """
CREATE TABLE IF NOT EXISTS inspection_db (
  inspection_id INTEGER PRIMARY KEY,
  aka_name VARCHAR(255),
  facility_type VARCHAR(100),
  risk VARCHAR(50),
  address VARCHAR(255),
  zip VARCHAR(10),
  inspection_date DATE,
  inspection_type VARCHAR(100),
  results VARCHAR(50),
  latitude FLOAT,
  longitude FLOAT,
  violations VARCHAR(500)
);
"""
cur.execute(create_table_query)

# Insert data into the table
insert_query = """
INSERT INTO inspection_db (
  inspection_id, aka_name, facility_type, risk, address, zip,
  inspection_date, inspection_type, results, latitude, longitude, violations
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

for index, row in df.iterrows():
    cur.execute(insert_query, (
        row['inspection_id'],
        row['aka_name'],
        row['facility_type'],
        row['risk'],
        row['address'],
        row['zip'],
        row['inspection_date'],
        row['inspection_type'],
        row['results'],
        row['latitude'],
        row['longitude'],
        row['violations']
    ))

conn.commit()
cur.close()
conn.close()

