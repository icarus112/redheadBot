from sqlalchemy.ext.asyncio import AsyncSession
from database.funcs import parse_text_to_decimal, parse_date
from sqlalchemy import select, insert, DateTime, delete, text, update, values

import datetime as dt
from database.models import WorkTime

async def delete_date_repo(session: AsyncSession,wd: str, tg_id: int):
    wd = parse_date(wd)
    stmt = delete(WorkTime).where(
        WorkTime.user_id == tg_id,
                    WorkTime.date == wd)
    result = await session.execute(stmt)

    return result

async def get_time_period_repo(session: AsyncSession,tg_id: int,
                               date_from: str, date_to: str):
    stmt = (
        select(WorkTime).where(
            WorkTime.user_id == tg_id,
            WorkTime.date.between(parse_date(date_from), parse_date(date_to))
        )
        .order_by(WorkTime.date)
    )

    result = await session.execute(stmt)
    return result.scalars().all()

async def insert_time_repo(session: AsyncSession,
                      tg_id: int, date: dt.datetime,
                      hour: str, tips: str = "0") -> None:
    wt = WorkTime(
        user_id=tg_id,
        date=date,
        hour=parse_text_to_decimal(hour),
        tips=parse_text_to_decimal(tips)
    )

    session.add(wt)

async def update_work_hours_repo(
        session: AsyncSession,
        tg_id: int,
        date: dt.date,
        hour: str)->bool:
    stmt = (
        update(WorkTime)
        .where(
            WorkTime.user_id == tg_id,
            WorkTime.date == date
        )
        .values(hour=parse_text_to_decimal(hour))
    )

    result = await session.execute(stmt)
    return result.rowcount > 0

async def update_work_tips_repo(
    session: AsyncSession,
            tg_id: int,
            date: dt.date,
            tips: str)->bool:
    stmt = (
        update(WorkTime)
        .where(WorkTime.user_id == tg_id,
               WorkTime.date == date)
        ).values(tips=parse_text_to_decimal(tips))

    result = await session.execute(stmt)
    return result.rowcount > 0

async def update_work_date_repo(
        session: AsyncSession,
        tg_id: int,
        old_date: dt.date,
        new_date: dt.date) -> bool:
    stmt = (update(WorkTime)
            .where(WorkTime.user_id==tg_id,
                   WorkTime.date == old_date)
            ).values(date=new_date)
    result = await session.execute(stmt)
    return result.rowcount > 0
