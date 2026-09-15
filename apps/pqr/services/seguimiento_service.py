from apps.common.exceptions import NotFoundError, ValidationError
from apps.common.logging import get_logger
from apps.pqr.models import TipoAccionSeguimiento
from apps.pqr.repositories.pqr_repository import PQRRepository
from apps.pqr.repositories.seguimiento_repository import SeguimientoRepository

logger = get_logger(__name__)


class SeguimientoService:
    def __init__(
        self,
        pqr_repository: PQRRepository,
        seguimiento_repository: SeguimientoRepository,
    ):
        self._pqrs = pqr_repository
        self._seguimientos = seguimiento_repository

    def list_by_pqr(self, pqr_id: int):
        if self._pqrs.get_by_id(pqr_id) is None:
            raise NotFoundError(f"PQR {pqr_id} no encontrada.")
        return self._seguimientos.list_by_pqr(pqr_id)

    def add(self, *, pqr_id: int, descripcion: str, user, tipo_accion: str | None = None):
        pqr = self._pqrs.get_by_id(pqr_id)
        if pqr is None:
            raise NotFoundError(f"PQR {pqr_id} no encontrada.")
        if not descripcion or not descripcion.strip():
            raise ValidationError("La descripción del seguimiento es obligatoria.")

        seguimiento = self._seguimientos.create(
            pqr=pqr,
            descripcion=descripcion.strip(),
            tipo_accion=tipo_accion or TipoAccionSeguimiento.COMENTARIO,
            usuario=user if getattr(user, "is_authenticated", False) else None,
        )
        logger.info(
            "seguimiento_added",
            pqr_id=pqr_id,
            seguimiento_id=seguimiento.id,
            user_id=getattr(user, "id", None),
        )
        return seguimiento
