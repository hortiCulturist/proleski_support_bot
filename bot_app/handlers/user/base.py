import asyncio

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from bot_app.config import FAQ_TEMPLATES
from bot_app.db.admin.base import FAQDatabase
from bot_app.db.translation_db import TranslationDB
from bot_app.markups.user import back_and_support, go_to_main_manu, get_numbered_questions_keyboard
from bot_app.misc import router
from bot_app.utils.neural_search import NeuralSearch
from bot_app.utils.rate_limiter import check_rate_limit


@router.message(lambda message: message.text in ["Описание тренажёров", "Simulators description"])
async def button_simulator_description(message: types.Message):
    await message.answer(await TranslationDB.get_admin_translation(message.from_user.id, "simulator_description"),
                         reply_markup=back_and_support(await TranslationDB.get_user_language_code(message.from_user.id)))


@router.message(lambda message: message.text in ["Описание дополнительных опций", "Description of additional options"])
async def button_option_description(message: types.Message):
    await message.answer(await TranslationDB.get_admin_translation(message.from_user.id, "option_description"),
                         reply_markup=back_and_support(await TranslationDB.get_user_language_code(message.from_user.id)))


@router.message(F.text == "FAQ")
async def button_faq(message: types.Message):
    await message.answer(await TranslationDB.get_admin_translation(message.from_user.id, "FAQ"),
                         reply_markup=go_to_main_manu(await TranslationDB.get_user_language_code(message.from_user.id)))


@router.message(lambda message: message.text in ["Другие вопросы", "Other questions"])
async def button_faq(message: types.Message):
    await message.answer(await TranslationDB.get_admin_translation(message.from_user.id, "other_issues"),
                         reply_markup=go_to_main_manu(await TranslationDB.get_user_language_code(message.from_user.id)))


@router.message(F.text)
async def neural_answer_question(message: types.Message):
    """Обрабатывает вопросы пользователя с помощью нейросетевого поиска"""
    # Получаем язык пользователя
    user_lang = await TranslationDB.get_user_language_code(message.from_user.id)

    # Проверяем, не превышен ли лимит запросов
    is_allowed, wait_seconds = await check_rate_limit(message.from_user.id)
    if not is_allowed:
        # Формируем сообщение об ограничении в зависимости от языка
        if user_lang == "en":
            limit_message = f"⚠️ **Rate limit exceeded**. Please wait {wait_seconds} seconds before sending your next question."
        else:
            limit_message = f"⚠️ **Превышен лимит запросов**. Пожалуйста, подождите {wait_seconds} секунд перед отправкой следующего вопроса."

        await message.answer(limit_message, parse_mode="Markdown")
        return

    # Получаем текст запроса пользователя
    user_question = message.text.strip().lower()

    # Добавляем индикатор, что используется нейросетевой поиск
    await message.answer("🧠 *Используется нейросетевой поиск*...", parse_mode="Markdown")
    await asyncio.sleep(2)

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
            # Добавляем значение сходства для более понятного дебага
            message_text += f"{number_emoji} {matched_question} (сходство: {score:.2f})\n"

        message_text += templates['click_button']

        # Отправляем сообщение с найденными вопросами и клавиатурой
        await message.answer(
            message_text,
            reply_markup=get_numbered_questions_keyboard(matches)
        )
        return

    # Если ничего не найдено, отправляем сообщение о непонимании
    await message.answer(await TranslationDB.get_translation(message.from_user.id, "question_not_understood"))


# @router.message(F.text)
# async def answer_question(message: types.Message):
#     # Очищаем запрос пользователя от знаков препинания
#     user_question = PUNCTUATION_PATTERN.sub(' ', message.text.strip().lower())
#     user_lang = await TranslationDB.get_user_language_code(message.from_user.id)
#
#     # Получаем вопросы на языке пользователя
#     rows = await FAQDatabase.get_faq_data_by_language(user_lang)
#     if not rows:
#         await message.answer(await TranslationDB.get_translation(message.from_user.id, "question_not_understood"))
#         return
#
#     # Расширяем запрос пользователя с лемматизацией
#     expanded_query_words = expand_query(user_question)
#
#     # Создаем список вопросов для поиска с их ID
#     questions_with_ids = []
#     for row in rows:
#         # Нормализуем каждый вопрос так же, как и запрос пользователя
#         question_text = row['question'].strip().lower()
#         # Очищаем вопрос от знаков препинания для сравнения
#         clean_question = PUNCTUATION_PATTERN.sub(' ', question_text)
#         question_words = set(clean_question.split())
#         normalized_words = {normalize_word(word) for word in question_words if word}
#
#         questions_with_ids.append((question_text, normalized_words, row['faq_id']))
#
#     # Фильтруем вопросы, которые содержат хотя бы одно слово из расширенного запроса
#     filtered_questions = []
#     for q_text, q_norm_words, faq_id in questions_with_ids:
#         # Проверяем пересечение множеств слов
#         if expanded_query_words.intersection(q_norm_words):
#             filtered_questions.append((q_text, faq_id))
#
#     # Если есть отфильтрованные вопросы, используем нечеткий поиск для них
#     if filtered_questions:
#         questions = [q for q, _ in filtered_questions]
#
#         from rapidfuzz import process
#         # Понижаем порог оценки до 60, чтобы захватить больше потенциальных совпадений
#         matches_raw = process.extract(user_question, questions, limit=6, score_cutoff=60)
#
#         if matches_raw:
#             templates = FAQ_TEMPLATES[user_lang]
#             message_text = templates['choose_question'] + "\n\n"
#
#             matches = []
#             for i, (matched_question, score, _) in enumerate(matches_raw, 1):
#                 number_emoji = f"{i}️⃣"
#
#                 # Находим faq_id для совпавшего вопроса
#                 for q, faq_id in filtered_questions:
#                     if q == matched_question:
#                         matches.append((matched_question, faq_id))
#                         message_text += f"{number_emoji} {matched_question}\n"
#                         break
#
#             message_text += templates['click_button']
#
#             await message.answer(
#                 message_text,
#                 reply_markup=get_numbered_questions_keyboard(matches)
#             )
#             return
#
#     await message.answer(await TranslationDB.get_translation(message.from_user.id, "question_not_understood"))


@router.callback_query(F.data.startswith("faq:"))
async def handle_faq_callback(callback: CallbackQuery, state: FSMContext):
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


@router.message(~F.text)
async def answer_question_error(message: types.Message):
    pass

