CREATE TABLE sales (
    id SERIAL PRIMARY KEY,
    sale_date DATE NOT NULL,
    store_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL
);

CREATE TABLE forecasts (
    id SERIAL PRIMARY KEY,
    forecast_date DATE NOT NULL,
    store_id INTEGER NOT NULL,
    item_id INTEGER NOT NULL,
    predicted_quantity NUMERIC NOT NULL,
    model_version TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE model_runs (
    id SERIAL PRIMARY KEY,
    model_version TEXT NOT NULL,
    mae NUMERIC,
    rmse NUMERIC,
    trained_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_sales_store_item_date ON sales (store_id, item_id, sale_date);