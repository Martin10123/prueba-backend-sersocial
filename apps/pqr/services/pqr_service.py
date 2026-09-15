from datetime import datetime

from django.db import transaction
from django.utils import timezone

from apps.accounts.models import UserRole
from apps.common.exceptions import (
    InvalidTransitionError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from apps.common.logging import get_logger
from apps.pqr.models import (
    ALLOWED_TRANSITIONS,
    EstadoPQR,
    PQR,
    TipoAccionSeguimiento,
)
from apps.pqr.repositories.pqr_repository import PQRRepository
from apps.pqr.repositories.seguimiento_repository import SeguimientoRepository
from apps.pqr.repositories.solicitante_repository import SolicitanteRepository
from apps.pqr.services.notification_service import NotificationPort

logger = get_logger(__name__)


class PQRService:
    def __init__(
        self,
        pqr_repository: PQRRepository,
        solicitante_repository: SolicitanteRepository,
        seguimiento_repository: SeguimientoRepository,
        notifier: NotificationPort,
    ):
        self._pqrs = pqr_repository
        self._solicitantes = solicitante_repository
        self._seguimientos = seguimiento_repository
        self._notifier = notifier

    def list_pqrs(self, filters: dict):
        return self._pqrs.list_filtered(filters)

    def get_pqr(self, pqr_id: int) -> PQR:
        pqr = self._pqrs.get_by_id(pqr_id)
        if pqr is None:
            raise NotFoundError(f"PQR {pqr_id} no encontrada.")
        return pqr

    def buscar_por_radicado(self, radicado: str) -> PQR:
        if not radicado or not radicado.strip():
            raise ValidationError("El radicado es obligatorio.")
        pqr = self._pqrs.get_by_radicado(radicado)
        if pqr is None:
            raise NotFoundError(f"No existe PQR con radicado {radicado}.")
        return pqr

    @transaction.atomic
    def create_pqr(self, data: dict) -> PQR:
        payload = dict(data)
        solicitante_data = dict(payload.pop("solicitante"))
        solicitante, created = self._solicitantes.get_or_create_by_identificacion(
            identificacion=solicitante_data["identificacion"],
            defaults={
                "nombre": solicitante_data["nombre"],
                "apellido": solicitante_data["apellido"],
                "email": solicitante_data["email"],
                "telefono": solicitante_data.get("telefono", ""),
            },
        )
        if not created:
            # Keep contact data fresh without duplicating rows.
            for field in ("nombre", "apellido", "email", "telefono"):
                if field in solicitante_data and solicitante_data[field]:
                    setattr(solicitante, field, solicitante_data[field])
            solicitante.save(
                update_fields=["nombre", "apellido", "email", "telefono"]
            )

        radicado = self._generate_radicado()
        pqr = self._pqrs.create(
            radicado=radicado,
            solicitante=solicitante,
            estado=EstadoPQR.RECIBIDA,
            **payload,
        )
        self._seguimientos.create(
            pqr=pqr,
            descripcion="PQR registrada en el sistema.",
            tipo_accion=TipoAccionSeguimiento.SISTEMA,
            usuario=None,
        )
        logger.info(
            "pqr_created",
            pqr_id=pqr.id,
            radicado=pqr.radicado,
            tipo=pqr.tipo,
            solicitante_id=solicitante.id,
        )
        self._notifier.send(
            subject=f"PQR recibida {pqr.radicado}",
            to_email=solicitante.email,
            body=(
                f"Su solicitud {pqr.radicado} fue registrada con estado "
                f"{pqr.get_estado_display()}."
            ),
            metadata={"pqr_id": pqr.id, "event": "created"},
        )
        return self.get_pqr(pqr.id)

    @transaction.atomic
    def update_estado_prioridad(
        self,
        *,
        pqr_id: int,
        user,
        estado: str | None = None,
        prioridad: str | None = None,
    ) -> PQR:
        pqr = self._pqrs.get_by_id(pqr_id)
        if pqr is None:
            raise NotFoundError(f"PQR {pqr_id} no encontrada.")

        if estado is None and prioridad is None:
            raise ValidationError("Debe enviar estado y/o prioridad.")

        update_fields: list[str] = ["updated_at"]

        if estado is not None and estado != pqr.estado:
            self._assert_transition_allowed(pqr.estado, estado, user)
            old = pqr.estado
            pqr.estado = estado
            update_fields.append("estado")
            self._seguimientos.create(
                pqr=pqr,
                descripcion=f"Estado: {old} → {estado}",
                tipo_accion=TipoAccionSeguimiento.CAMBIO_ESTADO,
                usuario=user,
            )
            logger.info(
                "pqr_estado_changed",
                pqr_id=pqr.id,
                from_estado=old,
                to_estado=estado,
                user_id=getattr(user, "id", None),
            )

        if prioridad is not None and prioridad != pqr.prioridad:
            old_prio = pqr.prioridad
            pqr.prioridad = prioridad
            update_fields.append("prioridad")
            self._seguimientos.create(
                pqr=pqr,
                descripcion=f"Prioridad: {old_prio} → {prioridad}",
                tipo_accion=TipoAccionSeguimiento.CAMBIO_PRIORIDAD,
                usuario=user,
            )
            logger.info(
                "pqr_prioridad_changed",
                pqr_id=pqr.id,
                from_prioridad=old_prio,
                to_prioridad=prioridad,
                user_id=getattr(user, "id", None),
            )

        self._pqrs.save(pqr, update_fields=update_fields)

        if "estado" in update_fields:
            self._notifier.send(
                subject=f"Actualización PQR {pqr.radicado}",
                to_email=pqr.solicitante.email,
                body=(
                    f"Su PQR {pqr.radicado} cambió a estado "
                    f"{pqr.get_estado_display()}."
                ),
                metadata={"pqr_id": pqr.id, "event": "estado_changed"},
            )

        return self.get_pqr(pqr.id)

    def _assert_transition_allowed(self, current: str, new: str, user) -> None:
        allowed = ALLOWED_TRANSITIONS.get(current, set())
        if new not in allowed:
            raise InvalidTransitionError(
                f"No se puede pasar de '{current}' a '{new}'."
            )
        if new == EstadoPQR.CERRADA:
            rol = getattr(user, "rol", None)
            if rol not in {UserRole.SUPERVISOR, UserRole.ADMIN}:
                raise PermissionDeniedError(
                    "Solo supervisor o admin pueden cerrar una PQR."
                )

    def _generate_radicado(self) -> str:
        now: datetime = timezone.localtime()
        prefix = now.strftime("PQR-%Y%m%d")
        # Count today's PQRs without N+1: single aggregate query.
        today_count = (
            PQR.objects.filter(radicado__startswith=prefix).count() + 1
        )
        return f"{prefix}-{today_count:04d}"
