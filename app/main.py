#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.container import setup_container
from app.handlers import register_all_handlers

# STEP 2 logging (logger)
from app.logger import bot_logger
from app.middleware.access_log_middleware import AccessLogMiddleware

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
)


async def main():
    logger = logging.getLogger(__name__)

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN не установлен в .env")

    # DI container
    container = setup_container()

    # Bot and Dispatcher
    bot = Bot(
        token=token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    # Подключаем middleware до регистрации роутеров
    dp.update.middleware(AccessLogMiddleware())

    # Register all handlers via central registrar (ЭТАП 1)
    router = Router()
    register_all_handlers(router, container)
    dp.include_router(router)

    # Логгер STEP 2 готов (используется во всех местах)
    bot_logger.info("🚀 MyVibe Bot (aiogram + punq DI) запускается... (STEP 2 logging ready)")

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())