from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db_connection import create_db_session
from models.city import City
from models.category import Category


hello_kb_btn_1 = InlineKeyboardButton("Начать подбор", callback_data="start_search")
hello_kb_btn_2 = InlineKeyboardButton("Добавить место", callback_data="add_place")
hello_kb = InlineKeyboardMarkup().add(hello_kb_btn_1, hello_kb_btn_2)
