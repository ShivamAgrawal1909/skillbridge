import uuid

import pytest


def unique_email():
    return f"test_{uuid.uuid4().hex[:8]}@test.com"


@pytest.mark.asyncio
async def test_register(client):
    response = await client.post("/auth/register", json={
        "email": unique_email(),
        "password": "Test@1234",
        "full_name": "New User",
        "role": "client",
    })
    assert response.status_code == 201
    data = response.json()
    assert data["role"] == "client"
    assert "password" not in data
    assert "password_hash" not in data


@pytest.mark.asyncio
async def test_register_duplicate_email(client):
    email = unique_email()
    payload = {
        "email": email,
        "password": "Test@1234",
        "full_name": "Dup User",
        "role": "client",
    }
    await client.post("/auth/register", json=payload)
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


@pytest.mark.asyncio
async def test_login(client):
    email = unique_email()
    await client.post("/auth/register", json={
        "email": email,
        "password": "Test@1234",
        "full_name": "Login User",
        "role": "client",
    })
    response = await client.post("/auth/login", json={
        "email": email,
        "password": "Test@1234",
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_wrong_password(client):
    email = unique_email()
    await client.post("/auth/register", json={
        "email": email,
        "password": "Test@1234",
        "full_name": "Wrong User",
        "role": "client",
    })
    response = await client.post("/auth/login", json={
        "email": email,
        "password": "WrongPassword",
    })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_me(auth_client):
    response = await auth_client.get("/auth/me")
    assert response.status_code == 200
    assert "email" in response.json()


@pytest.mark.asyncio
async def test_me_no_token(client):
    response = await client.get("/auth/me")
    assert response.status_code == 403