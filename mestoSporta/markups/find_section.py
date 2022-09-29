from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from models.district import District

from utils.db_connection import create_db_session
from models.city import City
from models.category import Category
from models.metro import Metro
from models.traning import Traning

metro_or_district_kb = InlineKeyboardMarkup()
metro_or_district_kb.add(
    InlineKeyboardButton(text="По метро", callback_data="by_metro")
)
metro_or_district_kb.add(
    InlineKeyboardButton(text="По району", callback_data="by_district")
)
metro_or_district_kb.add(InlineKeyboardButton(text="Назад", callback_data="city_s"))


async def f_get_categories_kb(offset:int=0):

    session = await create_db_session()
    categories = await Category.get_limited(session, offset=offset)

    categories_kb = InlineKeyboardMarkup()
    for category in categories:
        categories_kb.add(InlineKeyboardButton(f'{category.name}', callback_data=f'findcategory_{category.name}'))
    
    categories_kb.add(InlineKeyboardButton("«", callback_data='start_search'))

    return categories_kb


async def get_metros_kb(city: str, offset: int = 0):
    session_maker = await create_db_session()

    metros_kb = InlineKeyboardMarkup()
    metros = await Metro.filter_by_city(
        session_maker=session_maker, city=city, offset=offset
    )


    for metro in metros:
        metros_kb.add(
            InlineKeyboardButton(
                text=f"{metro.name}", callback_data=f"findmetro_{metro.name}"
            )
        )

    metros_kb.add(InlineKeyboardButton(text="Назад", callback_data="findcategory_ "))
    return metros_kb



async def get_districts_kb(city: str, offset: int = 0):
    session_maker = await create_db_session()

    districts_kb = InlineKeyboardMarkup()
    districts = await District.filter_by_city(
        session_maker=session_maker, city=city, offset=offset
    )
    for district in districts:
        districts_kb.add(
            InlineKeyboardButton(
                text=f"{district.name}", callback_data=f"finddistrict_{district.name}"
            )
        )

    districts_kb.add(InlineKeyboardButton(text="Назад", callback_data="findcategory_ "))

    return districts_kb


async def get_trainigs_kb(offset: int = 0):
    session_maker = await create_db_session()

    tranings_kb = InlineKeyboardMarkup()
    tranings = await Traning.get_limited(session_maker=session_maker, offset=offset)

    for traning in tranings:
        tranings_kb.add(
            InlineKeyboardButton(
                text=f"{traning.name}", callback_data=f"findtraning_{traning.name}"
            )
        )

    # tranings_kb.add(
    #     InlineKeyboardButton(text="След. страница", callback_data="select_tranings")
    # )

    return tranings_kb


waiting_for_find_kb = InlineKeyboardMarkup()
waiting_for_find_kb.add(
    InlineKeyboardButton("Получить консультанцию", callback_data="consult")
)
waiting_for_find_kb.add(InlineKeyboardButton("Как добраться", callback_data="way"))
waiting_for_find_kb.add(
    InlineKeyboardButton("Оставить отзыв", callback_data="feedback")
)
waiting_for_find_kb.add(
    InlineKeyboardButton("След. место", callback_data="next_section")
)
waiting_for_find_kb.add(InlineKeyboardButton("Назад", callback_data="finddistrict_ "))


consult_kb = InlineKeyboardMarkup()
consult_kb.add(InlineKeyboardButton("Отправить", callback_data="Send ancet"))
consult_kb.add(InlineKeyboardButton("Назад", callback_data="Back"))


consult_sent_kb = InlineKeyboardMarkup()
consult_sent_kb.add(InlineKeyboardButton("Поддержать", callback_data="subscribe"))
consult_sent_kb.add(
    InlineKeyboardButton("Спасибо, воздержусь", callback_data="not_help")
)


feedback_kb = InlineKeyboardMarkup()
feedback_kb.add(InlineKeyboardButton("⭐️⭐️⭐️⭐️⭐️(5)", callback_data="rate_5"))
feedback_kb.add(InlineKeyboardButton("⭐️⭐️⭐️⭐️(4)", callback_data="rate_4"))
feedback_kb.add(InlineKeyboardButton("⭐️⭐️⭐️(3)", callback_data="rate_3"))
feedback_kb.add(InlineKeyboardButton("⭐️⭐️(2)", callback_data="rate_2"))
feedback_kb.add(InlineKeyboardButton("⭐️(1)", callback_data="rate_1"))


yes_or_not_kb = InlineKeyboardMarkup()
yes_or_not_kb.add(InlineKeyboardButton("Да", callback_data="yes"))
yes_or_not_kb.add(InlineKeyboardButton("Нет", callback_data="no"))
