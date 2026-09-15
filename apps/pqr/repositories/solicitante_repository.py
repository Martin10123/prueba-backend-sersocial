from apps.pqr.models import Solicitante


class SolicitanteRepository:
    def get_by_identificacion(self, identificacion: str) -> Solicitante | None:
        return Solicitante.objects.filter(identificacion=identificacion).first()

    def create(self, **data) -> Solicitante:
        return Solicitante.objects.create(**data)

    def get_or_create_by_identificacion(self, *, identificacion: str, defaults: dict) -> tuple[Solicitante, bool]:
        return Solicitante.objects.get_or_create(
            identificacion=identificacion,
            defaults=defaults,
        )
