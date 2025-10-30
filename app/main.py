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

    # Register all handlers via central registrar
    router = Router()
    register_all_handlers(router, container)
    dp.include_router(router)

    logger.info("🚀 MyVibe Bot (aiogram + punq DI) запускается...")
    
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
