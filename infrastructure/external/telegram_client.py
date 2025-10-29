# -*- coding: utf-8 -*-
"""
Telegram client wrapper
"""

from aiogram import Bot


class TelegramClient:
    def __init__(self, bot: Bot) -> None:
        self._bot = bot

    @property
    def bot(self) -> Bot:
        return self._bot
