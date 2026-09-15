from django.db.models import QuerySet

from apps.pqr.models import Seguimiento


class SeguimientoRepository:
    def list_by_pqr(self, pqr_id: int) -> QuerySet[Seguimiento]:
        return (
            Seguimiento.objects.select_related("usuario")
            .filter(pqr_id=pqr_id)
            .order_by("fecha_registro")
        )

    def create(self, **data) -> Seguimiento:
        return Seguimiento.objects.create(**data)
