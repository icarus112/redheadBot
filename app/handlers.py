import asyncio
from readline import insert_text
from sqlalchemy import delete
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
import datetime
from decimal import Decimal

from sqlalchemy.orm import defer

from database.funcs import (parse_date, parse_hours, dates_for_status)
from database.repo.work_time import ( insert_time1, delete_date, get_time_period)
from database.repo.users import (get_or_create_user, get_user_with_times, set_rate, set_tips, delete_user)
from database.reports import show_status
import app.keyboards as kb

router = Router()

class Logging(StatesGroup):
    in_rate = State()

class AddWorkTime(StatesGroup):
    date = State()
    hour = State()
    tips = State()

class DeleteFlow(StatesGroup):
    waiting_date = State()
    waiting_period = State()

# для дебага


@router.message(CommandStart())
async def Hello(message: Message, state: FSMContext):
    greeting, flag =await  get_or_create_user(message.from_user.username, message.from_user.id)
    if flag:
        await message.answer(greeting)
        await message.answer("введите вашу ставку:")
        await state.set_state(Logging.in_rate)
    else:
        await message.answer(greeting, reply_markup=kb.main)

@router.message(Logging.in_rate)
async def logging(message: Message, state: FSMContext):

    try:
        rate = parse_hours(message.text)
        await set_rate(message.from_user.id, rate)
    except Exception as e:
        await message.answer(f"ошибка:{e}")
        return

    await message.answer("будети ли вы вводить чаевые для статистики?", reply_markup=kb.for_tips)
    await state.clear()

@router.callback_query(F.data == "with_tips")
async def with_tips(call: CallbackQuery):
    await set_tips(
        tg_id=call.from_user.id, value=True
    )
    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer("✅ Чаевые включены", reply_markup=kb.main)
    await call.answer()

@router.callback_query(F.data == "without_tips")
async def without_tips(call: CallbackQuery):
    await set_tips(
        tg_id=call.from_user.id, value=False
    )
    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer("❌ Чаевые выключены", reply_markup=kb.main)
    await call.answer()

@router.message(F.text == "Показать статус")
async def status(message: Message):
    user = await get_user_with_times(message.from_user.id)

    if not user:
        print("Пользователь не найден")
        return
    # 6480514308
    await message.answer( await show_status(message.from_user.id), parse_mode="HTML")


@router.message(F.text == "Добавить запись")
async def add_record(message: Message, state: FSMContext):
    await message.answer("введи дату")
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
            await insert_time1(tg_id=tg_id, date=date_obj, hour=hour)
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
        await insert_time1(tg_id=tg_id, date=date_obj, hour=hour, tips=tips)
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
        wd = parse_date(message.text)
        result = await delete_date(message.text, message.from_user.id)

        if result.rowcount == 0:
            await message.answer(f"по запросу {wd.strftime('%d.%m.%Y')}, ничего не найдено", reply_markup=kb.for_delete)
        else:
            await message.answer(f"дата {wd.strftime('%d.%m.%Y')} успешно удалено", reply_markup=kb.for_delete)

        await state.clear()
    except Exception as e:
        # await message.answer(e)
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return