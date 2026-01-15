from sqlalchemy.orm import selectinload

from conf import async_session
from database.models import User, WorkTime
import asyncio
from sqlalchemy import select
from decimal import Decimal
import datetime as dt

async def main():
    async with (async_session() as session):
        '''CREATE'''
        user = User(
            tg_id=123321,
            name="Gandon"
        )
        # session.add(user)
        #
        # await session.commit()

        '''CREATE_2'''
        user = User(tg_id=123322, name="Gandon2")
        # session.add(user)
        # await session.commit()
        # await session.refresh(user)

        '''INSERT'''
        wt = WorkTime(
            user_id=user.id,
            date=dt.date.today(),
            hour=Decimal("6.0")
        )
        # session.add(wt)
        # await session.commit()

        '''SELECT'''
        stmt = (select(User)
                .where(User.id == 1)
                .options(selectinload(User.work_times))
                )

        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        print(user.id, user.name)
        print(user.work_times[0].date)

# asyncio.run(main())

async def test():
    async with (async_session() as session):
        stmt = select(User).options(selectinload(User.work_times))
        result = await session.execute(stmt)

        users = result.scalars().all()

        for user in users:
            print(user.id, user.tg_id, user.name)
            for wt in user.work_times:
                print(wt.date, wt.hour)

asyncio.run(test())

async def test2():
    async with(async_session() as session):
        stmt = select(WorkTime)
        result = await session.execute(stmt)

        work_times = result.scalars().all()
        for wt in work_times:
            print(wt.date)

# asyncio.run(test2())

'''DELETE'''


async def delete_user_by_tg_id(tg_id: int) -> bool:
    async with async_session() as session:
        # Находим пользователя
        user = await session.scalar(
            select(User).where(User.tg_id == tg_id)
        )

        if not user:
            return False  # Пользователь не найден

        await session.delete(user)
        await session.commit()
        return True


# Использование:
# deleted = await delete_user_by_tg_id(123321)
# print(f"Удален: {deleted}")

'''DELETE2'''
from sqlalchemy import delete


async def delete_user_by_tg_id(tg_id: int) -> int:
    async with async_session() as session:
        stmt = delete(User).where(User.tg_id == tg_id)
        result = await session.execute(stmt)
        await session.commit()

        return result.rowcount  # Возвращает количество удаленных строк


# Использование:
# count = await delete_user_by_tg_id(123321)
# print(f"Удалено записей: {count}")

