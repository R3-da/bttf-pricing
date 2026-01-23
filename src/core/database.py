import os
import logging
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()


# Database configuration from environment variables
# Helper function to handle empty strings
def get_env_or_default(key: str, default: str = None) -> str:
    """Get environment variable, treating empty strings as None."""
    value = os.getenv(key, default)
    return value if value else default


POSTGRES_USER = get_env_or_default("POSTGRES_USER")
POSTGRES_PASSWORD = get_env_or_default("POSTGRES_PASSWORD")
POSTGRES_DB = get_env_or_default("POSTGRES_DB")
DATABASE_HOST = get_env_or_default("DATABASE_HOST")
DATABASE_PORT = get_env_or_default("DATABASE_PORT", "5432")
DB_ECHO = os.getenv("DB_ECHO", "False").lower() == "true"

# Check for missing environment variables
missing_vars = [
    var
    for var, val in {
        "POSTGRES_USER": POSTGRES_USER,
        "POSTGRES_PASSWORD": POSTGRES_PASSWORD,
        "POSTGRES_DB": POSTGRES_DB,
        "DATABASE_HOST": DATABASE_HOST,
    }.items()
    if not val
]

if missing_vars:
    logger.error(
        f"Missing environment variables: {', '.join(missing_vars)}. DB connection might fail."
    )

# Fallback values for URL construction if missing
DATABASE_URL = (
    f"postgresql+asyncpg://"
    f"{POSTGRES_USER or 'user'}:{POSTGRES_PASSWORD or 'password'}@"
    f"{DATABASE_HOST or 'localhost'}:{DATABASE_PORT or '5432'}/"
    f"{POSTGRES_DB or 'bttf_pricing'}"
)

try:
    engine = create_async_engine(
        DATABASE_URL,
        echo=DB_ECHO,  # Configured via environment variable
    )
except Exception as e:
    logger.error(f"Failed to create database engine: {e}")
    # Create a dummy engine or handle it gracefully
    engine = None

async_session_factory = None
if engine:
    async_session_factory = async_sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    if not async_session_factory:
        logger.error(
            "Database session factory is not initialized. DB operations will fail."
        )
        return
    try:
        async with async_session_factory() as session:
            yield session
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {e}")
        raise


async def init_db():
    if not engine:
        logger.error("Database engine is not initialized. Cannot initialize DB.")
        return
    try:
        async with engine.begin() as conn:
            # await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
