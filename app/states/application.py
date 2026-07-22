from aiogram.fsm.state import State, StatesGroup


class ApplicationState(StatesGroup):
    fullname = State()
    age = State()
    phone = State()
    student = State()
    address = State()
    location = State()
    languages = State()
    schedule = State()
    motivation = State()
    resume = State()
    confirm = State()
