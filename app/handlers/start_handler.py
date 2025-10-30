from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from punq import Container

from infrastructure.database.connection import session_scope
from infrastructure.database.repositories.user_repository import UserRepository


def register_start_handler(router: Router, container: Container):
    """Register start command handler"""

    @router.message(Command("start"))
    async def start_command(message: Message) -> None:
        """Handle /start command.
        Правило доступа: если пользователя нет в БД (users), бот молчит.
        Если есть — отправляет приветствие и список команд.
        """
        tg_id = message.from_user.id

        with session_scope() as s:
            users = UserRepository(s)
            user = users.get_by_tg_id(tg_id)
            if user is None:
                # Не авторизован — ничего не отвечаем
                return

        welcome_text = (
            f"👋 Привет, {message.from_user.first_name}!\n\n"
            "🤖 Я MyVibe Bot - твой помощник для работы!\n\n"
            "📊 Доступные команды:\n"
            "/start - Начать работу\n"
            "/access - Управление доступом (admin)\n\n"
            "✨ Использую aiogram + punq DI + SQLAlchemy!"
        )
        await message.answer(welcome_text, parse_mode=ParseMode.HTML)
