import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# ✅ Corrected environment variable names
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = int(os.getenv("POSTGRES_PORT"))
POSTGRES_DB = os.getenv("POSTGRES_DB")  # ✅ FIX: match .env key
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

# ✅ Debug print to verify loaded environment variables
print(f"Connecting to {POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB} as {POSTGRES_USER}")

# Connect to PostgreSQL
conn = psycopg2.connect(
    host=POSTGRES_HOST,
    port=POSTGRES_PORT,
    dbname=POSTGRES_DB,
    user=POSTGRES_USER,
    password=POSTGRES_PASSWORD
)

cur = conn.cursor()

# ✅ Confirm dropping table
print("Dropping table if exists...")
cur.execute("DROP TABLE IF EXISTS inspection_db;")

# ✅ Confirm table creation
print("Creating table...")
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
  violations TEXT
);
"""
cur.execute(create_table_query)

# ✅ Load CSV
print("Loading CSV data...")
df = pd.read_csv("DAEN328_Project/data/Clean_Data.csv")
print(f"Loaded {len(df)} rows from CSV.")

# ✅ Confirm start of data insertion
print("Inserting data into database...")

insert_query = """
INSERT INTO inspection_db (
  inspection_id, aka_name, facility_type, risk, address, zip,
  inspection_date, inspection_type, results, latitude, longitude, violations
) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
ON CONFLICT (inspection_id) DO NOTHING
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
    if index % 1000 == 0:
        print(f"Inserted {index}/{len(df)} rows...")

conn.commit()
cur.close()
conn.close()

print("✅ Data loading complete.")


