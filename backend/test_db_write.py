import asyncio
from database import async_session
from models import User
import uuid

async def test_write():
    async with async_session() as session:
        # Create a test user
        test_user = User(
            id=uuid.uuid4(),
            email="test_write@example.com",
            password_hash="test_hash",
            display_name="Test Write User",
            handle="test_write_user",
            email_verified=True
        )
        
        print("Adding user to session...")
        session.add(test_user)
        
        print("Committing...")
        await session.commit()
        
        print(f"User created with ID: {test_user.id}")
        
        # Query to verify
        from sqlalchemy import select
        stmt = select(User).where(User.email == "test_write@example.com")
        result = await session.execute(stmt)
        found_user = result.scalar_one_or_none()
        
        if found_user:
            print(f"User found in database: {found_user.email}")
        else:
            print("User NOT found in database!")

if __name__ == "__main__":
    asyncio.run(test_write())
