from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import User, UserRole
from apps.pqr.models import (
    CanalPQR,
    EstadoPQR,
    PrioridadPQR,
    TipoAccionSeguimiento,
    TipoPQR,
)
from container import get_container


class Command(BaseCommand):
    help = "Carga usuarios demo y PQRs de ejemplo."

    @transaction.atomic
    def handle(self, *args, **options):
        users = [
            ("agente@sersocial.test", "Agente Demo", UserRole.AGENTE, "Agente123!"),
            ("supervisor@sersocial.test", "Supervisor Demo", UserRole.SUPERVISOR, "Super123!"),
            ("admin@sersocial.test", "Admin Demo", UserRole.ADMIN, "Admin123!"),
        ]
        for email, nombre, rol, password in users:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={"nombre": nombre, "rol": rol},
            )
            if created:
                user.set_password(password)
                user.save()
                self.stdout.write(self.style.SUCCESS(f"Usuario creado: {email}"))
            else:
                self.stdout.write(f"Usuario ya existe: {email}")

        service = get_container().pqr_service
        if service.list_pqrs({}).exists():
            self.stdout.write("Ya hay PQRs; no se duplican ejemplos.")
            return

        samples = [
            {
                "tipo": TipoPQR.PETICION,
                "titulo": "Solicitud de certificado",
                "descripcion": "Necesito certificado de afiliación para trámite laboral.",
                "categoria": "Documentos",
                "prioridad": PrioridadPQR.MEDIA,
                "canal": CanalPQR.WEB,
                "solicitante": {
                    "nombre": "Ana",
                    "apellido": "Pérez",
                    "identificacion": "1001001001",
                    "email": "ana.perez@example.com",
                    "telefono": "3001112233",
                },
            },
            {
                "tipo": TipoPQR.QUEJA,
                "titulo": "Demora en atención",
                "descripcion": "Esperé más de 2 horas en la sede principal.",
                "categoria": "Atención",
                "prioridad": PrioridadPQR.ALTA,
                "canal": CanalPQR.PRESENCIAL,
                "solicitante": {
                    "nombre": "Carlos",
                    "apellido": "Ramírez",
                    "identificacion": "1002002002",
                    "email": "carlos.ramirez@example.com",
                    "telefono": "3102223344",
                },
            },
            {
                "tipo": TipoPQR.RECLAMO,
                "titulo": "Cobro indebido",
                "descripcion": "Se aplicó un cobro no autorizado en mi factura.",
                "categoria": "Facturación",
                "prioridad": PrioridadPQR.URGENTE,
                "canal": CanalPQR.EMAIL,
                "solicitante": {
                    "nombre": "Luisa",
                    "apellido": "Gómez",
                    "identificacion": "1003003003",
                    "email": "luisa.gomez@example.com",
                    "telefono": "3203334455",
                },
            },
        ]

        for sample in samples:
            pqr = service.create_pqr(sample)
            self.stdout.write(self.style.SUCCESS(f"PQR creada: {pqr.radicado}"))

        # Move one into gestión for richer demo data.
        agente = User.objects.get(email="agente@sersocial.test")
        first = service.list_pqrs({}).order_by("id").first()
        if first and first.estado == EstadoPQR.RECIBIDA:
            service.update_estado_prioridad(
                pqr_id=first.id,
                user=agente,
                estado=EstadoPQR.EN_GESTION,
            )
            get_container().seguimiento_service.add(
                pqr_id=first.id,
                descripcion="Caso asignado para revisión documental.",
                user=agente,
                tipo_accion=TipoAccionSeguimiento.COMENTARIO,
            )

        self.stdout.write(self.style.SUCCESS("Seed completado."))
