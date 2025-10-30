from __future__ import annotations
import os
from typing import Optional

from infrastructure.database.connection import session_scope
from infrastructure.database.repositories.access_repository import AccessRepository
from infrastructure.database.repositories.role_repository import RoleRepository
from infrastructure.database.repositories.user_repository import UserRepository

ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip().isdigit()}

class AccessService:
    def __init__(self):
        pass

    def is_admin(self, telegram_user_id: int) -> bool:
        return telegram_user_id in ADMIN_IDS

    def ensure_user(self, telegram_user_id: int, username: Optional[str], full_name: Optional[str]) -> None:
        with session_scope() as s:
            users = UserRepository(s)
            roles = RoleRepository(s)
            user = users.get_by_tg_id(telegram_user_id)
            if user is None:
                default_role = roles.get_by_name(os.getenv("DEFAULT_USER_ROLE", "prodavan"))
                role_id = default_role.id if default_role else roles.get_by_name("prodavan").id
                users.create(telegram_user_id, username, full_name, role_id)

    def can_execute(self, telegram_user_id: int, command_name: str) -> bool:
        if self.is_admin(telegram_user_id):
            return True
        with session_scope() as s:
            access = AccessRepository(s)
            return access.can_execute(telegram_user_id, command_name)
