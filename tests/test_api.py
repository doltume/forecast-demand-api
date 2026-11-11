from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_requires_store_and_item():
    response = client.get("/predict")
    assert response.status_code == 422


def test_predict_rejects_non_integer_ids():
    response = client.get("/predict", params={"store_id": "abc", "item_id": 1})
    assert response.status_code == 422