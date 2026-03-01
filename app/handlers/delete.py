from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State

from database.funcs import (parse_date, parse_hours, dates_for_status, parse_rate)
from database.service.work_time import (insert_time1, delete_date, get_time_period)
from database.service.users import (get_or_create_user, get_user_with_times, set_rate, set_tips, delete_user)
from database.reports import show_status
import app.keyboards as kb

router = Router()

class DeleteFlow(StatesGroup):
    waiting_date = State()
    waiting_period = State()

@router.message(F.text == "❗Удалить")
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
            await message.answer(f"дата {wd.strftime('%d.%m.%Y')} успешно удалена", reply_markup=kb.for_delete)

        await state.clear()
    except Exception as e:
        # await message.answer(e)
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return