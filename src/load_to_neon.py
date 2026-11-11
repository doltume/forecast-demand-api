import io
import os

import pandas as pd
import psycopg2
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("DATABASE_URL")
if url is None:
    raise SystemExit("DATABASE_URL is missing in .env")

conn = psycopg2.connect(url)
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM sales")
if cur.fetchone()[0] > 0:
    raise SystemExit("The sales table on Neon is not empty. Stopping.")

df = pd.read_csv("data/train.csv").rename(
    columns={
        "date": "sale_date",
        "store": "store_id",
        "item": "item_id",
        "sales": "quantity",
    }
)

buffer = io.StringIO()
df.to_csv(buffer, index=False, header=False)
buffer.seek(0)

cur.copy_expert(
    "COPY sales (sale_date, store_id, item_id, quantity) FROM STDIN WITH CSV",
    buffer,
)
conn.commit()

cur.execute("SELECT COUNT(*) FROM sales")
print(f"{cur.fetchone()[0]} rows now in Neon")
conn.close()