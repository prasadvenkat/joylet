import sqlite3
import asyncio
from database import engine
from models import Base
from sqlalchemy import select, text
from database import async_session

async def check_db():
    async with async_session() as session:
        # Check users
        result = await session.execute(text("SELECT id, email, email_verified, display_name FROM users"))
        users = result.fetchall()
        print("Users in database:")
        for user in users:
            print(f"  ID: {user[0]}, Email: {user[1]}, Verified: {user[2]}, Name: {user[3]}")
        
        # Check verification tokens
        result = await session.execute(text("SELECT token, user_id, expires_at FROM email_verification_tokens"))
        tokens = result.fetchall()
        print("\nVerification tokens:")
        for token in tokens:
            print(f"  Token: {token[0]}, User ID: {token[1]}, Expires: {token[2]}")

if __name__ == "__main__":
    asyncio.run(check_db())
