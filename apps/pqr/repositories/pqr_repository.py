from django.db.models import Count, QuerySet

from apps.pqr.models import PQR


class PQRRepository:
    def base_queryset(self) -> QuerySet[PQR]:
        return PQR.objects.select_related("solicitante")

    def get_by_id(self, pqr_id: int) -> PQR | None:
        return (
            self.base_queryset()
            .prefetch_related("seguimientos__usuario")
            .filter(pk=pqr_id)
            .first()
        )

    def get_by_radicado(self, radicado: str) -> PQR | None:
        return (
            self.base_queryset()
            .prefetch_related("seguimientos__usuario")
            .filter(radicado__iexact=radicado.strip())
            .first()
        )

    def list_filtered(self, filters: dict) -> QuerySet[PQR]:
        qs = self.base_queryset()
        if tipo := filters.get("tipo"):
            qs = qs.filter(tipo=tipo)
        if estado := filters.get("estado"):
            qs = qs.filter(estado=estado)
        if prioridad := filters.get("prioridad"):
            qs = qs.filter(prioridad=prioridad)
        if categoria := filters.get("categoria"):
            qs = qs.filter(categoria__icontains=categoria)
        return qs

    def create(self, **data) -> PQR:
        return PQR.objects.create(**data)

    def save(self, pqr: PQR, update_fields: list[str] | None = None) -> PQR:
        pqr.save(update_fields=update_fields)
        return pqr

    def count_by_estado(self) -> list[dict]:
        return list(
            PQR.objects.values("estado")
            .annotate(total=Count("id"))
            .order_by("estado")
        )

    def count_by_tipo(self) -> list[dict]:
        return list(
            PQR.objects.values("tipo").annotate(total=Count("id")).order_by("tipo")
        )
