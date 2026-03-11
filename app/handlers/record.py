from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State

from database.funcs import parse_date
from database.service.work_time import insert_time
from database.service.users import get_user_with_times
import app.keyboards as kb

router = Router()

class AddWorkTime(StatesGroup):
    date = State()
    hour = State()
    tips = State()

@router.message(F.text == "✏️Добавить запись")
async def add_new_record(message: Message, state: FSMContext):
    await message.answer("Введи дату")
    await state.set_state(AddWorkTime.date)

@router.message(AddWorkTime.date)
async def on_date(message: Message, state: FSMContext):
    try:
        date_obj = parse_date(message.text)
    except Exception:
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return

    await state.update_data(date=date_obj)
    await message.answer(f"успешно сохранено как {date_obj.strftime('%d.%m.%Y')}")
    await state.set_state(AddWorkTime.hour)
    await message.answer("теперь введи кол-во часов")

@router.message(AddWorkTime.hour)
async def on_hour(message: Message, state: FSMContext):

    hour = message.text
    tg_id = message.from_user.id
    user = await get_user_with_times(message.from_user.id)

    data = await state.get_data()#сохряняем все данные FSM в виде словаря
    date_obj = data.get("date")#находим date
    await state.update_data(hour=hour)
    if date_obj is None:
        await message.answer("что то пошло не так, начни заново")
        await state.clear()
        return

    if user.user_tips:
        await message.answer("теперь введи сумму чаевых за этот день:")
        await state.set_state(AddWorkTime.tips)
    else:
        try:
            await insert_time(tg_id=tg_id, date=date_obj, hour=hour)
        except Exception as e:
            await message.answer(f"ошибка:{e}")
            return
        await message.answer("✅ Запись добавлена!", reply_markup=kb.main)
        await state.clear()

@router.message(AddWorkTime.tips)
async def on_tips(message: Message,state: FSMContext):
    data = await state.get_data()
    date_obj = data.get("date")
    hour = data.get("hour")
    tg_id = message.from_user.id
    tips = message.text
    try:
        await insert_time(tg_id=tg_id, date=date_obj, hour=hour, tips=tips)
    except Exception as e:
        await message.answer(f"ошибка:{e}")
        return
    await message.answer("✅ Запись добавлена!", reply_markup=kb.main)
    await state.clear()