from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
import os

# Allow overriding via env var for docker vs local
DATABASE_DIR = os.getenv("DATABASE_HOST", "localhost")
DATABASE_URL = f"postgresql+asyncpg://user:password@{DATABASE_DIR}:5432/bttf_pricing"

engine = create_async_engine(
    DATABASE_URL,
    echo=True, # Set to False in production
)

async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)
