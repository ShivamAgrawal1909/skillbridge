import asyncio
import uuid
from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.security import hash_password
from sqlalchemy import select


async def main():
    async with SessionLocal() as db:
        result = await db.execute(
            select(User).where(User.email == 'admin@skillbridge.com')
        )
        if result.scalar_one_or_none():
            print("Admin already exists")
            return

        admin = User(
            id=uuid.uuid4(),
            email='admin@skillbridge.com',
            password_hash=hash_password('Admin@1234'),
            full_name='SkillBridge Admin',
            role=UserRole.admin,
            is_verified=True,
        )
        db.add(admin)
        await db.commit()
        print("Admin created successfully")


asyncio.run(main())