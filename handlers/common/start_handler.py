# -*- coding: utf-8 -*-
"""
Стартовые команды и базовые приветствия
"""

from aiogram import Router, types
from aiogram.filters import CommandStart, Command

router = Router()


def register_start_handlers(dp):
    dp.include_router(router)


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я MyVibe Bot. Готов к работе.")


@router.message(Command("ping"))
async def cmd_ping(message: types.Message):
    await message.answer("pong")
