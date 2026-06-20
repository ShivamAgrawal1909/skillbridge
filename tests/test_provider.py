import pytest


@pytest.mark.asyncio
async def test_create_provider_profile(provider_client):
    response = await provider_client.post("/providers/profile", json={
        "bio": "Expert Python developer",
        "tagline": "I build clean APIs",
        "hourly_rate": 500,
        "years_experience": 2,
        "location": "Lucknow",
        "skill_ids": [],
    })
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "pending"
    assert data["tagline"] == "I build clean APIs"
    assert data["location"] == "Lucknow"


@pytest.mark.asyncio
async def test_client_cannot_create_provider_profile(auth_client):
    response = await auth_client.post("/providers/profile", json={
        "bio": "I am a client not a provider",
        "tagline": "Should fail",
        "hourly_rate": 500,
        "years_experience": 1,
        "location": "Delhi",
        "skill_ids": [],
    })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_search_providers(client):
    response = await client.get("/providers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)