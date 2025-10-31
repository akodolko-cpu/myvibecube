from telegram import Update
from telegram.ext import ContextTypes
from typing import Callable

from infrastructure.database.connection import get_db
from app.services.access_service import AccessService
from app.logger import log_command_start, log_access_denied


class AccessMiddleware:
    @staticmethod
    async def require_access(command_name: str):
        def decorator(handler: Callable):
            async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
                if not update.message:
                    return await handler(update, context)
                user_id = update.effective_user.id
                db = next(get_db())
                result = AccessService(db).check_command_access(user_id, command_name)
                if not result['has_access']:
                    log_access_denied(user_id, command_name)
                    await update.message.reply_text(f"❌ Доступ запрещен\n\n{result['message']}")
                    return
                log_command_start(user_id, command_name)
                return await handler(update, context)
            return wrapper
        return decorator

    @staticmethod
    async def check_access_before_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        if not update.message or not update.message.text:
            return True
        if not update.message.text.startswith('/'):
            return True
        command = update.message.text.split()[0]
        user_id = update.effective_user.id
        db = next(get_db())
        result = AccessService(db).check_command_access(user_id, command)
        if not result['has_access']:
            log_access_denied(user_id, command)
            await update.message.reply_text(f"❌ Доступ запрещен\n\n{result['message']}")
            return False
        log_command_start(user_id, command)
        return True
