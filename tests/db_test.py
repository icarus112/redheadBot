import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text, select
from decimal import Decimal
import datetime as dt
import pytest


from database.db import async_session
from database.models import WorkTime
from database.service.users import get_or_create_user
# from database.service.work_time import upsert_work_hours
from database.repos.users import get_or_create_user
from database.repos.work_time import (update_work_hours_repo, update_work_tips_repo)

from database.reports import show_status

DATABASE_URL = "postgresql+asyncpg://tracker_user:tracker_pass@localhost:5433/tracker"

@pytest.mark.asyncio
async def test_update_work_hour():
    async with (async_session() as session):
        await update_work_hours_repo(
            session,
            tg_id=6480514308,
            date=dt.date(2026,2,24),
            hour='10')
        await session.commit()

        ok = await update_work_hours_repo(
            session,
            tg_id=6480514308,
            date=dt.date(2026,2,24),
            hour='16')
        await session.commit()
        assert ok is True

        result = await session.execute(
            select(WorkTime).where(WorkTime.user_id==6480514308, WorkTime.date == dt.date(2026, 2, 24)))
        row = result.scalar_one()

        assert row.hour == Decimal('16')

@pytest.mark.asyncio
async def test_update_tips():
    async with async_session() as session:
        await update_work_tips_repo(
            session, tg_id=6480514308, date=dt.date(2026,2,24),
            tips="1000"
        )
        await session.commit()

        ok = await update_work_tips_repo(
            session, tg_id=6480514308, date=dt.date(2026,2,24),
            tips="3000"
        )
        await session.commit()
        assert ok is True
        res = await session.execute(
            select(WorkTime).where(WorkTime.user_id==6480514308, WorkTime.date == dt.date(2026, 2, 24))
        )
        row = res.scalar_one()
        assert row.tips == Decimal("3000")

# async def test_status():
#     status = await show_status(6480514308)
#     print(status)

# async def test_creating():
#     greeting, flag = await get_or_create_user("Atlant744", 6480514308)
#     print(f"greeting:{greeting}")
#     print(f"flag:{flag}")
#
# async def test_upsert_work_hour():
#     await upsert_work_hours(tg_id=6480514308, date=dt.date(2026,2,24), hour='15')
#
# if __name__ == "__main__":
#     asyncio.run(test_upsert_work_hour())

# async def main():
#     engine = create_async_engine(DATABASE_URL, echo=False)
#     async with engine.begin() as conn:
#         res = await conn.execute(text("SELECT 1"))
#         print("DB OK:", res.scalar())
#     await engine.dispose()