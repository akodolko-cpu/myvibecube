from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import select

from infrastructure.database.repositories.access_repository import AccessRepository
from infrastructure.database.repositories.user_repository import UserRepository
from infrastructure.database.models import Role, Command, RoleCommand


class AccessService:
    """Полноценный сервис проверки доступа по Step1/Step2 архитектуре.
    
    Конструктор принимает Session, все методы согласно документации.
    Использует REAL AccessRepository.can_execute() и UserRepository.get_by_tg_id().
    """

    def __init__(self, db: Session):
        self.db = db
        self.access_repo = AccessRepository(db)
        self.user_repo = UserRepository(db)

    def check_command_access(self, telegram_user_id: int, command_name: str) -> Dict:
        """Проверка доступа пользователя к команде (для middleware).
        
        Returns:
            Dict с полями: has_access (bool), role (str), message (str)
        """
        user = self.user_repo.get_by_tg_id(telegram_user_id)
        if user is None:
            return {
                'has_access': False,
                'role': None,
                'message': 'Пользователь не зарегистрирован в системе'
            }
        
        role_name = user.role.role_name if hasattr(user, 'role') and user.role else 'unknown'
        
        # Используем REAL can_execute() метод из AccessRepository
        can_execute = self.access_repo.can_execute(telegram_user_id, command_name)
        
        if not can_execute:
            return {
                'has_access': False,
                'role': role_name,
                'message': f'Нет доступа к команде {command_name} для роли {role_name}'
            }
            
        return {
            'has_access': True,
            'role': role_name,
            'message': 'Доступ разрешён'
        }

    def is_admin(self, telegram_user_id: int) -> bool:
        """Проверка, является ли пользователь администратором."""
        user = self.user_repo.get_by_tg_id(telegram_user_id)
        if not user or not hasattr(user, 'role') or not user.role:
            return False
        return user.role.role_name == 'admin'

    def get_user_role_name(self, telegram_user_id: int) -> Optional[str]:
        """Получить название роли пользователя."""
        user = self.user_repo.get_by_tg_id(telegram_user_id)
        if not user or not hasattr(user, 'role') or not user.role:
            return None
        return user.role.role_name

    def get_user_commands(self, telegram_user_id: int) -> List[str]:
        """Получить список доступных команд для пользователя."""
        user = self.user_repo.get_by_tg_id(telegram_user_id)
        if not user or not hasattr(user, 'role') or not user.role:
            return []
        
        # Получаем команды через RoleCommand -> Command
        query = (
            select(Command.command_name)
            .join(RoleCommand, RoleCommand.command_id == Command.id)
            .where(
                RoleCommand.role_id == user.role.id,
                Command.is_active.is_(True)
            )
        )
        result = self.db.execute(query).scalars().all()
        return list(result)

    def has_access(self, telegram_user_id: int, command_name: str) -> bool:
        """Простая проверка доступа (возвращает bool)."""
        return self.access_repo.can_execute(telegram_user_id, command_name)

    def get_role_commands(self, role_id: int) -> List[str]:
        """Получить список команд для роли."""
        query = (
            select(Command.command_name)
            .join(RoleCommand, RoleCommand.command_id == Command.id)
            .where(
                RoleCommand.role_id == role_id,
                Command.is_active.is_(True)
            )
        )
        result = self.db.execute(query).scalars().all()
        return list(result)
