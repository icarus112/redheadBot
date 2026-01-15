import datetime as dt

from pydantic.v1.datetime_parse import parse_date
from sqlalchemy import select, insert, DateTime, delete, text
from sqlalchemy.orm import (Session, selectinload)
from sqlalchemy.dialects.postgresql import insert
from decimal import Decimal
import asyncio
from conf import async_session
from database.models import User, WorkTime
from database.funcs import parse_hours, pars_date, get_date

async def get_or_create_user(name:str, tg_id: int) -> str:
    async with (async_session() as session):
        stmt = (select(User)
                .where(User.tg_id == tg_id))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        if user:
            greeting = f"приветсвую тебя {name} сновa, у тебя есть здесь учетная запись"
            return greeting

        user = User(tg_id=tg_id, name=name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        greeting = f"приветсвую тебя {name}, этот бот был создан для трекинга рабочего времени"
        return greeting

async def insert_time1(tg_id: int, date: dt.datetime, hour: str) -> None:
    async with(async_session() as session):
        wt = WorkTime(
            user_id = tg_id,
            date=date,
            hour=parse_hours(hour)
        )

        session.add(wt)
        await session.flush()
        await session.commit()

async def test():
    await insert_time1(6480514308, dt.date(2026,2,5), "12,0")

# asyncio.run(test())

async def delete_user(tg_id: int) -> int:
    async with async_session() as session:
        stmt = delete(User).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        await session.commit()

        return result.rowcount()

# async def delete():
#     await delete_user(6480514308)

# asyncio.run(delete())

async def checking():
    async with async_session() as session:
        dbname = await session.scalar(text("select current_database()"))
        port = await session.scalar(text("select inet_server_port()"))
        usercnt = await session.scalar(text("select count(*) from users"))
        print("DB:", dbname, "PORT:", port, "users:", usercnt)

# asyncio.run(checking())

async def get_user_with_times(tg_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .where(User.tg_id == tg_id)
            .options(selectinload(User.work_times))
        )
        return result.scalar_one_or_none()


# asyncio.run(get_date('3', 6480514308))

async def delete_date(wd: str, tg_id: int):
    async with async_session() as session:
        wd = pars_date(wd)
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


# asyncio.run(delete_date('3', 6480514308))
