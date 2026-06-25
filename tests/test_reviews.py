import pytest


@pytest.mark.asyncio
async def test_get_provider_reviews(client):
    # public endpoint — no auth needed
    # use Rahul Developer's user_id from DB
    provider_id = "ed1811c3-7f37-47fd-b86f-b0dc7098bed8"
    response = await client.get(f"/reviews/provider/{provider_id}")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_review_requires_auth(client):
    response = await client.post("/reviews", params={
        "request_id": "cb6944cd-e2c2-4241-8604-ed50951a8b01",
        "reviewee_id": "ed1811c3-7f37-47fd-b86f-b0dc7098bed8"
    }, json={"rating": 5, "comment": "Great work"})
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_invalid_rating(auth_client):
    response = await auth_client.post("/reviews", params={
        "request_id": "cb6944cd-e2c2-4241-8604-ed50951a8b01",
        "reviewee_id": "ed1811c3-7f37-47fd-b86f-b0dc7098bed8"
    }, json={"rating": 6, "comment": "Great"})
    assert response.status_code == 422