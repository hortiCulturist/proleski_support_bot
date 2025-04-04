from aiogram import types, F
from rapidfuzz import process

from bot_app.db.admin.base import FAQDatabase
from bot_app.db.translation_db import TranslationDB
from bot_app.markups.user import back_and_support, go_to_main_manu
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

    faq_dict = {
        row['question_ru'].lower(): row for row in rows
    }
    faq_dict.update({
        row['question_en'].lower(): row for row in rows
    })

    result = process.extractOne(user_question, faq_dict.keys(), score_cutoff=70)

    if result:
        best_match = faq_dict[result[0]]
        if result[0] in faq_dict and best_match['question_ru'].lower() == result[0]:
            await message.answer(best_match['answer_ru'])
        elif result[0] in faq_dict and best_match['question_en'].lower() == result[0]:
            await message.answer(best_match['answer_en'])
    else:
        await message.answer(await TranslationDB.get_translation(message.from_user.id,
                                                                 "question_not_understood"))


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


