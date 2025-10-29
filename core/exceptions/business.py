# -*- coding: utf-8 -*-
"""
Бизнес-исключения

Специфичные исключения, связанные с бизнес-логикой
приложения MyVibe Bot.
"""

from .base import DomainException


class BusinessLogicException(DomainException):
    """Общее бизнес-исключение"""
    pass


class UserAlreadyExistsException(BusinessLogicException):
    """Пользователь уже существует"""
    pass


class InsufficientPermissionsException(BusinessLogicException):
    """Недостаточно прав для выполнения операции"""
    pass


class ReportGenerationException(BusinessLogicException):
    """Ошибка генерации отчёта"""
    pass
