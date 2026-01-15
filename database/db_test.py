import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://tracker_user:tracker_pass@localhost:5433/tracker"

async def main():
    engine = create_async_engine(DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        res = await conn.execute(text("SELECT 1"))
        print("DB OK:", res.scalar())
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
