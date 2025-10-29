# -*- coding: utf-8 -*-
"""
Простой Redis-кеш (шаблон)
"""

from typing import Optional

from app.config.settings import Settings


class RedisCache:
    def __init__(self, settings: Settings) -> None:
        self._url = settings.redis_url
        self._ttl = settings.cache_ttl
        # Заглушка: тут можно подключить aioredis

    async def get(self, key: str) -> Optional[str]:
        return None

    async def set(self, key: str, value: str, ttl: Optional[int] = None) -> None:
        return None
