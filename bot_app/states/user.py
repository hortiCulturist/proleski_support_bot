from aiogram.fsm.state import StatesGroup, State


class UserInfo(StatesGroup):
    user_issue = State()


class UserPhone(StatesGroup):
    user_phone = State()