# bot_app/handlers/neural_faq_handler.py

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot_app.config import FAQ_TEMPLATES
from bot_app.db.admin.base import FAQDatabase
from bot_app.db.translation_db import TranslationDB
from bot_app.markups.user import get_numbered_questions_keyboard
from bot_app.utils.neural_search import NeuralSearch

# Создаем отдельный роутер для нейросетевого поиска
neural_router = Router()


@neural_router.message()
async def neural_answer_question(message: types.Message):
    """Обрабатывает вопросы пользователя с помощью нейросетевого поиска"""
    # Получаем язык пользователя
    user_lang = await TranslationDB.get_user_language_code(message.from_user.id)

    # Получаем текст запроса пользователя
    user_question = message.text.strip().lower()

    # Используем нейросетевой поиск для нахождения похожих вопросов
    matches_raw = await NeuralSearch.find_similar_questions(
        query=user_question,
        lang=user_lang,
        limit=6,
        threshold=0.6  # Пороговое значение сходства
    )

    if matches_raw:
        templates = FAQ_TEMPLATES[user_lang]
        message_text = templates['choose_question'] + "\n\n"

        matches = []
        for i, (matched_question, faq_id, score) in enumerate(matches_raw, 1):
            number_emoji = f"{i}️⃣"
            matches.append((matched_question, faq_id))
            message_text += f"{number_emoji} {matched_question}\n"

        message_text += templates['click_button']

        # Отправляем сообщение с найденными вопросами и клавиатурой
        await message.answer(
            message_text,
            reply_markup=get_numbered_questions_keyboard(matches)
        )
        return

    # Если ничего не найдено, отправляем сообщение о непонимании
    await message.answer(await TranslationDB.get_translation(message.from_user.id, "question_not_understood"))


@neural_router.callback_query(lambda c: c.data.startswith("faq:"))
async def handle_faq_callback(callback: CallbackQuery, state: FSMContext):
    """Обрабатывает нажатие на кнопку с вопросом"""
    try:
        # Получаем ID из callback_data
        faq_id = int(callback.data.split(":")[1])

        # Получаем строку из БД
        faq = await FAQDatabase.get_question_by_id(faq_id)

        if not faq:
            await callback.message.edit_text("Извините, информация не найдена.")
            return

        # Получаем язык пользователя
        lang = await TranslationDB.get_user_language_code(callback.from_user.id)

        # Отправляем ответ на нужном языке
        if lang == "en":
            answer = faq["answer_en"]
        else:
            answer = faq["answer_ru"]

        await callback.message.edit_text(answer)

    except Exception as e:
        await callback.message.edit_text("Произошла ошибка при обработке запроса.")
        print(f"Callback error: {e}")


# Функция для инициализации нейросетевого поиска
async def initialize_neural_search():
    """Инициализирует нейросетевой поиск при запуске бота"""
    search = NeuralSearch()
    await search.load_model()

    # Предварительная загрузка эмбеддингов для обоих языков
    await search.precompute_embeddings('ru')
    await search.precompute_embeddings('en')

    print("Нейросетевой поиск успешно инициализирован!")