from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from datetime import datetime

from infrastructure.database.models import ActionLog
from infrastructure.database.repositories.user_repository import UserRepository


class ActionLogService:
    """Сервис для логирования всех действий пользователей"""

    def __init__(self, db: Session):
        self.db = db

    # === WRITE API ===
    def log_action(
        self,
        telegram_user_id: int,
        action_type: str,
        command_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        success: bool = True,
    ) -> ActionLog:
        user = UserRepository(self.db).get_user_by_telegram_id(telegram_user_id)
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
        return self.log_action(telegram_user_id, "command_executed", command_name, success=success)

    def log_command_denied(self, telegram_user_id: int, command_name: str, reason: str = "access_denied"):
        return self.log_action(telegram_user_id, "command_denied", command_name, details={"reason": reason}, success=False)

    def log_user_added(self, admin_id: int, new_user_id: int, role_name: str):
        return self.log_action(admin_id, "user_added", details={"new_user_id": new_user_id, "role": role_name}, success=True)

    def log_user_deleted(self, admin_id: int, deleted_user_id: int):
        return self.log_action(admin_id, "user_deleted", details={"deleted_user_id": deleted_user_id}, success=True)

    def log_user_role_changed(self, admin_id: int, user_id: int, new_role: str, old_role: str):
        return self.log_action(admin_id, "user_role_changed", details={"user_id": user_id, "old_role": old_role, "new_role": new_role}, success=True)

    # === READ API ===
    def get_user_action_logs(self, telegram_user_id: int, limit: int = 50) -> List[ActionLog]:
        user = UserRepository(self.db).get_user_by_telegram_id(telegram_user_id)
        if not user:
            return []
        return (
            self.db.query(ActionLog)
            .filter(ActionLog.user_id == user.id)
            .order_by(ActionLog.created_at.desc())
            .limit(limit)
            .all()
        )

    def get_all_logs(self, action_type: Optional[str] = None, limit: int = 100) -> List[ActionLog]:
        query = self.db.query(ActionLog)
        if action_type:
            query = query.filter(ActionLog.action_type == action_type)
        return query.order_by(ActionLog.created_at.desc()).limit(limit).all()
