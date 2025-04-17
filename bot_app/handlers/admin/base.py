import asyncio
import os

from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot_app.config import ADMIN_ID, FILES_PATH, sections_mapping
from bot_app.db.admin.base import FAQDatabase, ExcelOperation
from bot_app.db.translation_db import TranslationDB
from bot_app.markups.admin import admin_main_menu, faq_id_keyboard, admin_back_menu, edit_text_button
from bot_app.misc import router, bot
from bot_app.states.admin import AddFaq, DeleteFaq, AddXlsx, EditText


@router.message(F.text == "Добавить вопрос")
async def add_questions(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer('Введите вопрос/ы на русском языке:', reply_markup=admin_back_menu())
    await state.set_state(AddFaq.add_questions1)


@router.message(AddFaq.add_questions1)
async def add_questions(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(ru_questions=message.text)
    await message.answer('Добавлено!\nВведите вопрос/ы на английском языке:')
    await state.set_state(AddFaq.add_questions2)


@router.message(AddFaq.add_questions2)
async def add_questions(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(en_questions=message.text)
    await message.answer('Добавлено!\nТеперь введите ответ на русском языке:')
    await state.set_state(AddFaq.add_answer1)


@router.message(AddFaq.add_answer1)
async def add_questions(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(ru_answer=message.text)
    await message.answer('Добавлено!\nТеперь введите ответ на английском языке:')
    await state.set_state(AddFaq.add_answer2)


@router.message(AddFaq.add_answer2)
async def add_questions(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await state.update_data(en_answer=message.text)
    user_data = await state.get_data()

    ru_questions = user_data['ru_questions'].split('\n')
    en_questions = user_data['en_questions'].split('\n') if user_data.get('en_questions') else []

    await FAQDatabase.add_faq(
        answer_ru=user_data['ru_answer'],
        answer_en=user_data['en_answer'],
        questions_ru=ru_questions,
        questions_en=en_questions
    )
    await state.clear()
    await message.answer('Шаблон вопросов и ответ добавлен!', reply_markup=admin_main_menu())


@router.message(F.text == "Удалить вопрос")
async def delete_questions(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return

    faq_dict = {}
    data = await FAQDatabase.get_all_questions()

    if not data:
        await message.answer("Пока тут пусто", reply_markup=admin_main_menu())
        return

    for i in data:
        faq_id = i['faq_id']
        question_ru = i['question_ru']
        question_en = i['question_en']

        if faq_id not in faq_dict:
            faq_dict[faq_id] = {'ru': [], 'en': []}

        faq_dict[faq_id]['ru'].append(question_ru)
        faq_dict[faq_id]['en'].append(question_en)

    for faq_id, questions in faq_dict.items():
        result = f"ID: {faq_id}\n"
        result += f"Language: RU\n" + "\n".join(questions['ru'])
        result += f"\n\nLanguage: EN\n" + "\n".join(questions['en'])
        await message.answer(result)

    await message.answer('Выберите нужный вариант на клавиатуре ниже:',
                         reply_markup=faq_id_keyboard(set(i['faq_id'] for i in await FAQDatabase.get_all_questions())))
    await state.set_state(DeleteFaq.select_id)


@router.message(DeleteFaq.select_id)
async def delete_questions(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    if message.text.isdigit():
        if await FAQDatabase.delete_faq(int(message.text)):
            await state.clear()
            await message.answer('Шаблон успешно удален', reply_markup=admin_main_menu())
        else:
            await message.answer('При удалении была ошибка!', reply_markup=admin_main_menu())
    else:
        await message.answer('Выберите нужный вариант на клавиатуре ниже:',
                             reply_markup=faq_id_keyboard(
                                 set(i['faq_id'] for i in await FAQDatabase.get_all_questions())))
        await state.set_state(DeleteFaq.select_id)



@router.message(F.text == "Загрузить вопросы/ответы Excel")
async def add_xlsx_data(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer("Отправьте файл xlsx:", reply_markup=admin_back_menu())
    await state.set_state(AddXlsx.add)


@router.message(AddXlsx.add, lambda message: message.document is not None)
async def xlsx_data(message: types.Message, state: FSMContext):
    if message.document:
        document = message.document

        file_name = document.file_name
        if not file_name.lower().endswith('.xlsx'):
            await message.answer("Пожалуйста, отправьте файл с расширением .xlsx")
            return

        file_id = document.file_id

        file = await bot.get_file(file_id)
        save_path = os.path.join(FILES_PATH, file_name)

        await bot.download_file(file.file_path, save_path)

        await message.answer(f"Файл <{file_name}> успешно загружен, идет обработка ✅")
        if await ExcelOperation.add_xlsx_data(file_name):
            await message.answer("Данные успешно добавлены, обновляем нейросетевой поиск...")

            # Добавляем обновление нейросетевых эмбеддингов
            from bot_app.utils.neural_search import NeuralSearch
            await NeuralSearch.update_embeddings()

            await asyncio.sleep(2)
            await message.answer(f"Данные и нейросетевой поиск успешно обновлены ✅", reply_markup=admin_main_menu())
        else:
            await message.answer(f"Ошибка❌")
        await state.clear()
    await state.clear()


@router.message(F.text == "Изменить текст")
async def edit_text_handle(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer(f"Выберите пункт в котором нужно изменить текст:", reply_markup=edit_text_button())
    await state.set_state(EditText.edit_t1)


@router.message(EditText.edit_t1)
async def edit_text_state(message: types.Message, state: FSMContext):
    button_code = sections_mapping.get(message.text)
    await state.update_data(button_code=button_code)
    await message.answer(f"Введите текст на русском языке:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(EditText.edit_t2)


@router.message(EditText.edit_t2)
async def edit_text_state(message: types.Message, state: FSMContext):
    await state.update_data(ru_text=message.text)
    await message.answer('Добавлено!\nВведите текст на английском языке:')
    await state.set_state(EditText.edit_t3)


@router.message(EditText.edit_t3)
async def edit_text_state(message: types.Message, state: FSMContext):
    data = await state.get_data()
    button_code = data['button_code']
    ru_text = data['ru_text']
    en_text = message.text
    await TranslationDB.add_admin_translation(button_code, ru_text, en_text)
    await message.answer('Добавлено!\nТекст изменен.', reply_markup=admin_main_menu())
    await state.clear()


# @router.message(F.text == "Изменить 'Другие вопросы'")
# async def edit_other_issues(message: types.Message, state: FSMContext):
#     if message.from_user.id != ADMIN_ID:
#         return
#     await message.answer(f"Введите текст на русском языке:", reply_markup=ReplyKeyboardRemove())
#     await state.set_state(UpdateOtherIssuesText.admin_text1)
#
#
# @router.message(UpdateOtherIssuesText.admin_text1)
# async def edit_other_issues_state(message: types.Message, state: FSMContext):
#     if message.from_user.id != ADMIN_ID:
#         return
#     await state.update_data(ru_text=message.text)
#     await message.answer('Добавлено!\nВведите текст на английском языке:')
#     await state.set_state(UpdateOtherIssuesText.admin_text2)
#
#
# @router.message(UpdateOtherIssuesText.admin_text2)
# async def edit_other_issues_state(message: types.Message, state: FSMContext):
#     if message.from_user.id != ADMIN_ID:
#         return
#     data = await state.get_data()
#     ru_text = data['ru_text']
#     en_text = message.text
#     await TranslationDB.add_admin_translation("other_issues", ru_text, en_text)
#     await message.answer('Добавлено!\nТекст изменен.', reply_markup=admin_main_menu())
#     await state.clear()













