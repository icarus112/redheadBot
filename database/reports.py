import datetime as dt

from pydantic.v1.datetime_parse import parse_date
from sqlalchemy import select, insert, DateTime, delete, text, update
from sqlalchemy.orm import (Session, selectinload)
from sqlalchemy.dialects.postgresql import insert
from decimal import Decimal
import asyncio
from database.db import async_session
from database.models import User, WorkTime
from database.funcs import parse_hours, parse_date, get_date, dates_for_status
from database.repo.users import get_user_with_times
from database.repo.work_time import get_time_period

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

# async def test3():
#     user = await get_user_with_times(6480514308)
#     print(user.user_tips)
#
# asyncio.run(test3())

async def show_status(tg_id: int) -> str:
    dates = dates_for_status()
    user = await get_user_with_times(tg_id=tg_id)
    bool_tips = user.user_tips
    rate = user.rate
    text = f'Ваша ставка: {rate}\n'
    text += 'Статус по периодам\n\n'
    for d in dates:
        res = await get_time_period(tg_id = tg_id, date_from=d[0], date_to=d[1])
        text +=f"\u21a6на период {d[0]} - {d[1]}\n"
        if len(res) == 0:
            text +="записей нету\n\n"
        else:
            k = Decimal("0")
            tip = Decimal("0")
            lines = []
            for r in res:
                line = f"\u2022🗓 {r.date.strftime('%d.%m')} | {r.hour:>4.1f} ч"
                if bool_tips:
                    line += f" | {r.tips:.0f} ₽\n"
                    lines.append(line)

                else:
                    line += "\n"
                    lines.append(line)

                k += r.hour
                tip += r.tips
            lines.append(f"\n⌛часы: {k:.0f} ч\n")
            lines.append(f"💸Итого: {rate * k:.0f} ₽\n")
            if bool_tips:
                lines.append(f"🪙чаевые:{tip} ₽\n")
                lines.append(f"💰В сумме с чаем: {(rate * k) + tip:.0f} ₽\n")
            text += "<pre>\n" + "\n".join(lines) + "\n</pre>\n"
    return text

# async def test():
#     res = await get_time_period(6480514308, date_from='01', date_to='15')
#     for r in res:
#         print("RESULT: ", r.date, "hours", r.hour)
# asyncio.run(test())
