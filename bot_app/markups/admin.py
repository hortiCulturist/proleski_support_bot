from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



def admin_main_menu():
    button_1 = KeyboardButton(text="Добавить вопрос")
    button_2 = KeyboardButton(text="Удалить вопрос")
    button_3 = KeyboardButton(text="Изменить текст")
    # button_3 = KeyboardButton(text="Изменить FAQ")
    # button_4 = KeyboardButton(text="Изменить 'Другие вопросы'")
    button_5 = KeyboardButton(text="Загрузить вопросы/ответы Excel")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_1, button_2],
            [button_3],
            [button_5]
        ],
        resize_keyboard=True
    )

    return keyboard


def admin_no_translate():
    button_1 = KeyboardButton(text="Нет перевода")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_1],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите язык..."
    )

    return keyboard


def admin_back_menu():
    button_1 = KeyboardButton(text="Меню")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_1],
        ],
        resize_keyboard=True
    )

    return keyboard


def faq_id_keyboard(faq_ids):
    button_main = KeyboardButton(text="Меню")

    sorted_ids = sorted(faq_ids, key=int)

    rows = [sorted_ids[i:i+2] for i in range(0, len(sorted_ids), 2)]
    rows = [[KeyboardButton(text=str(faq_id)) for faq_id in row] for row in rows]

    rows.append([button_main])

    keyboard = ReplyKeyboardMarkup(
        keyboard=rows,
        resize_keyboard=True,
        input_field_placeholder="Выберите ID..."
    )
    return keyboard


def edit_text_button():
    button_1 = KeyboardButton(text="Описание тренажёров")
    button_2 = KeyboardButton(text="Описание дополнительных опций")
    button_3 = KeyboardButton(text="FAQ")
    button_4 = KeyboardButton(text="Другие вопросы")
    button_5 = KeyboardButton(text="Меню")

    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [button_1, button_2],
            [button_3, button_4],
            [button_5]
        ],
        resize_keyboard=True
    )

    return keyboard