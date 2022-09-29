from urllib.request import urlretrieve
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery, PreCheckoutQuery
from aiogram.types.successful_payment import SuccessfulPayment
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

import requests
import time
import os
import urllib

from config import config
from markups.add_section import *
from models.user import User
from models.city import City
from models.category import Category
from models.section import Section, SectionPhoto
from models.metro import Metro
from models.district import District
from states.add_section import AddSection
from utils.db_connection import create_db_session
from utils.get_district_and_metro import get_data

from pprint import pprint

from email_validator import validate_email, EmailNotValidError


async def change_context_add_section(message: Message):
    await AddSection.City.set()
    kb = await get_cities_kb(offset=0)
    chat_id = message["from"]["id"]
    await message.bot.send_message(
        text="""
        Город 🏢
        ---
        Выберите город из списка⤵️
        ---
        Если ваш город отсутствует, то
        напишите его в ответ.
    """,
        chat_id=chat_id,
        reply_markup=kb,
    )


async def save_city_value(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["city"] = call.data.split("_")[1]

    await AddSection.next()

    category_kb = await get_categories_kb(offset=0)
    chat_id = call["from"]["id"]
    await call.bot.send_message(
        text="""
        В какую Категорию добавить
        ваше место?
        ---
        На данный момент активные
        категории⤵️
    """,
        chat_id=chat_id,
        reply_markup=category_kb,
    )


async def save_category_value(call: CallbackQuery, state: FSMContext):
    async with state.proxy() as data:
        data["category"] = call.data.split("_")[1]

    chat_id = call["from"]["id"]
    await call.bot.send_message(
        text="""
        Название фитнес-клуба🏋️
        ---
        Напишите в ответ⤵️
    """,
        chat_id=chat_id,
    )

    await AddSection.next()


async def save_section_name(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["name"] = message["text"]
        data["urls"] = []

    chat_id = message["from"]["id"]
    await message.bot.send_message(
        text="""
        Адрес фитнес-клуба📍
        (пример:ул. Льва Толстого,д.16)
        ---
        Напишите в ответ⤵️
    """,
        chat_id=chat_id,
    )

    await AddSection.next()


async def save_section_address(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["address"] = message["text"]

        chat_id = message["from"]["id"]
        await message.bot.send_message(text="Wait a minute...", chat_id=chat_id)

        data["district"], data["geoposition"], data["metro"] = get_data(data['city'] + ' ' + data["address"])
        session_maker = await create_db_session()
        try:
            metro = await Metro.create(
                session_maker=session_maker, name=data["metro"], city=data["city"]
            )
        except Exception as e:
            print(e)

        try:
            await District.create(
                session_maker=session_maker, name=data["district"], city=data["city"]
            )
        except Exception as e:
            print(e)
        category = await Category.get_category(
            session_maker=session_maker, name=data["category"]
        )
        data["category_id"] = category[0].id

    time.sleep(3)
    async with state.proxy() as data:
        await message.bot.send_message(
            text=f"""
            🔥Супер!
            Давайте проверим адрес
            {data['address']}

            📍 Район
            {data['district']}            

            🚇Метро
            {data['metro']}

        """,
            chat_id=chat_id,
            reply_markup=confirm_kb,
        )


async def pre_save_images(call: CallbackQuery, state: FSMContext):
    await AddSection.next()
    chat_id = call["from"]["id"]
    await call.bot.send_message(
        text="""
        Добавим фото фитнес-клубу
        ---
        Нажми на скрепку 📎 и прикрепи
        мне фотографии, которые ты хочешь отправить!

        ❗️ Важно! Дождись загрузки всех
        фото.
        ❗️ Когда отправишь все фото, просто нажми "Готово"⤵️
    """,
        chat_id=chat_id,
        reply_markup=send_photos_kb,
    )


async def save_images(call: CallbackQuery, state: FSMContext):
    photo = call.photo.pop()
    urls = await photo.get_url()
    async with state.proxy() as data:
        data["urls"].append(urls)
    await photo.download(f'photos/{photo["file_unique_id"]}')


async def write_trainings(call: CallbackQuery, state: FSMContext):
    await AddSection.next()
    chat_id = call["from"]["id"]
    await call.bot.send_message(
        text="""
        Виды занятий
        ---
        Через запятую или с новой
        строки напишите виды занятий,
        которые есть в фитнес-клубе⤵️

        Это может быть все, что угодно,
        от йоги и стретчинга до бокса
        и функциональных тренировок.🏋️

        Ознакомиться со списком
        занятий можно по 🔗
        https://mestosporta.io/list
    """,
        chat_id=chat_id,
        reply_markup=write_trainings_kb,
    )


async def save_trainings(message: Message, state: FSMContext):
    async with state.proxy() as data:
        data["tranings"] = message["text"].replace(" ", "").split(",")

    time.sleep(1)
    await message.bot.send_message(
        text="""
        Напишите адрес электронной почты ✉️

        На нее будут приходить заявки
        от клиентов🔥
    """,
        chat_id=message["from"]["id"],
    )
    await AddSection.next()


async def write_email(message: Message, state: FSMContext):
    await AddSection.next()
    async with state.proxy() as data:
        try:
            validate_email(message["text"])
            data["email"] = message["text"]
            time.sleep(1)
            await message.bot.send_message(
                text="Группируем информацию, ожидайте", chat_id=message["from"]["id"]
            )

            tranings = ""
            for traning in data["tranings"]:
                tranings += f"{traning} \n"

            if data["urls"] != []:
                photo = requests.get(data["urls"][0])
                await message.bot.send_photo(
                    photo=photo.content,
                    caption=f"""
                    Последний шаг☑️
                    Давайте проверим информацию

                    Название:{data['name']}

                    Город:{data['city']}
                    Категория:{data['category']}
                    Адрес:{data['address']}
                    Район:{data['district']}
                    Метро:{data['metro']}

                    Электронная почта:
                    {data['email']}

                    Виды занятий:
                    {tranings}

                """,
                    chat_id=message["from"]["id"],
                    reply_markup=confirm_anket_kb,
                )

            else:
                await message.bot.send_message(
                    text=f"""
                    Последний шаг☑️
                    Давайте проверим информацию

                    Название:{data['name']}

                    Город:{data['city']}
                    Категория:{data['category']}
                    Адрес:{data['address']}
                    Район:{data['district']}
                    Метро:{data['metro']}

                    Электронная почта:
                    {data['email']}

                    Виды занятий:
                    {tranings}

                """,
                    chat_id=message["from"]["id"],
                    reply_markup=confirm_anket_kb,
                )

        except EmailNotValidError as e:
            await message.bot.send_message(
                text="""
                Это не совсем похоже на почту!
                Перепроверьте, пожалуйста.
            """,
                chat_id=message["from"]["id"],
            )


async def save_data(call: CallbackQuery, state: FSMContext):
    await call.bot.send_message(text="Сохраняем данные ♻️", chat_id=call["from"]["id"])

    async with state.proxy() as data:
        session_maker = await create_db_session()

        user = await User.get_user(
            session_maker=session_maker, telegram_id=call["from"]["id"]
        )
        tranings = ""
        if type(data["tranings"]) == list:
            for traning in data["tranings"]:
                tranings += traning + ", "
        metro = await Metro.get_metro(session_maker=session_maker, name=data["metro"])

        district = await District.get_district(
            session_maker=session_maker, name=data["district"]
        )
        section = await Section.add(
            session_maker=session_maker,
            title=data["name"],
            address=data["address"],
            category_id=data["category_id"],
            geoposition=data["geoposition"],
            metro_id=metro[0].id,
            district_id=district[0].id,
            city=data["city"],
            email=data["email"],
            user_id=user.telegram_id,
            tranings=tranings,
        )
        for photo_url in data['urls']:
            await SectionPhoto.add(session_maker=session_maker,
            file_path=photo_url,
            section_id=section.id)

    time.sleep(1)
    await call.bot.send_message(
        text="""
        Ваше место отправлено на модерацию.
        ---
        Оплатите подписку и получайте
        заявки от клиентов без ограничений.
        ❗️ Стоимость подписки в месяц 299₽.⤵️
    """,
        chat_id=call["from"]["id"],
        reply_markup=success_anket_kb,
    )


async def subscribe(call: CallbackQuery, state: FSMContext):
    await AddSection.next()

    await call.bot.send_invoice(
        chat_id=call["from"]["id"],
        title="Оформление подписки",
        description="Подписка на месяц",
        payload="month_sub",
        provider_token=config["YOOTOKEN"],
        currency="RUB",
        start_parameter="test_bot",
        prices=[{"label": "Руб", "amount": 29900}],
    )

    await call.bot.send_message(
        chat_id=call["from"]["id"],
        text="""
    Отлично🏆
    Спасибо, что добавили место.
    ---
    Ваши места можно посмотреть, отправив команду /list
    """,
    )


async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.bot.answer_pre_checkout_query(
        pre_checkout_query.id, ok=True
    )


async def process_pay(message: Message):
    session_maker = await create_db_session()
    if message.successful_payment.invoice_payload == "month_sub":
        user = await User.get_user(message["from"]["id"])
        await user.set_subscription(session_maker)


async def not_subscribe(call: CallbackQuery, state: FSMContext):
    await call.bot.send_message(
        chat_id=call["from"]["id"],
        text="❗️ Стоимость каждого нового клиента без подписки составит 99₽",
    )

    await call.bot.send_message(
        chat_id=call["from"]["id"],
        text="""
    Отлично🏆
    Спасибо, что добавили место.
    ---
    Ваши места можно посмотреть, отправив команду /list
    """,
    )

def register_add_section_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(change_context_add_section, text=["add_place"])
    dp.register_callback_query_handler(
        save_city_value, Text(startswith="city_"), state=AddSection.City
    )
    dp.register_callback_query_handler(
        save_category_value, Text(startswith="category_"), state=AddSection
    )
    dp.register_message_handler(
        save_section_name, Text(startswith=""), state=AddSection.Name
    )
    dp.register_message_handler(
        save_section_address, Text(startswith=""), state=AddSection.Address
    )
    dp.register_callback_query_handler(
        pre_save_images, text=["confirm_section"], state=AddSection.Address
    )
    dp.register_message_handler(
        save_images, content_types=["photo"], state=AddSection.Photos
    )
    dp.register_callback_query_handler(
        write_trainings, text=["write_trainings"], state=AddSection.Photos
    )
    dp.register_message_handler(
        save_trainings, Text(startswith=""), state=AddSection.Trainings
    )
    dp.register_message_handler(
        write_email, Text(startswith=""), state=AddSection.Email
    )
    dp.register_callback_query_handler(save_data, text=["save_data"], state='*')
    dp.register_callback_query_handler(subscribe, text=["subscribe"], state='*')
    dp.pre_checkout_query_handler(process_pre_checkout_query)
    dp.register_message_handler(process_pay, content_types=[SuccessfulPayment])
    dp.register_callback_query_handler(
        not_subscribe, text=["not_subscribe"], state='*'
    )

# def register_add_section_handlers(dp: Dispatcher):
#     dp.register_callback_query_handler(change_context_add_section, text=["add_place"])
#     dp.register_callback_query_handler(
#         save_city_value, Text(startswith="city_"), state=AddSection.City
#     )
#     dp.register_callback_query_handler(
#         save_category_value, Text(startswith="category_"), state=AddSection.Category
#     )
#     dp.register_message_handler(
#         save_section_name, Text(startswith=""), state=AddSection.Name
#     )
#     dp.register_message_handler(
#         save_section_address, Text(startswith=""), state=AddSection.Address
#     )
#     dp.register_callback_query_handler(
#         pre_save_images, text=["confirm_section"], state=AddSection.Address
#     )
#     dp.register_message_handler(
#         save_images, content_types=["photo"], state=AddSection.Photos
#     )
#     dp.register_callback_query_handler(
#         write_trainings, text=["write_trainings"], state=AddSection.Photos
#     )
#     dp.register_message_handler(
#         save_trainings, Text(startswith=""), state=AddSection.Trainings
#     )
#     dp.register_message_handler(
#         write_email, Text(startswith=""), state=AddSection.Email
#     )
#     dp.register_callback_query_handler(save_data, text=["save_data"])
#     dp.register_callback_query_handler(subscribe, text=["subscribe"], state=AddSection)
#     dp.pre_checkout_query_handler(process_pre_checkout_query)
#     dp.register_message_handler(process_pay, content_types=[SuccessfulPayment])
#     dp.register_callback_query_handler(
#         not_subscribe, text=["not_subscribe"], state=AddSection
#     )
