# -*- coding: utf-8 -*-
"""
Базовые исключения доменного слоя

Основные классы исключений, от которых наследуются
все остальные исключения в приложении.
"""

from typing import Optional, Dict, Any


class DomainException(Exception):
    """Базовое доменное исключение"""
    
    def __init__(
        self, 
        message: str, 
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code or self.__class__.__name__
        self.details = details or {}
    
    def __str__(self) -> str:
        return f"{self.code}: {self.message}"


class ValidationException(DomainException):
    """Исключение валидации данных"""
    pass


class NotFoundException(DomainException):
    """Исключение не найдено"""
    pass


class AccessDeniedException(DomainException):
    """Исключение отсутствия доступа"""
    pass
