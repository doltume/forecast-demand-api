\# Demand Forecast API



A small end-to-end demand forecasting project: sales history in PostgreSQL, a LightGBM model, a FastAPI service, all packaged with Docker and checked by GitHub Actions.



\## What it does



Given a store and a product, the API predicts the next day's sales from the previous 28 days of history, and stores each prediction in the database.



\## Stack



Python, pandas, LightGBM, scikit-learn, PostgreSQL, SQLAlchemy, FastAPI, Docker / Docker Compose, pytest, GitHub Actions.



\## Results



Dataset: Kaggle "Store Item Demand Forecasting Challenge" (10 stores, 50 products, 5 years of daily sales). Test period: the last 90 days, never seen during training.



| Model | MAE | RMSE |

|---|---|---|

| Baseline (7-day average) | 8.64 | 11.37 |

| LightGBM | 5.94 | 7.70 |



LightGBM reduces the error by about 31% compared to the baseline.



\## Project structure



\- `src/load\_data.py`: loads the CSV into PostgreSQL

\- `src/baseline.py`: baseline model and its score

\- `src/lgbm\_model.py`: trains LightGBM, saves it in `models/`

\- `src/api.py`: FastAPI service

\- `sql/schema.sql`: table definitions

\- `sql/exploration.sql`: exploration queries

\- `tests/`: API tests

\- `.github/workflows/ci.yml`: tests and Docker build on every push



\## Run it locally



1\. Download `train.csv` from Kaggle and put it in `data/`.

2\. Create a `.env` file containing `DB\_PASSWORD=your\_password`.

3\. Start the database and the API:



&#x20;  `docker compose up -d --build`



4\. Create the tables:



&#x20;  `Get-Content sql\\schema.sql | docker compose exec -T db psql -U forecast -d forecast`



5\. Load the data (needs a Python environment with the libraries from `requirements.txt`):



&#x20;  `python src\\load\_data.py`



6\. Try the API: http://127.0.0.1:8000/predict?store\_id=1\&item\_id=1



Interactive docs: http://127.0.0.1:8000/docs



\## Tests



`pytest`



\## Limits and next steps



\- Predicts one day ahead only.

\- No authentication on the API.

\- Cloud deployment is the next step.

