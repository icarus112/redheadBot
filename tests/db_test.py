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
                                      get_time_period_repo, delete_date_repo)
from database.repos.users import (update_rate_repo)
from database.funcs import parse_text_to_decimal
DATABASE_URL = "postgresql+asyncpg://tracker_user:tracker_pass@localhost:5433/tracker"

#нужен из-за ошибка тестов в одной сессии
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

@pytest.mark.asyncio
async def test_get_time_period(session):
    tg_id=2
    await ensure_user(session, tg_id)

    await insert_time_repo(session=session, tg_id=tg_id,
                           date=dt.datetime(2016, 2, 2),
                           hour="12")
    await insert_time_repo(session=session, tg_id=tg_id,
                           date=dt.datetime(2016, 2, 3),
                           hour="12")

    result = await get_time_period_repo(session,tg_id=tg_id,
                                       date_from="30.01.2016",
                                       date_to="10.02.2016")
    assert len(result) == 2

    await session.flush()

@pytest.mark.asyncio
async def test_delete_date(session):
    tg_id = 3
    await ensure_user(session, tg_id)
    await insert_time_repo(session=session, tg_id=tg_id,
                           date=dt.datetime(2016, 2, 3),
                           hour="12")
    res = await session.execute(select(WorkTime)
                                .where(WorkTime.user_id == tg_id,
                                       WorkTime.date == dt.datetime(2016, 2, 3)))

    row = res.scalar_one()
    assert row.date == dt.date(2016, 2, 3)

    await delete_date_repo(session=session, wd="3.02.2016",tg_id=tg_id)
    res = await session.execute(select(WorkTime)
                                .where(WorkTime.user_id == tg_id,
                                       WorkTime.date == dt.datetime(2016, 2, 3)))
    row = res.scalar_one_or_none()
    assert row == None

@pytest.mark.asyncio
async def test_update_rate(session):
    tg_id = 4
    await ensure_user(session, tg_id)
    await update_rate_repo(session, tg_id, "290")
    result = await session.execute(select(User)
                                   .where(User.tg_id == tg_id))
    row = result.scalar_one_or_none()
    assert row.rate == Decimal('290')