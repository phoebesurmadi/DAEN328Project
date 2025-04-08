load_dotenv()

POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_PORT = os.getenv("POSTGRES_PORT")
POSTGRES_NAME = os.getenv("POSTGRES_NAME")
POSTGRES_USER = os.getenv("POSTGRES_USER")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")

conn = psycopg2.connect(
  host = POSTGRES_HOST,
  port = POSTGRES_PORT
  dbname = POSTGRES_NAME
  user = POSTGRES_USER
  password = POSTGRES_PASSWORD
)

cur = conn.cursor()

for index, row in df.iterrows():
  cur.execute(
    "INSERT INTO trends (keyword, date, trend_score) VALUES (%s, %s, %s)",
    (row['keyword'], row['date'], row['trend_score'])
  )

conn.commit()
cur.close()
conn.close()
