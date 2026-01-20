from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text

def test_calculate_price_api():
    cart_content = "Back to the Future 1\nBack to the Future 2\nBack to the Future 3"
    response = client.post(
        "/api/v1/price",
        content=cart_content,
        headers={"Content-Type": "text/plain"}
    )
    assert response.status_code == 200
    assert response.json() == {"price": 36.0}

def test_calculate_price_api_empty():
    response = client.post(
        "/api/v1/price",
        content="", # Use content instead of data for raw body in httpx/TestClient
        headers={"Content-Type": "text/plain"}
    )
    assert response.status_code == 200
    assert response.json() == {"price": 0.0}
