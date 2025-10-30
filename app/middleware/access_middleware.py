from __future__ import annotations
from functools import wraps
from typing import Callable

from app.services.access_service import AccessService

access_service = AccessService()

def require_access(command_name: str):
    """Decorator to require specific access level for command handlers."""
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(update, context, *args, **kwargs):
            user = update.effective_user
            # Ensure user exists in database
            access_service.ensure_user(
                user.id, 
                user.username, 
                f"{user.first_name or ''} {user.last_name or ''}".strip()
            )
            
            # Check if user can execute this command
            if not access_service.can_execute(user.id, command_name):
                await update.effective_chat.send_message("❌ Недостаточно прав для выполнения команды.")
                return
            
            return await func(update, context, *args, **kwargs)
        return wrapper
    return decorator
