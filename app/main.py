#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MyVibe Telegram Bot - Main Entry Point

Это основная точка входа в приложение.
Здесь происходит:
- Инициализация DI контейнера
- Регистрация всех обработчиков
- Запуск бота
"""

import asyncio
import logging

from app.config.settings import Settings
from app.container import Container
from handlers.common.start_handler import register_start_handlers
from infrastructure.logging.logger import setup_logging


async def main() -> None:
    """Главная функция запуска бота"""
    # Настройка логирования
    setup_logging()
    logger = logging.getLogger(__name__)
    
    try:
        # Загрузка настроек
        settings = Settings()
        
        # Инициализация DI контейнера
        container = Container(settings)
        container.wire(modules=[__name__])
        
        # Получение бота из контейнера
        dp = container.dispatcher()
        bot = container.bot()
        
        # Регистрация обработчиков
        register_start_handlers(dp)
        
        logger.info("🚀 MyVibe Bot запускается...")
        
        # Запуск бота
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
