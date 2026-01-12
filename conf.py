import os
from dotenv import load_dotenv

load_dotenv()

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
TOKEN = ('8445422919:AAG-bzjUWkBu3phkrYSn_xwf4tMVykzMnIo')

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5433")
DB_NAME = os.getenv("DB_NAME", "tracker")
DB_USER = os.getenv("DB_USER", "tracker_user")
DB_PASS = os.getenv("DB_PASS", "tracker_pass")

DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# print("DATABASE_URL =", DATABASE_URL)


