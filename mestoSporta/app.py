from aiogram import Dispatcher, Bot, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage

import logging
import asyncio

from utils.db_connection import create_db_session

from config import config


def register_all_handlers(dp):
    from handlers.hello import register_handlers

    register_handlers(dp)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )

    bot = Bot(token=config["BOT_TOKEN"], parse_mode="HTML")
    storage = MemoryStorage()
    dp = Dispatcher(bot, storage=storage)

    bot["db"] = await create_db_session()

    register_all_handlers(dp)

    await dp.start_polling()


if __name__ == "__main__":
    asyncio.run(main())
