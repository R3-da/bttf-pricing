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

@pytest.mark.asyncio
async def test_calculate_price_missing_movie(client):
    cart_content = "Back to the Future 1\nUnknown Movie"
    response = await client.post(
        "/api/v1/price",
        content=cart_content,
        headers={"Content-Type": "text/plain"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Movie(s) not found: Unknown Movie"}

@pytest.mark.asyncio
async def test_calculate_price_multiple_missing_movies(client):
    cart_content = "Back to the Future 1\nUnknown Movie 1\nUnknown Movie 2"
    response = await client.post(
        "/api/v1/price",
        content=cart_content,
        headers={"Content-Type": "text/plain"}
    )
    assert response.status_code == 404
    # The set logic might order them differently, but we sorted them in service code.
    # Expect alphabetical order "Unknown Movie 1, Unknown Movie 2"
    assert response.json() == {"detail": "Movie(s) not found: Unknown Movie 1, Unknown Movie 2"}
