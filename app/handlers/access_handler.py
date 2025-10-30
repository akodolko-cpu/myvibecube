from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode

from punq import Container
from app.services.access_service import AccessService


def register_access_handler(router: Router, container: Container):
    """Register access command handler"""
    
    @router.message(Command("access"))
    async def access_command(message: Message) -> None:
        """Handle /access command for user management."""
        access_service = container.resolve(AccessService)
        
        # Extract command arguments from message text
        command_parts = message.text.split()
        args = command_parts[1:] if len(command_parts) > 1 else []
        
        # Only admins can use this command
        if not access_service.is_admin(message.from_user.id):
            await message.answer("❌ Команда доступна только администраторам.")
            return

        # Show usage if no args provided
        if len(args) < 3 or args[0] not in {"add", "set"}:
            usage_text = (
                "📝 <b>Управление пользователями:</b>\n\n"
                "• <code>/access add &lt;telegram_id&gt; &lt;role&gt;</code> - добавить пользователя\n"
                "• <code>/access set &lt;telegram_id&gt; &lt;role&gt;</code> - изменить роль\n\n"
                "<b>Доступные роли:</b>\n"
                "• <code>admin</code> - администратор (полный доступ)\n"
                "• <code>rop</code> - руководитель отдела продаж\n"
                "• <code>topmanager</code> - топ-менеджер\n"
                "• <code>stm</code> - старший менеджер\n"
                "• <code>prodavan</code> - продавец"
            )
            await message.answer(usage_text, parse_mode=ParseMode.HTML)
            return

        action, tg_id_str, role_name = args[0], args[1], args[2]
        
        # Validate telegram ID
        if not tg_id_str.isdigit():
            await message.answer("❌ Telegram ID должен быть числом.")
            return

        tg_id = int(tg_id_str)

        from infrastructure.database.connection import session_scope
        from infrastructure.database.repositories.user_repository import UserRepository
        from infrastructure.database.repositories.role_repository import RoleRepository

        with session_scope() as s:
            users = UserRepository(s)
            roles = RoleRepository(s)
            
            # Check if role exists
            role = roles.get_by_name(role_name)
            if role is None:
                await message.answer(f"❌ Роль '{role_name}' не найдена.")
                return

            # Get or create user
            user = users.get_by_tg_id(tg_id)
            if user is None:
                users.create(tg_id, None, None, role.id)
                await message.answer(
                    f"✅ Пользователь {tg_id} добавлен с ролью <b>{role_name}</b>.",
                    parse_mode=ParseMode.HTML
                )
            else:
                users.set_role(user.id, role.id)
                await message.answer(
                    f"✅ Пользователю {tg_id} назначена роль <b>{role_name}</b>.",
                    parse_mode=ParseMode.HTML
                )
