#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
import logging
import os

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.container import setup_container

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

    # Register handlers
    from app.handlers.start_handler import register_start_handler
    from app.handlers.access_handler import register_access_handler

    register_start_handler(dp, container)
    register_access_handler(dp, container)

    logger.info("🚀 MyVibe Bot (aiogram + punq DI) запускается...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
