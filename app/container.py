from __future__ import annotations

import punq
from app.services.access_service import AccessService
from infrastructure.database.connection import SessionLocal


def setup_container() -> punq.Container:
    container = punq.Container()

    # Регистрируем фабрику, передающую новую Session в AccessService
    container.register(AccessService, factory=lambda: AccessService(SessionLocal()))

    return container
