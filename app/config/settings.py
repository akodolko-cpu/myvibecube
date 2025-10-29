# -*- coding: utf-8 -*-
"""
Настройки приложения

Все настройки приложения загружаются из переменных окружения
и имеют значения по умолчанию для разработки.
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Основные настройки приложения"""
    
    # === TELEGRAM BOT ===
    bot_token: str = os.getenv("BOT_TOKEN", "your_bot_token_here")
    webhook_url: Optional[str] = os.getenv("WEBHOOK_URL")
    webhook_secret: Optional[str] = os.getenv("WEBHOOK_SECRET")
    
    # === DATABASE ===
    database_url: str = os.getenv(
        "DATABASE_URL", 
        "sqlite+aiosqlite:///./myvibe.db"
    )
    database_echo: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"
    
    # === REDIS CACHE ===
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    cache_ttl: int = int(os.getenv("CACHE_TTL", "3600"))  # 1 час
    
    # === LOGGING ===
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_format: str = os.getenv(
        "LOG_FORMAT",
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # === SECURITY ===
    secret_key: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    
    # === API KEYS ===
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
