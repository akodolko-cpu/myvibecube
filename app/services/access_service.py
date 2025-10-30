from __future__ import annotations
import os
from typing import Optional

from infrastructure.database.connection import session_scope
from infrastructure.database.repositories.access_repository import AccessRepository
from infrastructure.database.repositories.role_repository import RoleRepository
from infrastructure.database.repositories.user_repository import UserRepository


def _env_admin_ids() -> set[int]:
    raw = os.getenv("ADMIN_IDS", "")
    return {int(x) for x in raw.split(",") if x.strip().isdigit()}


class AccessService:
    def __init__(self):
        pass

    def is_admin(self, telegram_user_id: int) -> bool:
        # Требование: человек считается админом ТОЛЬКО если
        # 1) он указан в ADMIN_IDS И
        # 2) его роль в БД = 'admin'
        if int(telegram_user_id) not in _env_admin_ids():
            return False
        with session_scope() as s:
            users = UserRepository(s)
            roles = RoleRepository(s)
            user = users.get_by_tg_id(telegram_user_id)
            if user is None:
                return False
            admin_role = roles.get_by_name("admin")
            return admin_role is not None and user.role_id == admin_role.id

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
        # Если не админ — проверяем доступ через ACL из БД
        with session_scope() as s:
            access = AccessRepository(s)
            return access.can_execute(telegram_user_id, command_name)
