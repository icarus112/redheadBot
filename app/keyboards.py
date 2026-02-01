from gc import callbacks

from aiogram import Router, F
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

# основное меню
main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Показать статус")],
                                     [KeyboardButton(text="Добавить запись")],
                                     [KeyboardButton(text="Удалить"),
                                      KeyboardButton(text="Редактировать")]],
                           resize_keyboard=True,
                           input_field_placeholder="Выберите пункт меню...")

for_delete = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="удалить запись", callback_data="del_record")],
        [InlineKeyboardButton(text="удалить период", callback_data="del_period")],
        [InlineKeyboardButton(text="назад в меню", callback_data="to_menu")]
    ]
)

'''для выбора отображения статуса'''
status = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="по 15 дням")],
                                       [KeyboardButton(text="от _ до _")],
                                       [KeyboardButton(text="за все время")]],
                             resize_keyboard=True,
                             input_field_placeholder="Выберите операцию..."
                             )

'''если на данный момент без ставки'''
for_rate = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="без ставки или ввести позже", callback_data="none_rate")]
    ]
)

'''статистика с чаевыми или без?'''
for_tips = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✅ с чаевыми", callback_data="with_tips")],
        [InlineKeyboardButton(text="❌ без чаевых", callback_data="without_tips")]
    ]
)