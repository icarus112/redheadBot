from readline import insert_text
from sqlalchemy import delete
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from decimal import Decimal

from database.funcs import pars_date, parse_hours
from database.models import async_session, User, WorkTime
from database.reports import (get_or_create_user, get_user_with_times, insert_time1,
                              delete_date)
import app.keyboards as kb

router = Router()

class AddWorkTime(StatesGroup):
    date = State()
    hour = State()

class DeleteFlow(StatesGroup):
    waiting_date = State()
    waiting_period = State()

@router.message(CommandStart())
async def Hello(message: Message):
    greeting =await  get_or_create_user(message.from_user.username, message.from_user.id)
    await message.answer(greeting, reply_markup=kb.main)

@router.message(F.text == "Показать статус")
async def status(message: Message):
    user = await get_user_with_times(message.from_user.id)

    if not user:
        print("Пользователь не найден")
        return

    await message.answer(user.get_status())

@router.message(F.text == "Добавить запись")
async def add_record(message: Message, state: FSMContext):
    await message.answer("введи дату")
    await state.set_state(AddWorkTime.date)

@router.message(AddWorkTime.date)
async def on_date(message: Message, state: FSMContext):
    try:
        date_obj = pars_date(message.text)
    except Exception:
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return

    await state.update_data(date=date_obj)
    await message.answer(f"успешно сохранено как {date_obj}")
    await state.set_state(AddWorkTime.hour)
    await message.answer("теперь введи кол-во часов")

@router.message(AddWorkTime.hour)
async def on_hour(message: Message, state: FSMContext):

    hour = message.text

    data = await state.get_data()#сохряняем все данные FSM в виде словаря
    date_obj = data.get("date")#находим date
    if date_obj is None:
        await message.answer("что то пошло не так, начни заново черт гребанный")
        await state.clear()
        return

    tg_id = message.from_user.id

    try:
        await insert_time1(tg_id=tg_id, date=date_obj, hour=hour)
    except Exception as e:
        await message.answer(f"ошибка:{e}")
        return

    await message.answer("✅ Запись добавлена!", reply_markup=kb.main)
    await state.clear()

@router.message(F.text == "Удалить")
async def choose_del_method(message: Message):
    await message.answer("Выберите способ", reply_markup=kb.for_delete)


@router.callback_query(F.data == "del_record")
async def press_del_record(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.edit_text("Введи дату которую хочешь удалить")
    await state.set_state(DeleteFlow.waiting_date)

@router.callback_query(F.data == "del_period")
async def press_del_period(call: CallbackQuery):
    await call.answer()
    await call.message.edit_text("Удалить период")

@router.callback_query(F.data == "to_menu")
async def back_to_menu(call: CallbackQuery):
    await call.answer("процесс отменен", reply_markup=kb.main)

@router.message(DeleteFlow.waiting_date)
async def del_record(message: Message, state: FSMContext):
    try:
        wd = pars_date(message.text)
        result = await delete_date(message.text, message.from_user.id)

        if result.rowcount == 0:
            await message.answer(f"по запросу {wd}, ничего не найдено", reply_markup=kb.for_delete)
        else:
            await message.answer(f"дата {wd} успешно удалено", reply_markup=kb.for_delete)

        await state.clear()
    except Exception as e:
        # await message.answer(e)
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return