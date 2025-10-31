from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from infrastructure.database.connection import get_db
from app.services.log_service import ActionLogService
from app.middleware.access_middleware import AccessMiddleware


@AccessMiddleware.require_access('/logs')
async def logs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📊 Все логи (последние 50)", callback_data="logs_all")],
        [InlineKeyboardButton("✅ Успешные команды", callback_data="logs_success")],
        [InlineKeyboardButton("❌ Отказы в доступе", callback_data="logs_denied")],
        [InlineKeyboardButton("👤 Добавление пользователей", callback_data="logs_user_added")],
        [InlineKeyboardButton("🗑️ Удаление пользователей", callback_data="logs_user_deleted")],
        [InlineKeyboardButton("❌ Отменить", callback_data="logs_cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📋 Выберите тип логов для просмотра:", reply_markup=reply_markup)


async def show_logs_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    db = next(get_db())
    logs = ActionLogService(db).get_all_logs(limit=50)

    if not logs:
        await update.callback_query.edit_message_text("📭 Логи не найдены")
        return

    log_text = "📊 Последние 50 логов:\n\n"
    for log in logs:
        user_name = log.user.full_name if getattr(log, 'user', None) else "Unknown"
        log_text += f"• {log.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {user_name} - {log.action_type}"
        if log.command_name:
            log_text += f" ({log.command_name})"
        log_text += "\n"

    await update.callback_query.edit_message_text(log_text[:4000])


async def show_logs_filtered(update: Update, context: ContextTypes.DEFAULT_TYPE, action_type: str):
    await update.callback_query.answer()
    db = next(get_db())
    logs = ActionLogService(db).get_all_logs(action_type=action_type, limit=30)

    if not logs:
        await update.callback_query.edit_message_text(f"📭 Логи с типом '{action_type}' не найдены")
        return

    log_text = f"📋 Логи (тип: {action_type}):\n\n"
    for log in logs:
        user_name = log.user.full_name if getattr(log, 'user', None) else "Unknown"
        log_text += f"• {log.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {user_name}\n"

    await update.callback_query.edit_message_text(log_text[:4000])


async def logs_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query.data == "logs_all":
        await show_logs_all(update, context)
    elif query.data == "logs_success":
        await show_logs_filtered(update, context, "command_executed")
    elif query.data == "logs_denied":
        await show_logs_filtered(update, context, "command_denied")
    elif query.data == "logs_user_added":
        await show_logs_filtered(update, context, "user_added")
    elif query.data == "logs_user_deleted":
        await show_logs_filtered(update, context, "user_deleted")
    elif query.data == "logs_cancel":
        await query.edit_message_text("❌ Отменено")
