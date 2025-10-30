from __future__ import annotations

import punq

from app.services.access_service import AccessService
from infrastructure.database.connection import SessionLocal


def setup_container() -> punq.Container:
    container = punq.Container()

    # DB session factory
    container.register("SessionLocal", SessionLocal)

    # Services
    container.register(AccessService, AccessService)

    return container
