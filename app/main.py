#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import logging
import os

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

from app.container import setup_container

load_dotenv()

logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
)


def main():
    logger = logging.getLogger(__name__)

    token = os.getenv("BOT_TOKEN")
    if not token:
        raise RuntimeError("BOT_TOKEN не установлен в .env")

    app = ApplicationBuilder().token(token).build()

    # DI container
    container = setup_container()

    # Handlers registration
    from app.handlers.start_handler import get_handler as start_handler
    from app.handlers.access_handler import get_handler as access_handler

    app.add_handler(start_handler())
    app.add_handler(access_handler())

    logger.info("🚀 MyVibe Bot (punq DI) запускается...")
    app.run_polling()


if __name__ == "__main__":
    main()
