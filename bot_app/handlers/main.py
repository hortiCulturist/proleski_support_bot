from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot_app import config
from bot_app.config import ADMIN_ID
from bot_app.db.translation_db import TranslationDB
from bot_app.db.user.base import UserDatabase
from bot_app.markups.admin import admin_main_menu
from bot_app.markups.user import go_to_main_manu, main_menu_keyboard, phone_request_keyboard, language_choice
from bot_app.misc import router, bot
from bot_app.states.user import UserInfo, UserPhone


@router.message(Command("start"))
async def start_handler(message: types.Message):
    await TranslationDB.get_user_language_code(message.from_user.id)
    if message.from_user.id == config.ADMIN_ID:
        await message.answer("Привет! Я готов к работе босс.", reply_markup=admin_main_menu())
        return
    if await UserDatabase.add_user(message.from_user.id, message.from_user.full_name, message.from_user.username):
        await message.answer(await TranslationDB.get_translation(message.from_user.id, "start"),
                             reply_markup=language_choice(await TranslationDB.get_user_language_code(message.from_user.id)))
    else:
        await message.answer(await TranslationDB.get_translation(message.from_user.id, "start"),
                             reply_markup=main_menu_keyboard(await TranslationDB.get_user_language_code(message.from_user.id)))



@router.message(lambda message: message.text in ["Изменить язык", "Change language"])
async def edit_language(message: types.Message, state: FSMContext):
    await message.answer(await TranslationDB.get_translation(message.from_user.id, "select_language"),
                         reply_markup=language_choice(await TranslationDB.get_user_language_code(message.from_user.id)))



@router.message(lambda message: message.text in ["🇬🇧 Английский", "Русский", "🇬🇧 English", "Russian"])
async def set_language(message: types.Message):
    if message.text in ["🇬🇧 English", "🇬🇧 Английский"]:
        user_languages = "en"
    else:
        user_languages = "ru"
    await UserDatabase.edit_language(message.from_user.id, user_languages)
    await message.answer(await TranslationDB.get_translation(message.from_user.id, "language_changed"),
                         reply_markup=main_menu_keyboard(await TranslationDB.get_user_language_code(message.from_user.id)))


@router.message(lambda message: message.text in ["Главное меню", "Main menu"])
async def main_menu(message: types.Message, state: FSMContext):
    await state.clear()
    if message.from_user.id == config.ADMIN_ID:
        await message.answer("Привет! Я готов к работе босс.", reply_markup=admin_main_menu())
        return
    await message.answer(await TranslationDB.get_translation(message.from_user.id, "start"),
                         reply_markup=main_menu_keyboard(await TranslationDB.get_user_language_code(message.from_user.id)))


@router.message(lambda message: message.text in ["☎️Связь с менеджером", "☎️Contact the manager"])
async def select_channel(message: types.Message, state: FSMContext):
    await message.answer(await TranslationDB.get_translation(message.from_user.id, "ask_question"),
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(UserInfo.user_issue)


@router.message(UserInfo.user_issue)
async def select_channel(message: types.Message, state: FSMContext):
    await bot.send_message(chat_id=ADMIN_ID, text=message.text)
    await state.clear()
    await message.answer(await TranslationDB.get_translation(message.from_user.id, "thanks_for_question"),
                         reply_markup=go_to_main_manu(await TranslationDB.get_user_language_code(message.from_user.id)))


@router.message(lambda message: message.text in ["📞Оставить номер телефона", "📞Leave phone number"])
async def select_channel(message: types.Message, state: FSMContext):
    await message.answer(await TranslationDB.get_translation(message.from_user.id, "leave_phone"),
                         reply_markup=phone_request_keyboard(await TranslationDB.get_user_language_code(message.from_user.id)))
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
    await message.answer(await TranslationDB.get_translation(message.from_user.id, "contact_saved"),
                         reply_markup=go_to_main_manu(await TranslationDB.get_user_language_code(message.from_user.id)))


@router.message(UserPhone.user_phone)
async def select_channel(message: types.Message):
    await message.answer(await TranslationDB.get_translation(message.from_user.id, "phone_required"),
                         reply_markup=phone_request_keyboard(await TranslationDB.get_user_language_code(message.from_user.id)))

