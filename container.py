"""Composition root — wires repositories and services (DI)."""

from functools import lru_cache

from apps.pqr.repositories import (
    PQRRepository,
    SeguimientoRepository,
    SolicitanteRepository,
)
from apps.pqr.services.notification_service import build_notifier
from apps.pqr.services.pqr_service import PQRService
from apps.pqr.services.seguimiento_service import SeguimientoService
from apps.pqr.services.stats_service import StatsService


class Container:
    def __init__(self):
        self.solicitante_repository = SolicitanteRepository()
        self.pqr_repository = PQRRepository()
        self.seguimiento_repository = SeguimientoRepository()
        self.notifier = build_notifier()

        self.pqr_service = PQRService(
            self.pqr_repository,
            self.solicitante_repository,
            self.seguimiento_repository,
            self.notifier,
        )
        self.seguimiento_service = SeguimientoService(
            self.pqr_repository,
            self.seguimiento_repository,
        )
        self.stats_service = StatsService(self.pqr_repository)


@lru_cache(maxsize=1)
def get_container() -> Container:
    return Container()
