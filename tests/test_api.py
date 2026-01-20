import pytest

@pytest.mark.asyncio
async def test_read_main(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text

@pytest.mark.asyncio
async def test_calculate_price_api(client):
    cart_content = "Back to the Future 1\nBack to the Future 2\nBack to the Future 3"
    response = await client.post(
        "/api/v1/price",
        content=cart_content,
        headers={"Content-Type": "text/plain"}
    )
    assert response.status_code == 200
    assert response.json() == {"price": 36.0}

@pytest.mark.asyncio
async def test_calculate_price_api_empty(client):
    response = await client.post(
        "/api/v1/price",
        content="", 
        headers={"Content-Type": "text/plain"}
    )
    assert response.status_code == 200
    assert response.json() == {"price": 0.0}
