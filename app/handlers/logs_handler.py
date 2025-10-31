from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from punq import Container

from app.services.log_service import ActionLogService
from infrastructure.database.connection import get_db


async def logs_command_handler(message: Message, container: Container):
    """Обработчик команды /logs (только для admin) - aiogram версия"""
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    
    # Показываем меню просмотра логов
    keyboard = [
        [InlineKeyboardButton(text="📊 Все логи (последние 50)", callback_data="logs_all")],
        [InlineKeyboardButton(text="✅ Успешные команды", callback_data="logs_success")],
        [InlineKeyboardButton(text="❌ Отказы в доступе", callback_data="logs_denied")],
        [InlineKeyboardButton(text="👤 Добавление пользователей", callback_data="logs_user_added")],
        [InlineKeyboardButton(text="🗑️ Удаление пользователей", callback_data="logs_user_deleted")],
        [InlineKeyboardButton(text="❌ Отменить", callback_data="logs_cancel")],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    await message.answer("📋 Выберите тип логов для просмотра:", reply_markup=reply_markup)


async def logs_callback_handler(query: CallbackQuery, container: Container):
    """Обработчик callback’ов для /logs"""
    db = next(get_db())
    log_service = ActionLogService(db)
    
    if query.data == "logs_all":
        logs = log_service.get_all_logs(limit=50)
        if not logs:
            await query.message.edit_text("📭 Логи не найдены")
            return
        
        log_text = "📊 Последние 50 логов:\n\n"
        for log in logs:
            user_name = log.user.full_name if hasattr(log, 'user') and log.user else "Unknown"
            log_text += f"• {log.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {user_name} - {log.action_type}"
            if log.command_name:
                log_text += f" ({log.command_name})"
            log_text += "\n"
        await query.message.edit_text(log_text[:4000])
        
    elif query.data in ["logs_success", "logs_denied", "logs_user_added", "logs_user_deleted"]:
        action_type_map = {
            "logs_success": "command_executed",
            "logs_denied": "command_denied",
            "logs_user_added": "user_added",
            "logs_user_deleted": "user_deleted"
        }
        action_type = action_type_map[query.data]
        
        logs = log_service.get_all_logs(action_type=action_type, limit=30)
        if not logs:
            await query.message.edit_text(f"📭 Логи с типом '{action_type}' не найдены")
            return
            
        log_text = f"📋 Логи (тип: {action_type}):\n\n"
        for log in logs:
            user_name = log.user.full_name if hasattr(log, 'user') and log.user else "Unknown"
            log_text += f"• {log.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {user_name}\n"
        await query.message.edit_text(log_text[:4000])
        
    elif query.data == "logs_cancel":
        await query.message.edit_text("❌ Отменено")

    await query.answer()


def register_logs_handler(router: Router, container: Container):
    """Регистрация обработчиков /logs"""
    
    # Команда /logs
    @router.message(Command("logs"))
    async def logs_command(message: Message):
        await logs_command_handler(message, container)
    
    # Callback’ы для меню логов
    @router.callback_query(lambda c: c.data and c.data.startswith('logs_'))
    async def logs_callback(query: CallbackQuery):
        await logs_callback_handler(query, container)
