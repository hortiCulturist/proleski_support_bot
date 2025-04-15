from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from rapidfuzz import process

from bot_app.db.admin.base import FAQDatabase
from bot_app.db.translation_db import TranslationDB
from bot_app.markups.user import back_and_support, go_to_main_manu, get_similar_questions_keyboard
from bot_app.misc import router



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
async def answer_question(message: types.Message):
    user_question = message.text.strip().lower()
    rows = await FAQDatabase.get_all_questions()

    question_answer_pairs = []

    for row in rows:
        question_ru = row['question_ru'].strip().lower() if row['question_ru'] else ''
        question_en = row['question_en'].strip().lower() if row['question_en'] else ''
        answer_ru = row['answer_ru']
        answer_en = row['answer_en']
        faq_id = row['faq_id']  # убедись, что это поле возвращается из базы

        if question_ru:
            question_answer_pairs.append((question_ru, answer_ru, faq_id))
        if question_en:
            question_answer_pairs.append((question_en, answer_en, faq_id))

    all_questions = [q for q, _, _ in question_answer_pairs]

    matches_raw = process.extract(user_question, all_questions, limit=3, score_cutoff=70)

    # Получаем список подходящих (вопрос, ответ, faq_id)
    matches = []
    for matched_question, score, _ in matches_raw:
        for q_text, answer, faq_id in question_answer_pairs:
            if q_text == matched_question:
                matches.append((matched_question, faq_id))
                break

    if matches:
        await message.answer(await TranslationDB.get_translation(message.from_user.id, "сhoose_question"),
            reply_markup=get_similar_questions_keyboard(matches))
        return

    await message.answer(await TranslationDB.get_translation(message.from_user.id, "question_not_understood"))


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


    # # Используем fuzzy-поиск с порогом 70
    # match = process.extractOne(user_question, all_questions, score_cutoff=70)


    # if match:
    #     matched_question = match[0]
    #     # Находим соответствующий ответ
    #     for question, answer in question_answer_pairs:
    #         if question == matched_question:
    #             await message.answer(answer)
    #             return
    #
    # # Если ничего не нашли
    # await message.answer(await TranslationDB.get_translation(message.from_user.id, "question_not_understood"))

# @router.message(F.text)
# async def answer_question(message: types.Message):
#     user_question = message.text.strip().lower()
#
#     rows = await FAQDatabase.get_all_questions()
#
#     faq_dict = {
#         row['question_ru'].lower(): row for row in rows
#     }
#     faq_dict.update({
#         row['question_en'].lower(): row for row in rows
#     })
#
#     result = process.extractOne(user_question, faq_dict.keys(), score_cutoff=70)
#
#     if result:
#         best_match = faq_dict[result[0]]
#         if result[0] in faq_dict and best_match['question_ru'].lower() == result[0]:
#             await message.answer(best_match['answer_ru'])
#         elif result[0] in faq_dict and best_match['question_en'].lower() == result[0]:
#             await message.answer(best_match['answer_en'])
#     else:
#         await message.answer(await TranslationDB.get_translation(message.from_user.id,
#                                                                  "question_not_understood"))


@router.message(~F.text)
async def answer_question_error(message: types.Message):
    pass
# @router.message()
# async def answer_question(message: types.Message):
#     user_question = message.text.strip().lower()
#
#     result = process.extractOne(user_question, FAQ.keys(), score_cutoff=70)
#
#     if result:
#         best_match, score, _ = result
#         await message.answer(FAQ[best_match])
#     else:
#         await message.answer("Извините, я не понял ваш вопрос. Попробуйте сформулировать иначе.")


