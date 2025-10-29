# -*- coding: utf-8 -*-
"""
Dependency Injection Container

Здесь управляются все зависимости проекта:
- Конфигурации
- Сервисы
- Репозитории
- Внешние клиенты
"""

from dependency_injector import containers, providers
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode

from app.config.settings import Settings
from app.config.database import DatabaseConfig
from infrastructure.database.connection import DatabaseConnection
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.external.telegram_client import TelegramClient


class Container(containers.DeclarativeContainer):
    """DI контейнер для управления зависимостями"""
    
    # Конфигурация
    config = providers.Configuration()
    
    # Настройки
    settings = providers.Singleton(
        Settings
    )
    
    # База данных
    db_config = providers.Singleton(
        DatabaseConfig,
        settings=settings
    )
    
    db_connection = providers.Singleton(
        DatabaseConnection,
        config=db_config
    )
    
    # Кеш
    redis_cache = providers.Singleton(
        RedisCache,
        settings=settings
    )
    
    # Telegram Bot
    bot = providers.Singleton(
        Bot,
        token=settings.provided.bot_token,
        parse_mode=ParseMode.HTML
    )
    
    dispatcher = providers.Singleton(
        Dispatcher
    )
    
    # Внешние клиенты
    telegram_client = providers.Factory(
        TelegramClient,
        bot=bot
    )
    
    # Репозитории будут добавлены здесь
    # repositories = providers.Resource(...)
    
    # Сервисы будут добавлены здесь
    # services = providers.Resource(...)
