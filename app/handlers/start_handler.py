from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import Message

from punq import Container


def register_start_handler(router: Router, container: Container):
    """Register start command handler"""
    
    @router.message(Command("start"))
    async def start_command(message: Message) -> None:
        """Handle /start command"""
        user = message.from_user
        welcome_text = (
            f"👋 Привет, {user.first_name}!\n\n"
            "🤖 Я MyVibe Bot - твой помощник для работы!\n\n"
            "📊 Доступные команды:\n"
            "/start - Начать работу\n"
            "/access - Управление доступом (admin)\n\n"
            "✨ Использую aiogram + punq DI + SQLAlchemy!"
        )
        
        await message.answer(welcome_text)
