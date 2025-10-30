from aiogram import Router
from app.handlers.access_dialog import register_user_manage_dialog
from app.handlers.start_handler import register_start_handler
from app.handlers.access_handler import register_access_handler


def register_all_handlers(router: Router, container):
    # Базовые команды
    register_start_handler(router, container)
    register_access_handler(router, container)
    # Диалог управления пользователями
    register_user_manage_dialog(router)
