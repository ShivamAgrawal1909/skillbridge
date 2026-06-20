import asyncio
import uuid

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as c:
        yield c


@pytest_asyncio.fixture
async def auth_client(client):
    email = f"client_{uuid.uuid4().hex[:8]}@test.com"
    await client.post("/auth/register", json={
        "email": email,
        "password": "Test@1234",
        "full_name": "Test User",
        "role": "client",
    })
    response = await client.post("/auth/login", json={
        "email": email,
        "password": "Test@1234",
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


@pytest_asyncio.fixture
async def provider_client(client):
    email = f"provider_{uuid.uuid4().hex[:8]}@test.com"
    await client.post("/auth/register", json={
        "email": email,
        "password": "Test@1234",
        "full_name": "Test Provider",
        "role": "provider",
    })
    response = await client.post("/auth/login", json={
        "email": email,
        "password": "Test@1234",
    })
    token = response.json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client