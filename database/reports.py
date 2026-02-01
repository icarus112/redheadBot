import datetime as dt

from pydantic.v1.datetime_parse import parse_date
from sqlalchemy import select, insert, DateTime, delete, text, update
from sqlalchemy.orm import (Session, selectinload)
from sqlalchemy.dialects.postgresql import insert
from decimal import Decimal
import asyncio
from conf import async_session
from database.models import User, WorkTime
from database.funcs import parse_hours, parse_date, get_date, dates_for_status

async def get_or_create_user(name:str, tg_id: int) -> str:
    async with (async_session() as session):
        stmt = (select(User)
                .where(User.tg_id == tg_id))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user:
            greeting = f"приветсвую тебя {name} сновa, у тебя есть здесь учетная запись"
            flag = False
            return greeting, flag

        user = User(tg_id=tg_id, name=name)
        session.add(user)
        await session.commit()
        await session.refresh(user)
        greeting = f"приветсвую тебя {name}, этот бот был создан для трекинга рабочего времени"
        flag = True
        return greeting, flag

async def set_rate(tg_id: int, rate: int):
    async with async_session() as session:
        stmt = (select(User)
                .where(User.tg_id == tg_id))
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if user is None:
            raise ValueError("User not found")

        user.rate = rate
        await session.commit()

async def set_tips(tg_id: int, value: bool):
    async with async_session() as session:
        stmt = (update(User)
                .where(User.tg_id == tg_id)
                .values(user_tips=value)
                )
        await session.execute(stmt)
        await session.commit()

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

# async def test3():
#     user = await get_user_with_times(6480514308)
#     print(user.rate)
#
# asyncio.run(test3())

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

async def show_status(tg_id: int) -> str:
    dates = dates_for_status()
    user = await get_user_with_times(tg_id=tg_id)
    rate = user.rate
    text = f'Ваша ставка: {rate}\n'
    text += 'Статус по периодам\n\n'
    for d in dates:
        res = await get_time_period(tg_id = tg_id, date_from=d[0], date_to=d[1])
        text +=f"\u21a6на период {d[0]} - {d[1]}\n"
        if len(res) == 0:
            text +="записей нету\n\n"
        else:
            k = 0
            for r in res:
                text +=f"\u2022🗓 {r.date.strftime('%d.%m')} | {r.hour} ч\n"
                k += r.hour

            text +=f"\n⌛Итого часов: {k}\n ч"
            text +=f"💸В сумме: {rate*k} ₽\n\n"
    return text

async def test():
    res = await get_time_period(6480514308, date_from='01', date_to='15')
    for r in res:
        print("RESULT: ", r.date, "hours", r.hour)
# asyncio.run(test())
