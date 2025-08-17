import asyncio
from database import async_session
from models import User
from sqlalchemy import select

async def check_users():
    async with async_session() as session:
        stmt = select(User)
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        print(f"Found {len(users)} users via application:")
        for user in users:
            print(f"  - {user.email} ({user.display_name}) - Verified: {user.email_verified}")

if __name__ == "__main__":
    asyncio.run(check_users())
