# -*- coding: utf-8 -*-
"""
Асинхронное подключение к БД (SQLAlchemy)
"""

from typing import Any
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.config.database import DatabaseConfig


class DatabaseConnection:
    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._engine: AsyncEngine = create_async_engine(
            config.database_url,
            echo=config.echo,
            future=True,
        )

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    async def dispose(self) -> None:
        await self._engine.dispose()
