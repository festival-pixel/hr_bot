from aiogram.fsm.state import State, StatesGroup


class ApplicationState(StatesGroup):
    fullname = State()
    age = State()
    phone = State()
    student = State()
    experience = State()
    last_workplace = State()
    has_children = State()
    children_count = State()
    youngest_child_age = State()
    address = State()
    location = State()
    languages = State()
    schedule = State()
    motivation = State()
    resume = State()
    confirm = State()
