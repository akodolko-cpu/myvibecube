from __future__ import annotations

import punq
from app.services.access_service import AccessService

def setup_container() -> punq.Container:
    container = punq.Container()

    # Только сервисы (SessionLocal не регистрируем — forwardref ломает punq на Python 3.13)
    container.register(AccessService, factory=lambda: AccessService())

    return container
