
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

# основное меню
main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="👤Показать статус")],
                                     [KeyboardButton(text="✏️Добавить запись")],
                                     [KeyboardButton(text="❗Удалить"),
                                      KeyboardButton(text="🎛️Другое")]],
                           resize_keyboard=True,
                           input_field_placeholder="Выберите пункт меню...")

for_delete = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="удалить запись", callback_data="del_record")],
        [InlineKeyboardButton(text="назад в меню", callback_data="to_menu")]
    ]
)

'''для выбора отображения статуса'''
status = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="по 15 дням")],
                                       [KeyboardButton(text="от _ до _")],
                                       [KeyboardButton(text="назад в главное меню")]],
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

'''другое'''
other = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='📝Изменить запись')],
                                      [KeyboardButton(text='🪙Вкл/выкл чаевые'),
                                       KeyboardButton(text="🧮Изменить ставку")],
                                      [KeyboardButton(text='📄Отчёт в excel'),
                                       KeyboardButton(text="назад в главное меню")]])

'''изменить запись'''
update_rec = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='🗓️Дату', callback_data="upd_date")],
        [InlineKeyboardButton(text='🪙Чаевые', callback_data="upd_tips")],
        [InlineKeyboardButton(text='⌛Часы работы', callback_data="upd_hours")],
        [InlineKeyboardButton(text='назад в главное меню', callback_data="to_menu")]])