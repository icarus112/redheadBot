import asyncio
from aiogram import Bot, Dispatcher
from conf import TOKEN
import logging
import sys


from app.handlers import router
from database.init_db import init_db

async def main():
    bot = Bot(token=TOKEN, echo=True)
    dp=Dispatcher()
    logging.basicConfig(level=logging.INFO)
    dp.include_router(router)
    await init_db()
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("бот выкл.")