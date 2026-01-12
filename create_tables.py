import asyncio
import datetime as dt

from sqlalchemy import select, text
from conf import async_session
from database.models import User
from database.reports import insert_time1


async def main():
    tg_id = 6480514308

    async with async_session() as session:
        # Отладка: убедимся, что смотрим в правильную БД
        dbname = await session.scalar(text("select current_database()"))
        port = await session.scalar(text("select inet_server_port()"))
        print("DB:", dbname, "PORT:", port)

        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user is None:
            user = User(tg_id=tg_id, name="Atlant744")
            session.add(user)
            await session.commit()
            print("User created")
        else:
            print("User exists:", user.name)

    await insert_time1(tg_id, dt.date(2026, 1, 3), 5.0)
    print("WorkTime inserted OK")


if __name__ == "__main__":
    asyncio.run(main())
