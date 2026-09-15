from apps.common.logging import get_logger
from apps.pqr.repositories.pqr_repository import PQRRepository

logger = get_logger(__name__)


class StatsService:
    def __init__(self, pqr_repository: PQRRepository):
        self._pqrs = pqr_repository

    def get_summary(self) -> dict:
        por_estado = self._pqrs.count_by_estado()
        por_tipo = self._pqrs.count_by_tipo()
        total = sum(item["total"] for item in por_estado)
        logger.debug("stats_summary", total=total)
        return {
            "total": total,
            "por_estado": por_estado,
            "por_tipo": por_tipo,
        }
