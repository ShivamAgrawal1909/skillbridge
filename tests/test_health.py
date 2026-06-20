import pytest


@pytest.mark.asyncio
async def test_health(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_security_headers(client):
    response = await client.get("/health")
    assert "x-frame-options" in response.headers
    assert "x-content-type-options" in response.headers
    assert "content-security-policy" in response.headers
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-content-type-options"] == "nosniff"