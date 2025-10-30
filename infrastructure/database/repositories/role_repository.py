from __future__ import annotations
from typing import Optional, Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session

from infrastructure.database.models import Role, RoleCommand, Command

class RoleRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_name(self, role_name: str) -> Optional[Role]:
        return self.session.execute(select(Role).where(Role.role_name == role_name)).scalar_one_or_none()

    def get_by_id(self, role_id: int) -> Optional[Role]:
        return self.session.execute(select(Role).where(Role.id == role_id)).scalar_one_or_none()

    def list(self) -> Iterable[Role]:
        return self.session.execute(select(Role)).scalars().all()

    def role_has_command(self, role_id: int, command_name: str) -> bool:
        q = (
            select(RoleCommand)
            .join(Command, RoleCommand.command_id == Command.id)
            .where(
                RoleCommand.role_id == role_id,
                Command.command_name == command_name,
                Command.is_active.is_(True),
            )
        )
        return self.session.execute(q).scalar_one_or_none() is not None
