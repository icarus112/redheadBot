from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State

from database.funcs import (parse_date, dates_for_status)
from database.service.users import get_user_with_times
from database.reports import show_status, show_status_for_period
import app.keyboards as kb

router = Router()

class GetPeriod(StatesGroup):
    from_date = State()
    to_date = State()

@router.message(F.text == "👤Показать статус")
async def status(message: Message):
    await message.answer("выберите вариант вывода:", reply_markup=kb.status)

@router.message(F.text == "по 15 дням")
async def status(message: Message):
    dates = dates_for_status()
    user = await get_user_with_times(message.from_user.id)

    if not user:
        print("Пользователь не найден")
        return
    # 6480514308
    await message.answer( await show_status(message.from_user.id), parse_mode="HTML")
    await message.answer("главное меню:", reply_markup=kb.main)

@router.message(F.text == "от _ до _")
async def for_the_period(message: Message, state: FSMContext):
    await message.answer("введите начальную дату:")
    await state.set_state(GetPeriod.from_date)

@router.message(GetPeriod.from_date)
async def from_date(message: Message, state: FSMContext):
    try:
        date_obj = message.text
    except Exception:
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return

    await state.update_data(date=date_obj)
    await message.answer(f"успешно сохранено как {parse_date(date_obj).strftime('%d.%m.%Y')}")
    await state.set_state(GetPeriod.to_date)
    await message.answer("теперь введи конечную дату:")

@router.message(GetPeriod.to_date)
async def to_date(message: Message, state: FSMContext):
    try:
        date_2_obj = message.text
    except Exception:
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return

    data = await state.get_data()  # сохряняем все данные FSM в виде словаря
    date_obj = data.get("date")  # находим date
    if date_obj is None:
        await message.answer("что то пошло не так, начни заново")
        await state.clear()
        return

    await message.answer(await show_status_for_period (tg_id=message.from_user.id, date_from=date_obj, date_to=date_2_obj), parse_mode="HTML")
    await message.answer("главное меню:", reply_markup=kb.main)

@router.message(F.text == "назад в главное меню")
async def to_main(message: Message):
    await message.answer("процесс отменен", reply_markup=kb.main)