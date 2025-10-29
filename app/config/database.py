# -*- coding: utf-8 -*-
"""
Конфигурация базы данных

Настройки подключения к БД, пулы соединений,
параметры миграций.
"""

from typing import Optional
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config.settings import Settings


# Базовый класс для моделей
Base = declarative_base()


class DatabaseConfig:
    """Конфигурация базы данных"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.database_url = settings.database_url
        self.echo = settings.database_echo
        
        # Создание асинхронного движка
        self.async_engine = create_async_engine(
            self.database_url,
            echo=self.echo,
            future=True
        )
        
        # Фабрика сессий
        self.async_session_factory = sessionmaker(
            bind=self.async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncSession:
        """Получить асинхронную сессию БД"""
        async with self.async_session_factory() as session:
            yield session
    
    async def close(self) -> None:
        """Закрыть соединения с БД"""
        await self.async_engine.dispose()
