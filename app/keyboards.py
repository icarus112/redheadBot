from gc import callbacks

from aiogram import Router, F
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="Показать статус")],
                                     [KeyboardButton(text="Добавить запись")],
                                     [KeyboardButton(text="Удалить"),
                                      KeyboardButton(text="Редактировать")]],
                           resize_keyboard=True,
                           input_field_placeholder="Выберите пунскт меню...")

for_delete = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="удалить запись", callback_data="del_record")],
        [InlineKeyboardButton(text="удалить период", callback_data="del_period")],
        [InlineKeyboardButton(text="назад в меню", callback_data="to_menu")]
    ]
)