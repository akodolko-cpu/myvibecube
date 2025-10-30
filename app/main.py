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
import os
from pathlib import Path

# Добавляем корневую папку в путь для импортов
import sys
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
from telegram.ext import ApplicationBuilder

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, os.getenv("LOG_LEVEL", "INFO")),
    format=os.getenv("LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
)

def main():
    """Главная функция запуска бота"""
    logger = logging.getLogger(__name__)
    
    try:
        # Получаем токен бота
        token = os.getenv("BOT_TOKEN")
        if not token:
            raise RuntimeError("BOT_TOKEN не установлен в .env файле")
        
        # Создаем приложение
        app = ApplicationBuilder().token(token).build()
        
        # Импортируем и регистрируем обработчики
        from app.handlers.start_handler import get_handler as start_handler
        from app.handlers.access_handler import get_handler as access_handler
        
        # Регистрируем обработчики
        app.add_handler(start_handler())
        app.add_handler(access_handler())
        
        logger.info("🚀 MyVibe Bot запускается...")
        logger.info("✅ ЭТАП 1: Система управления доступом активирована")
        logger.info("📋 Доступные команды: /start, /access")
        
        # Запуск бота
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Ошибка запуска бота: {e}")
        raise


if __name__ == "__main__":
    main()
