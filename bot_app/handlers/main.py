from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot_app import config
from bot_app.config import ADMIN_ID
from bot_app.db.user.base import UserDatabase
from bot_app.markups.admin import admin_main_menu
from bot_app.markups.user import go_to_main_manu, main_menu_keyboard, phone_request_keyboard
from bot_app.misc import router, bot
from bot_app.states.user import UserInfo, UserPhone


@router.message(Command("start"))
async def start_handler(message: types.Message):
    text = ("Здравствуйте! Я – виртуальный помощник PROLESKI. Чем могу помочь? "
            "Вот основные направления, по которым я могу вас проконсультировать.")
    if message.from_user.id == config.ADMIN_ID:
        await message.answer("Привет! Я готов к работе босс.", reply_markup=admin_main_menu())
        return
    await UserDatabase.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username)
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(F.text == "Главное меню")
async def main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id == config.ADMIN_ID:
        await message.answer("Привет! Я готов к работе босс.", reply_markup=admin_main_menu())
        return
    text = ("Здравствуйте! Я – виртуальный помощник PROLESKI. Чем могу помочь? "
            "Вот основные направления, по которым я могу вас проконсультировать.")
    await message.answer(text, reply_markup=main_menu_keyboard())


@router.message(F.text == "☎️Связь с менеджером")
async def select_channel(message: types.Message, state: FSMContext):
    await message.answer("Напишите нам свой вопрос:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserInfo.user_issue)


@router.message(UserInfo.user_issue)
async def select_channel(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=ADMIN_ID, text=message.text)
    await state.clear()
    await message.answer("Благодарим за вопрос! В ближайшее время менеджер вам ответит",
                         reply_markup=go_to_main_manu())


@router.message(F.text == "📞Оставить номер телефона")
async def select_channel(message: types.Message, state: FSMContext):
    await message.answer("Нажмите на кнопку ниже, чтобы оставить свой номер телефона для обратной связи.",
                         reply_markup=phone_request_keyboard())
    await state.set_state(UserPhone.user_phone)


@router.message(UserPhone.user_phone, F.contact)
async def select_channel(message: types.Message, state: FSMContext):
    user = message.from_user
    phone_number = message.contact.phone_number if message.contact else "Не указан"
    print(type(phone_number))
    print(phone_number)
    username = f"@{user.username}" if user.username else "Не указан"
    full_name = f"{user.first_name} {user.last_name}" if user.first_name else "Не указано"
    await state.clear()
    await UserDatabase.save_user_phone(phone_number, message.from_user.id)

    text = f"""
    📝 Отчет о пользователе:
    - 🆔 ID пользователя: {user.id}
    - 👤 Имя: {full_name}
    - 📲 Юзернейм: {username}
    - 📞 Номер телефона: {phone_number}
    """
    await bot.send_message(chat_id=ADMIN_ID, text=text)
    await message.answer("✅Ваш контакт сохранен, мы свяжемся с вами в ближайшее время!",
                         reply_markup=go_to_main_manu())


@router.message(UserPhone.user_phone)
async def select_channel(message: types.Message):
    await message.answer("❌Пожалуйста, нажмите кнопку, чтобы отправить номер телефона, ввод не требуется.",
                         reply_markup=phone_request_keyboard())

