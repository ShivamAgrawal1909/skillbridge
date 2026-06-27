@pytest.mark.asyncio
async def test_create_request(auth_client):
    
    from app.database import SessionLocal
    from app.models.category import Category
    from sqlalchemy import select

    async with SessionLocal() as db:
        result = await db.execute(select(Category).limit(1))
        category = result.scalar_one_or_none()

    if not category:
        return  

    response = await auth_client.post("/requests", json={
        "title": "Test website project",
        "description": "Need a simple website for my business",
        "category_id": str(category.id),
        "budget_min": 5000,
        "budget_max": 15000,
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Test website project"
    assert data["status"] == "open"