from __future__ import annotations
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from app.middleware.access_middleware import require_access
from app.services.access_service import AccessService

access_service = AccessService()

@require_access("/access")
async def access_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /access command for user management."""
    args = context.args or []
    
    # Only admins can use this command
    if not access_service.is_admin(update.effective_user.id):
        await update.effective_chat.send_message("❌ Команда доступна только администраторам.")
        return

    # Show usage if no args provided
    if len(args) < 3 or args[0] not in {"add", "set"}:
        usage_text = (
            "📝 **Управление пользователями:**\n\n"
            "• `/access add <telegram_id> <role>` - добавить пользователя\n"
            "• `/access set <telegram_id> <role>` - изменить роль\n\n"
            "**Доступные роли:**\n"
            "• `admin` - администратор (полный доступ)\n"
            "• `rop` - руководитель отдела продаж\n"
            "• `topmanager` - топ-менеджер\n"
            "• `stm` - старший менеджер\n"
            "• `prodavan` - продавец"
        )
        await update.effective_chat.send_message(usage_text, parse_mode='Markdown')
        return

    action, tg_id_str, role_name = args[0], args[1], args[2]
    
    # Validate telegram ID
    if not tg_id_str.isdigit():
        await update.effective_chat.send_message("❌ Telegram ID должен быть числом.")
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
            await update.effective_chat.send_message(f"❌ Роль '{role_name}' не найдена.")
            return

        # Get or create user
        user = users.get_by_tg_id(tg_id)
        if user is None:
            users.create(tg_id, None, None, role.id)
            await update.effective_chat.send_message(
                f"✅ Пользователь {tg_id} добавлен с ролью **{role_name}**.",
                parse_mode='Markdown'
            )
        else:
            users.set_role(user.id, role.id)
            await update.effective_chat.send_message(
                f"✅ Пользователю {tg_id} назначена роль **{role_name}**.",
                parse_mode='Markdown'
            )

def get_handler():
    """Return the command handler for /access."""
    return CommandHandler("access", access_command)
