from urllib.request import urlretrieve
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types.inline_keyboard import InlineKeyboardMarkup, InlineKeyboardButton

import time
import os
import urllib


from markups.hello import *
from models.user import User
from models.city import City
from models.category import Category
from models.section import Section
from states.add_section import AddSection
from utils.db_connection import create_db_session

from pprint import pprint

from handlers.add_section import register_add_section_handlers
from handlers.find_section import register_select_section

from email_validator import validate_email, EmailNotValidError


async def hello(message: Message):
    user = message["from"]
    session_maker = await create_db_session()
    try:
        await User.add_user(
            session_maker=session_maker,
            telegram_id=user["id"],
            first_name=user["first_name"],
            last_name=user["last_name"],
            lang_code=user["language_code"],
            username=user["username"],
            role="user",
        )
    except Exception as e:
        print(e)

    await message.answer(
        """
        Привет!👋
        Это бот портала <b>MestoSporta</b>🏆
        ---
        Персонально и бесплатно помогу
        подобрать спортивную услугу
        или забронировать спорт.
        площадку в твоем городе 🏢
        ---
        Если ты владелец или
        представитель спортивного
        места, добавляй его к нам в
        сообщество и продвигай спорт в массы ⛳️
    
    """,
        reply_markup=hello_kb,
    )


async def list_command(message: Message):
    session_maker = await create_db_session()
    sections = await Section.find_user_sections(
        session_maker=session_maker, user_id=message["from"]["id"]
    )
    section_kb = InlineKeyboardMarkup()
    for section in sections:
        section_kb.add(
            InlineKeyboardButton(
                f"{section.title}", callback_data=f"section_{section.title}"
            )
        )


async def section_card(call: CallbackQuery):
    session_maker = await create_db_session()
    section = await Section.get_user_section(
        session_maker=session_maker,
        user_id=call["from"]["id"],
        name=call.data.split("_")[1],
    )
    tranigs = ""
    for traning in section.tranings.replace(" ", "").split(","):
        tranings += f"{traning} \n"
    await call.bot.send_message(
        text=f"""
    Название:
    <b>{section.title}</b>
    Город:{section.city}
    Категория:{section.category}
    Адрес: {section.address}
    Район: {section.district}
    Метро: {section.metro}

    Электронная почта:
    {section.email}
    Виды занятий:
    {tranigs}
    """
    )


def register_handlers(dp: Dispatcher):
    register_add_section_handlers(dp)
    register_select_section(dp)

    dp.register_message_handler(hello, commands=["start"], state="*")
    dp.register_message_handler(list_command, commands=["list"], state="*")
    dp.register_callback_query_handler(section_card, Text(startswith="section_"))
    dp.register_message_handler(hello, text=['start'], state='*')
