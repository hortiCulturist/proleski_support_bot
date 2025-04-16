from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


def main_menu_keyboard(lang: str):
    buttons = {
        "ru": [
            KeyboardButton(text="Описание тренажёров"),
            KeyboardButton(text="Описание дополнительных опций"),
            KeyboardButton(text="FAQ"),
            KeyboardButton(text="Другие вопросы"),
            KeyboardButton(text="Изменить язык")
        ],
        "en": [
            KeyboardButton(text="Simulators description"),
            KeyboardButton(text="Description of additional options"),
            KeyboardButton(text="FAQ"),
            KeyboardButton(text="Other questions"),
            KeyboardButton(text="Change language")
        ]
    }


    placeholders = {
        "ru": "Введите ваш вопрос...",
        "en": "Type your question..."
    }

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [buttons[lang][0], buttons[lang][1]],
            [buttons[lang][2], buttons[lang][3]],
            [buttons[lang][4]],
        ],
        resize_keyboard=True,
        input_field_placeholder=placeholders.get(lang)
    )

    return keyboard


def back_and_support(lang: str):
    buttons = {
        "ru": [
            KeyboardButton(text="☎️Связь с менеджером"),
            KeyboardButton(text="📞Оставить номер телефона"),
            KeyboardButton(text="Главное меню")
        ],
        "en": [
            KeyboardButton(text="☎️Contact the manager"),
            KeyboardButton(text="📞Leave phone number"),
            KeyboardButton(text="Main menu")
        ]
    }

    placeholders = {
        "ru": "Введите ваш вопрос...",
        "en": "Type your question..."
    }

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [buttons[lang][0]],
            [buttons[lang][1]],
            [buttons[lang][2]],
        ],
        resize_keyboard=True,
        input_field_placeholder=placeholders.get(lang)
    )

    return keyboard


def phone_request_keyboard(lang: str):
    buttons = {
        "ru": [
            KeyboardButton(text="Отправить номер", request_contact=True),
            KeyboardButton(text="Главное меню")
        ],
        "en": [
            KeyboardButton(text="Send number", request_contact=True),
            KeyboardButton(text="Main menu")
        ]
    }

    placeholders = {
        "ru": "Нажмите кнопку для отправки номера...",
        "en": "Click the button to send the number..."
    }

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [buttons[lang][0]],
            [buttons[lang][1]]
        ],
        resize_keyboard=True,
        input_field_placeholder=placeholders.get(lang)
    )

    return keyboard


def go_to_main_manu(lang: str):
    buttons = {
        "ru": [
            KeyboardButton(text="Главное меню")
        ],
        "en": [
            KeyboardButton(text="Main menu")
        ]
    }

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[buttons[lang][0]]],
        resize_keyboard=True
    )

    return keyboard


def language_choice(lang: str):
    buttons = {
        "ru": [
            KeyboardButton(text="🇬🇧 Английский"),
            KeyboardButton(text="Русский")
        ],
        "en": [
            KeyboardButton(text="🇬🇧 English"),
            KeyboardButton(text="Russian")
        ]
    }

    placeholders = {
        "ru": "Выберите язык ниже...",
        "en": "Choose your language below..."
    }

    keyboard = ReplyKeyboardMarkup(
        keyboard=[[buttons[lang][0], buttons[lang][1]]],
        resize_keyboard=True,
        input_field_placeholder=placeholders.get(lang)
    )

    return keyboard


def get_numbered_questions_keyboard(matches: list[tuple[str, int]]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=str(i), callback_data=f"faq:{faq_id}")
         for i, (_, faq_id) in enumerate(matches, 1)]
    ])
    return keyboard