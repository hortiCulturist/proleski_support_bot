from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



def main_menu_keyboard():
    button_1 = KeyboardButton(text="Описание тренажёров")
    button_2 = KeyboardButton(text="Описание дополнительных опций")
    button_3 = KeyboardButton(text="FAQ")
    button_4 = KeyboardButton(text="Другие вопросы")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_1, button_2],
            [button_3, button_4],
        ],
        resize_keyboard=True,
        input_field_placeholder="Введите ваш вопрос..."
    )

    return keyboard


def back_and_support():
    button_1 = KeyboardButton(text="☎️Связь с менеджером")
    button_2 = KeyboardButton(text="📞Оставить номер телефона")
    button_3 = KeyboardButton(text="Главное меню")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_1],
            [button_2],
            [button_3],
        ],
        resize_keyboard=True,
        input_field_placeholder="Введите ваш вопрос..."
    )

    return keyboard

def phone_request_keyboard():
    button_phone = KeyboardButton(text="Отправить номер", request_contact=True)
    button_main = KeyboardButton(text="Главное меню")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_phone],
            [button_main]
        ],
        resize_keyboard=True,
        input_field_placeholder="Нажмите кнопку для отправки номера"
    )

    return keyboard


def go_to_main_manu():
    button_1 = KeyboardButton(text="Главное меню")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_1],
        ],
        resize_keyboard=True
    )

    return keyboard