from __future__ import annotations

import logging
import os
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

logger = logging.getLogger(__name__)

# Priority: split DB_* variables, then fallback to DATABASE_URL
DB_HOST = os.getenv("DB_HOST", os.getenv("DB_SERVER", "localhost"))
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")

if DB_NAME and DB_USER and DB_PASS:
    port = DB_PORT or "3306"
    DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{port}/{DB_NAME}"
else:
    DB_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:@localhost:3306/telegram_bot")

ECHO = os.getenv("DATABASE_ECHO", "False").lower() == "true"
POOL_SIZE = int(os.getenv("DATABASE_POOL_SIZE", "10"))
MAX_OVERFLOW = int(os.getenv("DATABASE_MAX_OVERFLOW", "20"))
POOL_TIMEOUT = int(os.getenv("DATABASE_TIMEOUT", "30"))

engine = create_engine(
    DB_URL,
    echo=ECHO,
    pool_size=POOL_SIZE,
    max_overflow=MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=1800,
    pool_timeout=POOL_TIMEOUT,
    future=True,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        logger.exception("DB transaction rolled back due to exception")
        raise
    finally:
        session.close()
