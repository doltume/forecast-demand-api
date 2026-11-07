import os
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import URL

load_dotenv()
password = os.getenv("DB_PASSWORD")

url = URL.create(
    "postgresql+psycopg2",
    username="forecast",
    password=password,
    host="localhost",
    port=5432,
    database="forecast",
)
engine = create_engine(url)

df = pd.read_csv("data/train.csv")
df = df.rename(columns={
    "date": "sale_date",
    "store": "store_id",
    "item": "item_id",
    "sales": "quantity",
})
df["sale_date"] = pd.to_datetime(df["sale_date"])

df.to_sql("sales", engine, if_exists="append", index=False, chunksize=10000)
print(f"{len(df)} rows loaded")