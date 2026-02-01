from database.db import async_session
from database.funcs import parse_hours, parse_date, get_date, dates_for_status
from sqlalchemy import select, insert, DateTime, delete, text, update
from sqlalchemy.orm import (Session, selectinload)
from sqlalchemy.dialects.postgresql import insert
from decimal import Decimal
import asyncio
import datetime as dt
from database.models import User

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

async def delete_user(tg_id: int) -> int:
    async with async_session() as session:
        stmt = delete(User).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        await session.commit()

        return result.rowcount()

async def get_user_with_times(tg_id: int) -> User | None:
    async with async_session() as session:
        result = await session.execute(
            select(User)
            .where(User.tg_id == tg_id)
            .options(selectinload(User.work_times))
        )
        return result.scalar_one_or_none()