from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from punq import Container
from app.services.access_service import AccessService
from aiogram.utils.keyboard import InlineKeyboardBuilder


def register_access_handler(router: Router, container: Container):
    """Register access command handler with strict guards"""

    @router.message(Command("access"))
    async def access_command(message: Message) -> None:
        access_service = container.resolve(AccessService)

        # 1) Полная блокировка незарегистрированных (нет в users):
        from infrastructure.database.connection import session_scope
        from infrastructure.database.repositories.user_repository import UserRepository
        with session_scope() as s:
            if UserRepository(s).get_by_tg_id(message.from_user.id) is None:
                await message.answer("❌ Доступ запрещён. Ты никто. Обратись к администратору.")
                return

        # 2) Доступ к /access — только строгий админ (ENV + DB role=admin)
        if not access_service.is_admin(message.from_user.id):
            await message.answer("❌ Доступ запрещён. Недостаточно прав.")
            return

        # Корневое меню диалога
        kb = InlineKeyboardBuilder()
        kb.button(text="➕ Добавить пользователя", callback_data="access:add")
        kb.button(text="➖ Удалить пользователя", callback_data="access:remove")
        kb.button(text="❌ Отмена", callback_data="access:cancel")
        kb.adjust(1)
        await message.answer("Выберите действие:", reply_markup=kb.as_markup())
