from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from datetime import datetime

# Предполагаем, что модели и репозитории уже существуют в проекте
from infrastructure.database.models import ActionLog
from infrastructure.database.repositories.user_repository import UserRepository


class ActionLogService:
    """Сервис для логирования всех действий пользователей"""

    def __init__(self, db: Session):
        self.db = db

    def log_action(
        self,
        telegram_user_id: int,
        action_type: str,
        command_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
    ) -> ActionLog:
        user_repo = UserRepository(self.db)
        user = user_repo.get_user_by_telegram_id(telegram_user_id)

        log = ActionLog(
            user_id=user.id if user else None,
            action_type=action_type,
            command_name=command_name,
            details={"success": success, "timestamp": datetime.utcnow().isoformat(), **(details or {})},
            created_at=datetime.utcnow(),
        )
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def log_command_executed(self, telegram_user_id: int, command_name: str, success: bool = True):
        return self.log_action(telegram_user_id, 'command_executed', command_name, success=success)

    def log_command_denied(self, telegram_user_id: int, command_name: str, reason: str = 'access_denied'):
        return self.log_action(telegram_user_id, 'command_denied', command_name, details={'reason': reason}, success=False)

    def log_user_added(self, admin_id: int, new_user_id: int, role_name: str):
        return self.log_action(admin_id, 'user_added', details={'new_user_id': new_user_id, 'role': role_name}, success=True)

    def log_user_deleted(self, admin_id: int, deleted_user_id: int):
        return self.log_action(admin_id, 'user_deleted', details={'deleted_user_id': deleted_user_id}, success=True)

    def log_user_role_changed(self, admin_id: int, user_id: int, new_role: str, old_role: str):
        return self.log_action(admin_id, 'user_role_changed', details={'user_id': user_id, 'old_role': old_role, 'new_role': new_role}, success=True)
