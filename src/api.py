import os
from datetime import date, timedelta
from typing import Optional

import joblib
import pandas as pd
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

load_dotenv()
database_url = os.getenv("DATABASE_URL")
if database_url:
    database_url = database_url.replace("postgres://", "postgresql://", 1)
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    engine = create_engine(database_url, pool_pre_ping=True)
else:
    url = URL.create(
        "postgresql+psycopg2",
        username="forecast",
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=5432,
        database="forecast",
    )
    engine = create_engine(url)

bundle = joblib.load("models/lightgbm_v1.joblib")
model = bundle["model"]
features = bundle["features"]
MODEL_VERSION = "lightgbm_v1"

app = FastAPI(title="Demand Forecast API")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/predict")
def predict(store_id: int, item_id: int, target_date: Optional[date] = None):
    with engine.connect() as conn:
        last = conn.execute(
            text(
                "SELECT MAX(sale_date) FROM sales "
                "WHERE store_id = :s AND item_id = :i"
            ),
            {"s": store_id, "i": item_id},
        ).scalar()
        if last is None:
            raise HTTPException(status_code=404, detail="Unknown store_id / item_id")

        if target_date is None:
            target_date = last + timedelta(days=1)

        rows = conn.execute(
            text(
                "SELECT quantity FROM sales "
                "WHERE store_id = :s AND item_id = :i "
                "AND sale_date >= :start AND sale_date < :end "
                "ORDER BY sale_date"
            ),
            {
                "s": store_id,
                "i": item_id,
                "start": target_date - timedelta(days=28),
                "end": target_date,
            },
        ).fetchall()

    if len(rows) != 28:
        raise HTTPException(
            status_code=400,
            detail="Need the 28 days of sales before the target date",
        )

    q = pd.Series([r[0] for r in rows])  # oldest day first, newest day last

    row = {
        "store_id": store_id,
        "item_id": item_id,
        "lag_7": q.iloc[21],
        "lag_14": q.iloc[14],
        "lag_28": q.iloc[0],
        "roll_7": q.iloc[21:].mean(),
        "roll_28": q.mean(),
        "dayofweek": target_date.weekday(),
        "month": target_date.month,
        "dayofyear": target_date.timetuple().tm_yday,
    }
    X = pd.DataFrame([row])[features]
    pred = float(model.predict(X)[0])

    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO forecasts "
                "(forecast_date, store_id, item_id, predicted_quantity, model_version) "
                "VALUES (:d, :s, :i, :p, :v)"
            ),
            {
                "d": target_date,
                "s": store_id,
                "i": item_id,
                "p": pred,
                "v": MODEL_VERSION,
            },
        )

    return {
        "store_id": store_id,
        "item_id": item_id,
        "date": str(target_date),
        "predicted_quantity": round(pred, 1),
        "model_version": MODEL_VERSION,
    }