from typing import Dict, Optional
from sqlalchemy.orm import Session

from infrastructure.database.repositories.access_repository import AccessRepository
from infrastructure.database.repositories.user_repository import UserRepository


class AccessService:
    """Сервис проверки доступа по Step1/Step2 архитектуре.
    
    Конструктор принимает Session, метод check_command_access возвращает Dict.
    """

    def __init__(self, db: Session):
        self.db = db
        self.access_repo = AccessRepository(db)
        self.user_repo = UserRepository(db)

    def check_command_access(self, telegram_user_id: int, command_name: str) -> Dict:
        """Проверка доступа пользователя к команде.
        
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
        has_access = self.access_repo.has_access(user.id, command_name)
        
        if not has_access:
            return {
                'has_access': False,
                'role': role_name,
                'message': f'Нет доступа к команде {command_name} для роли {role_name}'
            }
            
        return {
            'has_access': True,
            'role': role_name,
            'message': 'Доступ разрешен'
        }
