from database.db import async_session
from database.repos.users import get_or_create_user_repo, update_rate_repo
from sqlalchemy import select, insert, DateTime, delete, text, update
from sqlalchemy.orm import (Session, selectinload)

from database.models import User

async def get_or_create_user(name:str, tg_id: int) -> str:
    async with (async_session() as session):
        try:
            user = await get_or_create_user_repo(session,name,tg_id)
            if user:
                greeting = (f"приветсвую тебя {name} сновa, у тебя есть здесь учетная запись, если есть вопросы ->"
                            f"напиши мне /help")
                flag = False
                return greeting, flag

            user = User(tg_id=tg_id, name=name)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            greeting = (f"приветсвую тебя {name}, этот бот был создан для трекинга рабочего времени если есть вопросы ->",
                       f"напиши мне /help")
            flag = True
            return greeting, flag
        except Exception:
            await session.rollback()
            raise

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

async def update_rate(tg_id: int, rate: str):
    async with async_session() as session:
        try:
            ok = await update_rate_repo(session=session,
                                        tg_id=tg_id, rate=rate)
            await session.commit()
            return ok
        except Exception:
            await session.rollback()
            raise