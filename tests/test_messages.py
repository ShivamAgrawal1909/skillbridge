import pytest


@pytest.mark.asyncio
async def test_get_conversations_empty(auth_client):
    response = await auth_client.get("/messages/conversations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_conversations_provider(provider_client):
    response = await provider_client.get("/messages/conversations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_unauthenticated_cannot_get_conversations(client):
    response = await client.get("/messages/conversations")
    assert response.status_code == 403