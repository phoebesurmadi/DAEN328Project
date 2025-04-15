load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_NAME = os.getenv("POSTGRES_NAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

conn = psycopg2.connect(
  host = POSTGRES_HOST,
  port = POSTGRES_PORT,
  dbname = POSTGRES_NAME,
  user = POSTGRES_USER,
  password = POSTGRES_PASSWORD
)

cur = conn.cursor()

create_table_query = """
CREATE TABLE IF NOT EXISTS inspection (
  inspection_id INTEGER PRIMARY KEY,
  business_name VARCHAR(255),
  facility_type VARCHAR(100),
  risk VARCHAR(50),
  address VARCHAR(255),
  zip VARCHAR(10),
  inspection_date DATE,
  inspection_type VARCHAR(100),
  results VARCHAR(50),
  latitude FLOAT,
  longitude FLOAT
);
"""

for index, row in df.iterrows():
  cur.execute(
    "INSERT INTO inspection (inspection_id, business_name, facility_type, risk, address, zip, inspection_date, inspection_type, results, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
    (row['inspection_id'], row['business_name'], row['facility_type'], row['risk'], row['address'], row['zip'], row['inspection_date'], row['inspection_type'], row['results'], row['latitude'], row['longitude'])
  )

conn.commit()
cur.close()
conn.close()
