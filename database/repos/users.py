from database.funcs import parse_text_to_decimal
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User

async def get_or_create_user_repo(session: AsyncSession, name:str, tg_id: int) -> str:
    stmt = (select(User)
            .where(User.tg_id == tg_id))
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    return user

async def update_rate_repo(session: AsyncSession, tg_id: int, rate: str):
    stmt = (
        update(User)
        .where(User.tg_id == tg_id)
    ).values(rate=parse_text_to_decimal(rate))
    result = await session.execute(stmt)
    return result.rowcount > 0