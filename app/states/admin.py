from aiogram.fsm.state import State, StatesGroup


class AdminState(StatesGroup):
    search_query = State()
    invite_date = State()
