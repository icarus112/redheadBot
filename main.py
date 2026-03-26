import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from conf import TOKEN, BOT_PROXY
import logging

from app.handlers.router import router
from database.init_db import init_db

async def main():
    #из-за проблем с сетью приходится использовать прокси
    if BOT_PROXY:
        session = AiohttpSession(proxy=BOT_PROXY)
        bot = Bot(token=TOKEN, session=session)
        print(f"Proxy enabled: {BOT_PROXY}")
    else:
        bot = Bot(token=TOKEN)
        print("Proxy disabled")
    dp=Dispatcher()
    logging.basicConfig(level=logging.DEBUG)
    #в папке handlers много отдельных файлов и поэтому собираются в router
    dp.include_router(router)
    await init_db()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("бот выкл.")