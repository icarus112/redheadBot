from sqlalchemy.dialects.mssql.information_schema import constraints
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import (Session, selectinload)
from sqlalchemy.dialects.postgresql import insert
from decimal import Decimal
import asyncio
import datetime as dt

from database.repos.work_time import update_work_hours_repo
from database.db import async_session
from database.funcs import parse_hours, parse_date, get_date, dates_for_status
from sqlalchemy import select, insert, DateTime, delete, text, update
from database.models import WorkTime

async def delete_date(wd: str, tg_id: int):
    async with async_session() as session:
        wd = parse_date(wd)
        stmt = delete(WorkTime).where(
            WorkTime.user_id == tg_id,
                        WorkTime.date == wd)
        result = await session.execute(stmt)
        await session.commit()

        return result

        if result.rowcount == 0:
            print(f"по запросу {wd}, ничего не найдено")
        else:
            print(f"дата {wd} успешно удалено")

async def get_time_period(tg_id: int, date_from: str, date_to: str):
    async with async_session() as session:

        stmt = (
            select(WorkTime).where(
            WorkTime.user_id == tg_id,
            WorkTime.date.between(parse_date(date_from), parse_date(date_to))
        )
        .order_by(WorkTime.date)
        )

        result = await session.execute(stmt)
        return result.scalars().all()

async def insert_time1(tg_id: int, date: dt.datetime, hour: str, tips: str = "0") -> None:
    async with(async_session() as session):
        wt = WorkTime(
            user_id = tg_id,
            date=date,
            hour=parse_hours(hour),
            tips=parse_hours(tips)
        )

        session.add(wt)
        await session.flush()
        await session.commit()

async def update_work_hours(tg_id: int, date: dt.date, hour: str)->bool:
    async with async_session() as session:
        try:
            ok = await update_work_hours_repo(
                session,
                tg_id=tg_id,
                date=date,
                hour=hour
            )
            await session.commit()

            return ok
        except Exception:
            await session.rollback()
            raise

# async def test():
#     await insert_time1(6480514308, dt.date(2026,2,15), "12,0", "1940")
#
# asyncio.run(test())