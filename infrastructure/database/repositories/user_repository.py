from __future__ import annotations
from typing import Optional, Iterable

from sqlalchemy import select, update
from sqlalchemy.orm import Session

# Прямой импорт моделей из файла models.py
from infrastructure.database.models.models import User, Role

class UserRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_tg_id(self, telegram_user_id: int) -> Optional[User]:
        return self.session.execute(select(User).where(User.telegram_user_id == telegram_user_id)).scalar_one_or_none()

    def create(self, telegram_user_id: int, username: str | None, full_name: str | None, role_id: int) -> User:
        user = User(telegram_user_id=telegram_user_id, username=username, full_name=full_name, role_id=role_id)
        self.session.add(user)
        self.session.flush()
        return user

    def set_role(self, user_id: int, role_id: int) -> None:
        self.session.execute(update(User).where(User.id == user_id).values(role_id=role_id))

    def list(self) -> Iterable[User]:
        return self.session.execute(select(User).join(Role)).scalars().all()
