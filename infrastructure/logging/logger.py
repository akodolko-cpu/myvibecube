# -*- coding: utf-8 -*-
"""
Logging setup
"""

import logging
from app.config.settings import Settings


def setup_logging() -> None:
    settings = Settings()
    logging.basicConfig(level=settings.log_level, format=settings.log_format)
