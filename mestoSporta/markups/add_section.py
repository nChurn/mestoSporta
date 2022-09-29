from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

from utils.db_connection import create_db_session
from models.city import City
from models.category import Category


async def get_cities_kb(offset:int=0):
    
    session = await create_db_session()
    cities = await City.get_limited(session, offset=offset)

    cities_kb = InlineKeyboardMarkup()
    for city in cities:
        cities_kb.add(InlineKeyboardButton(f'{city.name}', callback_data=f'city_{city.name}'))
        
    #cities_kb.add(InlineKeyboardButton("«", callback_data="start"))

    return cities_kb


async def get_categories_kb(offset:int=0):

    session = await create_db_session()
    categories = await Category.get_limited(session, offset=offset)

    categories_kb = InlineKeyboardMarkup()
    for category in categories:
        categories_kb.add(InlineKeyboardButton(f'{category.name}', callback_data=f'category_{category.name}'))
    
    # categories_kb.add(InlineKeyboardButton("«", callback_data='add_place'))

    return categories_kb


confirm_kb = InlineKeyboardMarkup()
confirm_kb.add(InlineKeyboardButton("Да, верно", callback_data='confirm_section'))
confirm_kb.add(InlineKeyboardButton("Нет, не верно", callback_data='category_ '))
confirm_kb.add(InlineKeyboardButton("«", callback_data='category_ '))

send_photos_kb = InlineKeyboardMarkup()
send_photos_kb.add(InlineKeyboardButton("Далее", callback_data='write_trainings'))
send_photos_kb.add(InlineKeyboardButton("Назад", callback_data='category_ '))


write_trainings_kb = InlineKeyboardMarkup()
write_trainings_kb.add(InlineKeyboardButton("Далее", callback_data='save_tranings'))
# NOT PRE_SAVE
#write_trainings_kb.add(InlineKeyboardButton("Назад", callback_data='confirm_section'))


confirm_anket_kb = InlineKeyboardMarkup()
confirm_anket_kb.add(InlineKeyboardButton("Да, все верно", callback_data='save_data'))
confirm_anket_kb.add(InlineKeyboardButton("Назад", callback_data='back'))


success_anket_kb = InlineKeyboardMarkup()
success_anket_kb.add(InlineKeyboardButton("Оформить подписку", callback_data='subscribe'))
success_anket_kb.add(InlineKeyboardButton("Спасибо, воздержусь", callback_data='not_subscribe'))


