from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from punq import Container

from infrastructure.database.connection import session_scope
from infrastructure.database.repositories.user_repository import UserRepository


BLOCKED_CACHE: set[int] = set()


def register_start_handler(router: Router, container: Container):
    """Register start command handler"""

    @router.message(Command("start"))
    async def start_command(message: Message) -> None:
        tg_id = message.from_user.id

        # Если уже блокировали этого пользователя ранее — не отвечаем повторно
        if tg_id in BLOCKED_CACHE:
            return

        # Пускаем только зарегистрированных пользователей
        with session_scope() as s:
            users = UserRepository(s)
            user = users.get_by_tg_id(tg_id)
            if user is None:
                BLOCKED_CACHE.add(tg_id)
                await message.answer("❌ Ты никто. Нахер с пляжа.")
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
