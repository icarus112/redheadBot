from database.db import async_session
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# Используй тот же URL, что и у тебя (или отдельный test-db URL)
DATABASE_URL = "postgresql+asyncpg://tracker_user:tracker_pass@localhost:5433/tracker"

@pytest_asyncio.fixture
async def session():
    # engine создаётся ВНУТРИ текущего event loop теста
    engine = create_async_engine(DATABASE_URL, echo=False)

    SessionLocal = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with SessionLocal() as s:
        trans = await s.begin()
        try:
            yield s
        finally:
            await trans.rollback()

    await engine.dispose()