from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from punq import Container
from app.services.access_service import AccessService
from app.handlers.access_dialog import register_user_manage_dialog


def register_access_handler(router: Router, container: Container):
    """Register access command handler.
    Заменён на запуск интерактивного диалога управления пользователями.
    """

    # Регистрация самого диалога
    register_user_manage_dialog(router)

    @router.message(Command("access"))
    async def access_command(message: Message) -> None:
        access_service = container.resolve(AccessService)
        # Доступ только для админов (по строгому правилу ENV+DB)
        if not access_service.is_admin(message.from_user.id):
            await message.answer("❌ Доступ запрещён.")
            return
        # Покажем корневое меню диалога
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        kb = InlineKeyboardBuilder()
        kb.button(text="➕ Добавить пользователя", callback_data="access:add")
        kb.button(text="➖ Удалить пользователя", callback_data="access:remove")
        kb.button(text="❌ Отмена", callback_data="access:cancel")
        kb.adjust(1)
        await message.answer("Выберите действие:", reply_markup=kb.as_markup())
