from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State

from database.funcs import parse_text_to_decimal
from database.service.users import (get_or_create_user, set_rate, set_tips)
import app.keyboards as kb

router = Router()

class Logging(StatesGroup):
    in_rate = State()

@router.message(CommandStart())
async def Hello(message: Message, state: FSMContext):

    try:
        greeting, flag =await  get_or_create_user(message.from_user.username, message.from_user.id)
    except Exception as ex:
        await message.answer(f"ошибка:{e}")
        return
    if flag:
        await message.answer(greeting)
        await message.answer("введите вашу ставку:")
        await state.set_state(Logging.in_rate)
    else:
        await message.answer(greeting, reply_markup=kb.main)

@router.message(Logging.in_rate)
async def logging(message: Message, state: FSMContext):

    try:
        rate = parse_text_to_decimal(message.text)
        await set_rate(message.from_user.id, rate)
    except Exception as e:
        await message.answer(f"ошибка:{e}")
        return

    await message.answer("будети ли вы вводить чаевые для статистики?", reply_markup=kb.for_tips)
    await state.clear()

@router.message(F.text == "/help")
async def help_me(message: Message):
    text = ("Этот бот создан для введение записей рабочих часов с его помощью можно добавлять, удалять, изменять записи\n"
            "учитывать чаевые (или нет), удобный отчет по 15 дням месяца, в котором данные для введения статистики,\nтакже все"
            " данные можно получить в виду excel(почему бы и нет)")

    await message.answer(text)

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