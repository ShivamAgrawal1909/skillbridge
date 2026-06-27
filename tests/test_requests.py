import uuid
import pytest


@pytest.mark.asyncio
async def test_create_request(auth_client):
    pytest.skip("requires seeded categories")


@pytest.mark.asyncio
async def test_get_my_requests(auth_client):
    response = await auth_client.get("/requests")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_provider_cannot_post_request(provider_client):
    response = await provider_client.post("/requests", json={
        "title": "Test",
        "description": "Test description",
        "category_id": str(uuid.uuid4()),
    })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_open_requests_for_provider(provider_client):
    response = await provider_client.get("/requests/open")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_client_cannot_see_open_requests(auth_client):
    response = await auth_client.get("/requests/open")
    assert response.status_code == 403
