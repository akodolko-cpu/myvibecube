from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable

from infrastructure.database.connection import session_scope
from app.services.log_service import ActionLogService
from services.access_service import AccessService


class AccessLogMiddleware(BaseMiddleware):
    """Aiogram middleware: проверка доступа и логирование команд в БД"""

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Интересуют только текстовые команды вида /...
        msg = event if isinstance(event, Message) else getattr(event, "message", None)
        if not msg or not msg.text or not msg.text.startswith('/'):
            return await handler(event, data)

        command = msg.text.split()[0]
        tg_id = msg.from_user.id

        with session_scope() as s:
            access = AccessService(s)
            check = access.check_command_access(tg_id, command)
            if not check.get('has_access', False):
                # Логируем отказ и сообщаем пользователю
                ActionLogService(s).log_command_denied(tg_id, command, reason=check.get('message','denied'))
                await msg.answer(f"❌ Доступ запрещён\n\n{check.get('message','')}\nКоманда: {command}")
                return
            # Логируем успешный вызов команды
            ActionLogService(s).log_command_executed(tg_id, command, success=True)

        return await handler(event, data)
