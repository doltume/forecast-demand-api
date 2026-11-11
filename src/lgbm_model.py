import os
import numpy as np
import pandas as pd
import lightgbm as lgb
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

# Features: clues built only from the past
g = df.groupby(["store_id", "item_id"])["quantity"]
df["lag_7"] = g.shift(7)
df["lag_14"] = g.shift(14)
df["lag_28"] = g.shift(28)
df["roll_7"] = g.transform(lambda s: s.shift(1).rolling(7).mean())
df["roll_28"] = g.transform(lambda s: s.shift(1).rolling(28).mean())
df["dayofweek"] = df["sale_date"].dt.dayofweek
df["month"] = df["sale_date"].dt.month
df["dayofyear"] = df["sale_date"].dt.dayofyear

features = [
    "store_id", "item_id", "lag_7", "lag_14", "lag_28",
    "roll_7", "roll_28", "dayofweek", "month", "dayofyear",
]
df = df.dropna(subset=features)

# Train on the past, test on the last 90 days
cutoff = df["sale_date"].max() - pd.Timedelta(days=90)
train = df[df["sale_date"] <= cutoff]
test = df[df["sale_date"] > cutoff]

model = lgb.LGBMRegressor(
    n_estimators=300, learning_rate=0.05, num_leaves=63,
    random_state=42, verbose=-1,
)
model.fit(train[features], train["quantity"])

pred = model.predict(test[features])
mae = mean_absolute_error(test["quantity"], pred)
rmse = np.sqrt(mean_squared_error(test["quantity"], pred))
print(f"LightGBM - MAE: {mae:.2f} | RMSE: {rmse:.2f}")

with engine.begin() as conn:
    conn.execute(
        text(
            "INSERT INTO model_runs (model_version, mae, rmse) "
            "VALUES (:v, :mae, :rmse)"
        ),
        {"v": "lightgbm_v1", "mae": float(mae), "rmse": float(rmse)},
    )


import joblib

os.makedirs("models", exist_ok=True)
joblib.dump({"model": model, "features": features}, "models/lightgbm_v1.joblib")
print("Model saved in models/lightgbm_v1.joblib")