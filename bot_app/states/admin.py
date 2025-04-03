from aiogram.fsm.state import StatesGroup, State


class AddFaq(StatesGroup):
    add_questions1 = State()
    add_questions2 = State()
    add_answer1 = State()
    add_answer2 = State()


class DeleteFaq(StatesGroup):
    select_id = State()


class AddXlsx(StatesGroup):
    add = State()

class UpdateFaqText(StatesGroup):
    admin_text1 = State()
    admin_text2 = State()

class UpdateOtherIssuesText(StatesGroup):
    admin_text1 = State()
    admin_text2 = State()