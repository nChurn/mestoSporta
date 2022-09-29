from aiogram.dispatcher.filters.state import StatesGroup, State


class FindSection(StatesGroup):
    City = State()
    Category = State()
    MetroOrDistrict = State()
    Metro = State()
    District = State()
    Trainings = State()
    Wait = State()
