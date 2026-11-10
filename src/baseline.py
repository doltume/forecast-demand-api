import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sklearn.metrics import mean_absolute_error, mean_squared_error

load_dotenv()
url = URL.create(
    "postgresql+psycopg2",
    username="forecast",
    password=os.getenv("DB_PASSWORD"),
    host="localhost",
    port=5432,
    database="forecast",
)
engine = create_engine(url)

df = pd.read_sql(
    "SELECT sale_date, store_id, item_id, quantity FROM sales "
    "ORDER BY store_id, item_id, sale_date",
    engine,
)
df["sale_date"] = pd.to_datetime(df["sale_date"])

# Prediction = average of the 7 previous days, for each store and product
df["pred"] = df.groupby(["store_id", "item_id"])["quantity"].transform(
    lambda s: s.shift(1).rolling(7).mean()
)

# Test on the last 90 days
cutoff = df["sale_date"].max() - pd.Timedelta(days=90)
test = df[df["sale_date"] > cutoff].dropna(subset=["pred"])

mae = mean_absolute_error(test["quantity"], test["pred"])
rmse = np.sqrt(mean_squared_error(test["quantity"], test["pred"]))
print(f"Baseline - MAE: {mae:.2f} | RMSE: {rmse:.2f}")

with engine.begin() as conn:
    conn.execute(
        text(
            "INSERT INTO model_runs (model_version, mae, rmse) "
            "VALUES (:v, :mae, :rmse)"
        ),
        {"v": "baseline_7d_mean", "mae": float(mae), "rmse": float(rmse)},
    )