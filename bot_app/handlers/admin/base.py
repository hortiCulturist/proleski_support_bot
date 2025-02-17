from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from bot_app.config import ADMIN_ID
from bot_app.db.admin.base import FAQDatabase
from bot_app.markups.admin import admin_main_menu, admin_no_translate, faq_id_keyboard
from bot_app.misc import router
from bot_app.states.admin import AddFaq, DeleteFaq


@router.message(F.text == "Добавить вопрос")
async def add_questions(message: types.Message, state: FSMContext):
    if message.from_user.id != ADMIN_ID:
        return
    await message.answer('Введите вопрос/ы на русском языке:', reply_markup=ReplyKeyboardRemove())
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



