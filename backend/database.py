from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
import os

# Use SQLite for local development if no DATABASE_URL is set
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./positive_journal.db")

engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=True if os.getenv("DEBUG") else False
)

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

async def init_db():
    from models import Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
