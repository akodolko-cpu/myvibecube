from __future__ import annotations
from typing import Optional

from sqlalchemy import select
from sqlalchemy.orm import Session

# Пакетный импорт из infrastructure.database.models (__init__ реэкспортирует из orm.py)
from infrastructure.database.models import User, Role, Command, RoleCommand

class AccessRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_user_with_role(self, telegram_user_id: int) -> Optional[User]:
        q = select(User).where(User.telegram_user_id == telegram_user_id)
        return self.session.execute(q).scalar_one_or_none()

    def can_execute(self, telegram_user_id: int, command_name: str) -> bool:
        q = (
            select(RoleCommand)
            .join(Role, RoleCommand.role_id == Role.id)
            .join(Command, RoleCommand.command_id == Command.id)
            .join(User, User.role_id == Role.id)
            .where(
                User.telegram_user_id == telegram_user_id,
                User.is_active.is_(True),
                Command.command_name == command_name,
                Command.is_active.is_(True),
            )
        )
        return self.session.execute(q).scalar_one_or_none() is not None
