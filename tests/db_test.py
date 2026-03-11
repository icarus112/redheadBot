import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import text, select, delete
from decimal import Decimal
import datetime as dt
import pytest
from database.models import User

from database.db import async_session
from database.models import WorkTime
from database.repos.work_time import (update_work_hours_repo, update_work_tips_repo,
                                      update_work_date_repo, insert_time_repo,
                                      get_time_period_repo)

from database.reports import show_status

DATABASE_URL = "postgresql+asyncpg://tracker_user:tracker_pass@localhost:5433/tracker"


async def ensure_user(session, tg_id: int, name: str = "test") -> None:
    stmt = (
        insert(User)
        .values(tg_id=tg_id, name=name)
        .on_conflict_do_nothing(index_elements=[User.tg_id])
    )
    await session.execute(stmt)
    await session.flush()  # чтобы FK точно видел User

@pytest.mark.asyncio
async def test_update_work_hour(session):
    tg_id = 999999991
    await ensure_user(session, tg_id)

    session.add(WorkTime(user_id=tg_id,
                         date=dt.date(2016, 2, 24),
                         hour=Decimal("10.00"), tips=Decimal("0")))
    await session.flush()

    ok = await update_work_hours_repo(session, tg_id=tg_id,
                                      date=dt.date(2016, 2, 24),
                                      hour="16")
    assert ok is True

    res = await session.execute(select(WorkTime)
                                .where(WorkTime.user_id == tg_id,
                                       WorkTime.date == dt.date(2016, 2, 24)))
    row = res.scalar_one()
    assert row.hour == Decimal("16.00")

@pytest.mark.asyncio
async def test_update_tips(session):
    tg_id = 999999992
    await ensure_user(session, tg_id)

    session.add(WorkTime(user_id=tg_id,
                         date=dt.date(2012, 2, 24), hour=Decimal("10.00"),
                         tips=Decimal("0")))
    await session.flush()

    ok = await update_work_tips_repo(session, tg_id=tg_id,
                                     date=dt.date(2012, 2, 24),
                                     tips="3000")
    assert ok is True


@pytest.mark.asyncio
async def test_update_date(session):
    tg_id = 999999993
    await ensure_user(session, tg_id)

    session.add(WorkTime(user_id=tg_id,
                         date=dt.date(2016, 2, 24),
                         hour=Decimal("10.00"), tips=Decimal("0")))
    await session.flush()

    ok = await update_work_date_repo(session,
                                     tg_id=tg_id, old_date=dt.date(2016, 2, 24),
                                     new_date=dt.date(2016, 1, 1))
    assert ok is True

    res = await session.execute(select(WorkTime).
                                where(WorkTime.user_id == tg_id,
                                      WorkTime.date == dt.date(2016, 1, 1)))
    row = res.scalar_one()
    assert row.date == dt.date(2016, 1, 1)

@pytest.mark.asyncio
async def test_insert_time(session):
    tg_id=1
    await ensure_user(session, tg_id)

    await insert_time_repo(session=session, tg_id=tg_id,
                           date=dt.datetime(2016, 1, 2),
                           hour="12")

    await session.flush()

    res = await session.execute(select(WorkTime)
                                .where(WorkTime.user_id==tg_id,
                                       WorkTime.date == dt.datetime(2016, 1, 2)))

    row = res.scalar_one()
    assert row.date == dt.date(2016, 1, 2)

# @pytest.mark.asycnio
# async def test_get_time_period(session):
#     tg_id=2
#     await ensure_user(session, tg_id)
#
#     await insert_time_repo(session=session, tg_id=tg_id,
#                            date=dt.datetime(2016, 2, 2),
#                            hour="12")
#     await insert_time_repo(session=session, tg_id=tg_id,
#                            date=dt.datetime(2016, 2, 3),
#                            hour="12")
#
#     result = await get_time_period_repo(session,tg_id=tg_id,
#                                        date_from=dt.datetime(2016, 1, 30),
#                                        date_to=dt.datetime(2016, 2, 10))
#     await session.flush()


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