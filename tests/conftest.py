import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlmodel import SQLModel
from typing import AsyncGenerator
from datetime import date

from src.main import app
from src.core.database import get_session
from src.domain.sql_models import Series, Movie

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function")
async def session() -> AsyncGenerator[AsyncSession, None]:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    
    async with TestingSessionLocal() as session:
        # Seed test data
        bttf_series = Series(title="Back to the Future", release_order=False)
        session.add(bttf_series)
        await session.commit()
        await session.refresh(bttf_series)
        
        movies = [
            Movie(title="Back to the Future 1", release_date=date(1985, 7, 3), duration_min=116, price=15.0, series=bttf_series, series_index=1),
            Movie(title="Back to the Future 2", release_date=date(1989, 11, 22), duration_min=108, price=15.0, series=bttf_series, series_index=2),
            Movie(title="Back to the Future 3", release_date=date(1990, 5, 25), duration_min=118, price=15.0, series=bttf_series, series_index=3),
            Movie(title="La chèvre", release_date=date(1981, 12, 9), duration_min=91, price=20.0),
        ]
        session.add_all(movies)
        await session.commit()
        
        yield session
    
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)

@pytest_asyncio.fixture(scope="function")
async def client(session) -> AsyncGenerator[AsyncClient, None]:
    async def override_get_session():
        yield session
    
    app.dependency_overrides[get_session] = override_get_session
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
