from aiogram.dispatcher.filters.state import StatesGroup, State


class AddSection(StatesGroup):
    City = State()
    Category = State()
    Name = State()
    Address = State()
    Photos = State()
    Trainings = State()
    Email = State()
    Save = State()
    Subscribtion = State()