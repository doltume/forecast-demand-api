import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()
url = os.getenv("DATABASE_URL")
if url is None:
    raise SystemExit("DATABASE_URL is missing in .env")

# SQLAlchemy needs to know which driver to use
url = url.replace("postgres://", "postgresql://", 1)
url = url.replace("postgresql://", "postgresql+psycopg2://", 1)
engine = create_engine(url)

with open("sql/schema.sql", encoding="utf-8-sig") as f:
    schema = f.read()

with engine.begin() as conn:
    conn.exec_driver_sql(schema)

print("Tables created on Neon")
