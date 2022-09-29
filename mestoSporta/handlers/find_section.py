from ast import Call
from re import L
from urllib.request import urlretrieve
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import time
import os
import urllib
import requests

from markups.add_section import *
from models.user import User
from models.city import City
from models.category import Category
from models.section import Section, SectionPhoto
from states.find_section import FindSection
from utils.db_connection import create_db_session

from markups.find_section import *


from email_validator import validate_email, EmailNotValidError


async def select_city(message: Message):
    await FindSection.City.set()
    kb = await get_cities_kb(offset=0)
    chat_id = message["from"]["id"]
    await message.bot.send_message(
        text="""
        Город🏢
        ---
        Выберите город из
        предложенного списка.
    """,
        chat_id=chat_id,
        reply_markup=kb,
    )


async def save_city_value_and_select_category(call: CallbackQuery, state: FSMContext):
    chat_id = call["from"]["id"]
    async with state.proxy() as data:
        data["city"] = call.data.split("_")[1]

    await FindSection.Category.set()

    kb = await f_get_categories_kb(offset=0)
    await call.bot.send_message(
        text="""
        Категория
        ---
        Необходимо определиться с
        категорией.
        Так мы сможем релевантно
        подобрать места.💪
    """,
        chat_id=chat_id,
        reply_markup=kb,
    )


async def metro_or_district(call: CallbackQuery, state: FSMContext):
    await FindSection.MetroOrDistrict.set()
    async with state.proxy() as data:
        data["category"] = call.data.split("_")[1]

    chat_id = call["from"]["id"]
    await call.bot.send_message(
        text="""
        Выбор метро или района
        ---
        По какому параметру сузить
        поиск мест.🗺
    """,
        chat_id=chat_id,
        reply_markup=metro_or_district_kb,
    )


async def by_metro(call: CallbackQuery, state: FSMContext):
    await FindSection.Metro.set()
    async with state.proxy() as data:
        data["by_metro"] = True
        
        kb = await get_metros_kb(city=data["city"], offset=0)

    chat_id = call["from"]["id"]

    await call.bot.send_message(
        text="""
        Метро
        ---
        Укажите станцию метро🚇
    """,
        chat_id=chat_id,
        reply_markup=kb,
    )


async def by_district(call: CallbackQuery, state: FSMContext):
    await FindSection.District.set()
    async with state.proxy() as data:
        data["by_district"] = True
        kb = await get_districts_kb(city=data["city"], offset=0)

    chat_id = call["from"]["id"]

    await call.bot.send_message(
        text="""
        Район
        ---
        Укажите район📍
    """,
        chat_id=chat_id,
        reply_markup=kb,
    )


async def select_training(call: CallbackQuery, state: FSMContext):
    await FindSection.Trainings.set()
    async with state.proxy() as data:
        data["metro_or_district"] = call.data.split("_")[1]

    kb = await get_trainigs_kb(offset=0)
    chat_id = call["from"]["id"]
    await call.bot.send_message(
        text="""
        Вид занятий
        ---
        Это может быть все, что угодно,
        от йоги и стретчинга до бокса
        и функциональных тренировок.🏋️‍♂️
        ---
        Вы можете написать в ответ боту
        вид занятий, который вас
        интересует⤵️
    """,
        chat_id=chat_id,
        reply_markup=kb,
    )


async def waiting_for_find(call: CallbackQuery, state: FSMContext):
    await FindSection.Wait.set()
    session_maker = await create_db_session()
    async with state.proxy() as data:
        data["traning"] = call.data

        category = await Category.get_category(
            session_maker=session_maker, name=data["category"]
        )
        category = category[0]
        if data.get("by_district"):
            district = await District.get_district(
                session_maker=session_maker, name=data["metro_or_district"]
            )
            district = district
            sections = await Section.find(
                session_maker=session_maker,
                city=data["city"],
                category_id=category.id,
                district_id=district[0].id,
            )
        else:
            metro = await Metro.get_metro(
                session_maker=session_maker, name=data["metro_or_district"]
            )
            sections = await Section.find(
                session_maker=session_maker,
                city=data["city"],
                category_id=category.id,
                metro_id=metro[0].id,
            )
        if sections == []:
            await call.bot.send_message(
                text="Подходящей секции не нашлось. ", chat_id=call['from']['id']
            )
        else:

            chat_id = call["from"]["id"]
            await call.bot.send_message(text="Ищем для вас места, ожидайте⏱", chat_id=chat_id)
            time.sleep(2)
            await call.bot.send_message(
                text="""
                Отлично!🏋️
                Нашли для тебя места,
                формируем список ⚙️
            """,
            chat_id=chat_id,
            )

            tranings = ""
            if type(sections[0].tranings) == list:
                for traning in sections[0].tranings:
                    tranings += traning + "\n"
            else:
                tranings = sections[0].tranings


            category = await Category.get_category(
                session_maker=session_maker, name=data["category"]
            )
            district = await District.get_district_by_id(
                session_maker=session_maker, id=sections[0].district_id
            )
            metro = await Metro.get_metro_by_id(
                session_maker=session_maker, id=sections[0].metro_id
            )

            data["section"] = sections[0]
            data['section_id'] = sections[0].id
            
            section_photo = await SectionPhoto.get_by_section_id(session_maker=session_maker, section_id=data['section'].id)
            
            if section_photo != []:
                photo = requests.get(section_photo[0].file_path)

                await call.bot.send_photo(
                photo=photo.content,
                caption=f"""
                    <b>{sections[0].title}</b>

                    Город:{sections[0].city}
                    Категория: {sections[0].category_id}
                    Адрес: {sections[0].address}
                    Район: {district[0].name}
                    Метро: {metro[0].name}

                    Виды занятий:
                    {tranings}
                """,
                chat_id=chat_id,
                reply_markup=waiting_for_find_kb,
                )
            else:
                await call.bot.send_message(
                    text=f"""
                    <b>{sections[0].title}</b>

                    Город:{sections[0].city}
                    Категория: {sections[0].category_id}
                    Адрес: {sections[0].address}
                    Район: {district[0].name}
                    Метро: {metro[0].name}

                    Виды занятий:
                    {tranings}
                """,
                chat_id=chat_id,
                reply_markup=waiting_for_find_kb,
                )


async def way(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        lat = data['section'].geoposition.split(' ')[0]
        long = data['section'].geoposition.split(" ")[1]

    await call.bot.send_message(text=f"""
        <a href='https://maps.yandex.ru/?ll={lat},{long}&z=12'>Открыть карту
Москвы в приложении Яндекс.Карты</a>
    """, chat_id=call['from']['id'])


async def consult(call: CallbackQuery, state: FSMContext):
    
    async with state.proxy() as data:
        await call.bot.send_message(
            text=f"""
            Подтвердите данные
            ---
            Место
            {data['section'].title}
            Имя
            {call['from']['first_name']}

            Телефон:

        """,
            chat_id=call["from"]["id"],
            reply_markup=consult_kb,
        )
    await call.bot.send_message(
        text = "Напишите свой номер телефона",
        chat_id = call['from']['id']
    )
    
    await call.bot.send_message(
        text=f"""
        Устанавливаем связь с местом
    """,
        chat_id=call["from"]["id"],
    )
    time.sleep(1)
    await call.bot.send_message(
        text=f"""
        Ваша заявка отправлена, в 
        рабочее время с вами свяжется
        менеджер места и ответит на все
        вопросы
        ---
        Спасибо, что воспользовались
        подбором, будем рады, если
        поддержите наш бот ₽(рублем)
    """,
        chat_id=call["from"]["id"],
        reply_markup=consult_sent_kb,
    )


async def feedback(call: CallbackQuery, state: FSMContext):
    await call.bot.send_message(
        text="""
        Оцените место⭐️
        ---
        Другие пользователи, при выборе места, будут учитывать рейтинг
    """,
        chat_id=call["from"]["id"],
        reply_markup=feedback_kb,
    )


async def feedback_text(call: CallbackQuery, state: FSMContext):

    rate = call.data.split("_")[1]
    session_maker = await create_db_session()
    async with state.proxy() as data:
        section = data["section"]
        await section.update_section_rates(session_maker=session_maker, rate=int(rate))

    await call.bot.send_message(
        text="""
        Напишите отзыв
        ---
        Вам нравится это место?
        Расскажите, почему!
    """,
        chat_id=call["from"]["id"],
    )


async def not_help(call: CallbackQuery, state: FSMContext):
    await call.bot.send_message(
        text="""
        Отлично
        Места, в которые вы отправили 
        заявки можно посмотреть, отправив команду
        ---
        /listplace 
    """,
        chat_id=call["from"]["id"],
    )

    time.sleep(10)
    await call.bot.send_message(
        text="""
        Привет!
        Это снова бот портала
        MestoSporta
        ---
        Скажите, связался ли с вами фитнес-клуб?
    """,
        chat_id=call["from"]["id"],
        reply_markup=yes_or_not_kb,
    )


async def yes_bot(call: CallbackQuery, state: FSMContext):
    await call.bot.send_message(
        text="""
        Спасибо за обратную связь. Хороших вам тренировок
    """,
    chat_id=call['from']['id']
    )


async def no_bot(call: CallbackQuery, state: FSMContext):
    await call.bot.send_message(
        text="""
        Спасибо за обратную связь. Мы поработаем над этим.
    """,
        chat_id=call["from"]["id"],
    )


def register_select_section(dp: Dispatcher):
    dp.register_callback_query_handler(select_city, text=["start_search"], state='*')
    dp.register_callback_query_handler(
        save_city_value_and_select_category,
        Text(startswith="city_"),
        state="*",
    )
    dp.register_callback_query_handler(
        metro_or_district, Text(startswith="findcategory_"), state=FindSection
    )
    dp.register_callback_query_handler(by_metro, text=["by_metro"], state='*')
    dp.register_callback_query_handler(
        by_district, text=["by_district"], state='*'
    )
    dp.register_callback_query_handler(
        select_training, Text(startswith="findmetro_"), state="*"
    )
    dp.register_callback_query_handler(
        select_training, Text(startswith="finddistrict_"), state='*'
    )
    dp.register_callback_query_handler(
        waiting_for_find, Text(startswith="findtraning_"), state='*'
    )

    dp.register_callback_query_handler(consult, text=["consult"], state='*')
    dp.register_callback_query_handler(feedback, text=["feedback"], state='*')
    dp.register_callback_query_handler(
        feedback_text, Text(startswith="rate_"), state='*'
    )

    dp.register_callback_query_handler(not_help, text=["not_help"], state='*')
    dp.register_callback_query_handler(yes_bot, text=["yes"], state='*')
    dp.register_callback_query_handler(no_bot, text=["no"], state='*')
    dp.register_callback_query_handler(way, text=['way'], state='*')

# def register_select_section(dp: Dispatcher):
#     dp.register_callback_query_handler(select_city, text=["start_search"])
#     dp.register_callback_query_handler(
#         save_city_value_and_select_category,
#         Text(startswith="city_"),
#         state=FindSection.City,
#     )
#     dp.register_callback_query_handler(
#         metro_or_district, Text(startswith="category_"), state=FindSection.Category
#     )
#     dp.register_callback_query_handler(by_metro, text=["by_metro"], state=FindSection)
#     dp.register_callback_query_handler(
#         by_district, text=["by_district"], state=FindSection
#     )
#     dp.register_callback_query_handler(
#         select_training, Text(startswith="metro_"), state=FindSection
#     )
#     dp.register_callback_query_handler(
#         select_training, Text(startswith="district_"), state=FindSection
#     )
#     dp.register_callback_query_handler(
#         waiting_for_find, Text(startswith="traning_"), state=FindSection
#     )

#     dp.register_callback_query_handler(consult, text=["consult"], state=FindSection)
#     dp.register_callback_query_handler(feedback, text=["feedback"], state=FindSection)
#     dp.register_callback_query_handler(
#         feedback_text, Text(startswith="rate_"), state=FindSection
#     )

#     dp.register_callback_query_handler(not_help, text=["not_help"], state=FindSection)
#     dp.register_callback_query_handler(yes_bot, text=["yes"], state=FindSection)
#     dp.register_callback_query_handler(no_bot, text=["no"], state=FindSection)
#     dp.register_callback_query_handler(way, text=['way'], state=FindSection)