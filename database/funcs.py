import datetime as dt
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from conf import async_session
from database.models import WorkTime, User
from sqlalchemy import select

def parse_hours(text: str) -> Decimal:
    t = text.strip().replace(",", ".")
    try:
        value = Decimal(t)
    except InvalidOperation:
        raise ValueError("нужно число например 1.5")

    if value <= 0:
        raise ValueError("Часы должны быть положительными и больше 0")

    return value.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)

def pars_date(wd: str):
    wd = wd.split(".")
    month = dt.date.today().month
    year = dt.date.today().year
    new_wd = ''
    for el in wd:
        if el == "":
            wd.remove(el)
    if len(wd) == 1:
        new_wd = f"{year}.{month}.{wd[0]}"
    if len(wd) == 2:
        new_wd = f"{year}.{wd[1]}.{wd[0]}"
    if len(wd) == 3:
        new_wd = f"{wd[2]}.{wd[1]}.{wd[0]}"

    return dt.datetime.strptime(new_wd, "%Y.%m.%d").date()



def from_date_to_str(wd: dt.datetime) -> str:
    year = wd.year
    month = wd.month
    day = wd.day
    return f"{day}.{month}.{year}"

async def get_date(wd: str, tg_id: int) -> dt.date | None :
    async with async_session() as session:
        wd = pars_date(wd)
        stmt = (select(WorkTime)
                .where(WorkTime.date == wd, WorkTime.user_id == tg_id)
                )

        result = await session.execute(stmt)
        result = result.scalar_one_or_none()
        if result is None:
            print(f"по запросу {wd}, ничего не найдено")
        else:
            print("найдено:", result.date)
            return result.date

# async def get_time_period(tg_id: int, date_from: dt.date, date_to: dt.date):
#     async with async_session() as session:


# async def get_total_hours(tg_id: int) -> Decimal:
#     async with async_session() as session:
#         total = await session.scalar(
#             select(func.coalesce(func.sum(WorkTime.hour), 0))
#             .where(WorkTime.user_id == tg_id)
#         )
#         return total


# async def test():
#     user = await get_user_with_times(6480514308)
#
#     if not user:
#         print("Пользователь не найден")
#         return
#
#     print(user.get_status())
#
# asyncio.run(test())

