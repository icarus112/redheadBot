from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import BufferedInputFile

from sqlalchemy import create_engine

from database.funcs import parse_date
from database.service.work_time import (update_work_hours, update_work_tips, update_work_date)
from database.service.users import get_user_with_times, update_rate
from conf import DATABASE_URL_SYNC
import app.keyboards as kb

from io import BytesIO
import pandas as pd
import datetime as dt
router = Router()

class ChangeRate(StatesGroup):
    update_rate = State()

class ChangeHour(StatesGroup):
    select_date = State()
    update_hour = State()

class ChangeTips(StatesGroup):
    select_date = State()
    update_tips = State()

class ChangeDate(StatesGroup):
    select_date = State()
    update_date = State()

@router.message(F.text == "🎛️Другое")
async def other(message: Message):
    await message.answer("выберите функцию:", reply_markup=kb.other)

@router.message(F.text == "🪙Вкл/выкл чаевые")
async def tips(message: Message):
    await message.answer("выберите:", reply_markup=kb.for_tips)

@router.message(F.text =="назад в главное меню")
async def back_to_main(message: Message):
    await message.answer(f"\u2b05", reply_markup=kb.main)

@router.message(F.text == "📝Изменить запись")
async def change_record(message: Message, state: FSMContext):
    await message.answer("что вам нужно изменить:", reply_markup=kb.update_rec)


@router.callback_query(F.data == "to_menu")
async def back_to_menu(call: CallbackQuery):
    await call.answer("процесс отменен", reply_markup=kb.main)

'''изменить часы работы'''

@router.callback_query(F.data == "upd_hours")
async def change_hour_by_date(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Введите дату для изменения часов работы:")
    await state.set_state(ChangeHour.select_date)

@router.message(ChangeHour.select_date)
async def select_date(message: Message, state: FSMContext):
    try:
        date_obj = message.text
    except Exception:
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return

    await state.update_data(date=date_obj)
    await message.answer("теперь введи кол-во часов которое хочешь ввести в эту дату:")
    await state.set_state(ChangeHour.update_hour)

@router.message(ChangeHour.update_hour)
async def update_hour(message: Message, state: FSMContext):
    data = await state.get_data()  # сохряняем все данные FSM в виде словаря
    date_obj = data.get("date")  # находим date
    if date_obj is None:
        await message.answer("что то пошло не так, начни заново")
        await state.clear()
        return

    date_obj = parse_date(date_obj)

    try:
        hour = message.text
    except Exception:
        await message.answer("ты ввел не правильно введи как 12 или 12.5")
        return

    ok = await update_work_hours(tg_id=message.from_user.id, date=date_obj, hour=hour)
    if ok:
        await message.answer("Часы работы по дате успешно изменены")
        await message.answer(f"\u2b05", reply_markup=kb.main)
    else:
        await message.answer(f"Такой даты как {date_obj.strftime('%d.%m.%Y')} не существует")
        await message.answer(f"\u2b05", reply_markup=kb.main)

    await state.clear()

'''изменить чаевые работы'''

@router.callback_query(F.data == "upd_tips")
async def change_tips_by_date(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Введите дату для изменения чаевых:")
    await state.set_state(ChangeTips.select_date)

@router.message(ChangeTips.select_date)
async def select_date(message: Message, state: FSMContext):
    try:
        date_obj = message.text
    except Exception:
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return

    await state.update_data(date=date_obj)
    await message.answer("теперь введи чаевые которое хочешь ввести в эту дату:")
    await state.set_state(ChangeTips.update_tips)

@router.message(ChangeTips.update_tips)
async def update_tips(message: Message, state: FSMContext):
    data = await state.get_data()
    date_obj = data.get("date")
    if date_obj is None:
        await message.answer("что то пошло не так, начни заново")
        await state.clear()
        return

    date_obj = parse_date(date_obj)

    try:
        tips = message.text
    except Exception:
        await message.answer("ты ввел не правильно введи как 1200 или 1200.5")
        return

    ok = await update_work_tips(tg_id=message.from_user.id, date=date_obj, tips=tips)
    if ok:
        await message.answer("Чаевые по дате успешно изменены")
        await message.answer(f"\u2b05", reply_markup=kb.main)
    else:
        await message.answer(f"Такой даты как {date_obj.strftime('%d.%m.%Y')} не существует")
        await message.answer(f"\u2b05", reply_markup=kb.main)

    await state.clear()

'''изменить даты работы'''
@router.callback_query(F.data == "upd_date")
async def change_date_by_date(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await call.message.answer("Введите старую дату что-бы его изменить :")
    await state.set_state(ChangeDate.select_date)

@router.message(ChangeDate.select_date)
async def select_date(message: Message, state: FSMContext):
    try:
        date1_obj = message.text
    except Exception:
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return

    await state.update_data(date=date1_obj)
    await message.answer("Теперь введите новую дату что-бы ввести изменения:")
    await state.set_state(ChangeDate.update_date)

@router.message(ChangeDate.update_date)
async def update_date(message: Message, state: FSMContext):
    data = await state.get_data()
    date1_obj = data.get("date")
    if date1_obj is None:
        await message.answer("что то пошло не так, начни заново")
        await state.clear()
        return

    date1_obj = parse_date(date1_obj)

    try:
        date2_obj = message.text
    except Exception:
        await message.answer("ты ввел не правильно введи как 12 или 12.01 или 12.02.2026")
        return

    date2_obj = parse_date(date2_obj)
    ok = await update_work_date(tg_id=message.from_user.id, old_date=date1_obj, new_date=date2_obj)
    if ok:
        await message.answer("Дата успешно изменена")
        await message.answer(f"\u2b05", reply_markup=kb.main)
    else:
        await message.answer(f"Такой даты как {date1_obj.strftime('%d.%m.%Y')} не существует")
        await message.answer(f"\u2b05", reply_markup=kb.main)

    await state.clear()

@router.message(F.text == "🧮Изменить ставку")
async def change_rate(message: Message, state: FSMContext):
    user = await get_user_with_times(message.from_user.id)
    await message.answer(f"Ваша ставка сейчас: {user.rate}")
    await message.answer("Введите новую ставку:")
    await state.set_state(ChangeRate.update_rate)

@router.message(ChangeRate.update_rate)
async def update_user_rate(message: Message, state: FSMContext):
    try:
        new_rate = message.text
        ok = await update_rate(rate=new_rate, tg_id=message.from_user.id)
    except Exception as ex:
        await message.answer("ошибка: ",ex)
        return
    if ok:
        await message.answer("Ваша ставка успешна изменена")
    else:
        await message.answer("Что-то пошло не так попробуйте снова")

    await state.clear()

@router.message(F.text == "📄Отчёт в excel")
async def export_work_times(message: Message):
    try:
        engine = create_engine(DATABASE_URL_SYNC)
        data = pd.read_sql("select * from work_time", engine)

        #изменение колонок
        data["date"] = pd.to_datetime(data["date"]).dt.strftime("%d.%m.%Y")
        data["user_id"] = data["user_id"].astype(str)

        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            today = f"""отчёт_{dt.date.today().strftime("%d.%m.%Y")}.xlsx"""
            data.to_excel(writer, index=False, sheet_name="Отчёт")

            workbook = writer.book
            worksheet = writer.sheets["Отчёт"]

            # формат заголовков
            header_format = workbook.add_format({
                "bold": True,
                "border": 1
            })

            # применяем формат к заголовкам
            for col_num, col_name in enumerate(data.columns):
                worksheet.write(0, col_num, col_name, header_format)

            # автоширина колонок
            for i, col in enumerate(data.columns):
                max_length = max(
                    data[col].astype(str).map(len).max(),
                    len(col)
                )
                worksheet.set_column(i, i, max_length + 2)

            # 🔹 формат даты
            date_format = workbook.add_format({"num_format": "dd.mm.yyyy"})
            if "date" in data.columns:
                col_idx = data.columns.get_loc("date")
                worksheet.set_column(col_idx, col_idx, 15, date_format)

        buffer.seek(0)
        await message.answer_document(BufferedInputFile(buffer.read(), filename=today))
    except Exception as ex:
        print(ex)
        return