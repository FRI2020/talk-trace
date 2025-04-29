from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os


DATABASE_URL_H = "sqlite+aiosqlite:////app/data/db/sqlite/talktrace.db"

# Create async engine for SQLite
engine_h = create_async_engine(DATABASE_URL_H, echo=True)

# Create session factory
AsyncSessionLocal_h = sessionmaker(bind=engine_h, class_=AsyncSession, expire_on_commit=False)

# Dependency to get DB session
async def get_db_h():
    async with AsyncSessionLocal_h() as session:
        yield session
