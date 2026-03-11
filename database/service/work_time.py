
from decimal import Decimal
import asyncio
import datetime as dt

from database.repos.work_time import (insert_time_repo, update_work_hours_repo, update_work_tips_repo, update_work_date_repo, get_time_period_repo)
from database.db import async_session
from database.funcs import parse_hours, parse_date
from sqlalchemy import select, delete
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
        try:
            result = await get_time_period_repo(session,tg_id=tg_id,
                                       date_from=date_from,
                                       date_to=date_to)

            return result
        except Exception:
            await session.rollback()
            raise


async def insert_time(tg_id: int, date: dt.datetime, hour: str, tips: str = "0") -> None:
    async with async_session() as session:
        try:
            await insert_time_repo(session, tg_id=tg_id,
                                   date=date, hour=hour,
                                   tips=tips)
            await session.commit()
        except Exception:
            await session.rollback()
            raise

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

async def update_work_tips(tg_id: int, date: dt.date, tips: str)->bool:
    async with async_session() as session:
        try:
            ok = await update_work_tips_repo(
                session,
                tg_id=tg_id,
                date=date,
                tips=tips
            )
            await session.commit()

            return ok
        except Exception:
            await session.rollback()
            raise

async def update_work_date(tg_id: int, old_date: dt.date, new_date: dt.date)->bool:
    async with async_session() as session:
        try:
            ok = await update_work_date_repo(
                session,
                tg_id=tg_id,
                old_date=old_date,
                new_date=new_date,
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