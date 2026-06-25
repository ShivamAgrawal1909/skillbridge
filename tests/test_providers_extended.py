import pytest


@pytest.mark.asyncio
async def test_search_providers_empty(client):
    response = await client.get("/providers")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_search_providers_by_location(client):
    response = await client.get("/providers", params={"location": "Lucknow"})
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_search_providers_by_max_rate(client):
    response = await client.get("/providers", params={"max_rate": 1000})
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_provider_not_found(client):
    import uuid
    fake_id = str(uuid.uuid4())
    response = await client.get(f"/providers/{fake_id}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_client_cannot_create_provider_profile(auth_client):
    response = await auth_client.post("/providers/profile", json={
        "bio": "test",
        "tagline": "test",
        "hourly_rate": 500,
        "years_experience": 1,
        "location": "Delhi",
        "skill_ids": [],
    })
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_provider_profile_update(provider_client):
    response = await provider_client.post("/providers/profile", json={
        "bio": "Updated bio for testing",
        "tagline": "Updated tagline",
        "hourly_rate": 750,
        "years_experience": 3,
        "location": "Mumbai",
        "skill_ids": [],
    })
    assert response.status_code == 201
    assert response.json()["location"] == "Mumbai"