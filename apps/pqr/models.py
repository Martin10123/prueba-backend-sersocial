from django.conf import settings
from django.db import models


class TipoPQR(models.TextChoices):
    PETICION = "peticion", "Petición"
    QUEJA = "queja", "Queja"
    RECLAMO = "reclamo", "Reclamo"


class PrioridadPQR(models.TextChoices):
    BAJA = "baja", "Baja"
    MEDIA = "media", "Media"
    ALTA = "alta", "Alta"
    URGENTE = "urgente", "Urgente"


class EstadoPQR(models.TextChoices):
    RECIBIDA = "recibida", "Recibida"
    EN_GESTION = "en_gestion", "En gestión"
    RESUELTA = "resuelta", "Resuelta"
    CERRADA = "cerrada", "Cerrada"


class CanalPQR(models.TextChoices):
    WEB = "web", "Web"
    EMAIL = "email", "Email"
    PRESENCIAL = "presencial", "Presencial"


class TipoAccionSeguimiento(models.TextChoices):
    COMENTARIO = "comentario", "Comentario"
    CAMBIO_ESTADO = "cambio_estado", "Cambio de estado"
    CAMBIO_PRIORIDAD = "cambio_prioridad", "Cambio de prioridad"
    ASIGNACION = "asignacion", "Asignación"
    SISTEMA = "sistema", "Sistema"


ALLOWED_TRANSITIONS: dict[str, set[str]] = {
    EstadoPQR.RECIBIDA: {EstadoPQR.EN_GESTION},
    EstadoPQR.EN_GESTION: {EstadoPQR.RESUELTA, EstadoPQR.RECIBIDA},
    EstadoPQR.RESUELTA: {EstadoPQR.CERRADA, EstadoPQR.EN_GESTION},
    EstadoPQR.CERRADA: set(),
}


class Solicitante(models.Model):
    nombre = models.CharField(max_length=120)
    apellido = models.CharField(max_length=120)
    identificacion = models.CharField(max_length=50, unique=True, db_index=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=30, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "solicitantes"
        ordering = ["apellido", "nombre"]

    def __str__(self) -> str:
        return f"{self.nombre} {self.apellido} ({self.identificacion})"


class PQR(models.Model):
    radicado = models.CharField(max_length=32, unique=True, db_index=True)
    tipo = models.CharField(max_length=20, choices=TipoPQR.choices)
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    categoria = models.CharField(max_length=100, db_index=True)
    prioridad = models.CharField(
        max_length=20,
        choices=PrioridadPQR.choices,
        default=PrioridadPQR.MEDIA,
        db_index=True,
    )
    estado = models.CharField(
        max_length=20,
        choices=EstadoPQR.choices,
        default=EstadoPQR.RECIBIDA,
        db_index=True,
    )
    canal = models.CharField(
        max_length=20,
        choices=CanalPQR.choices,
        default=CanalPQR.WEB,
    )
    solicitante = models.ForeignKey(
        Solicitante,
        on_delete=models.PROTECT,
        related_name="pqrs",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "pqrs"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["tipo", "estado"]),
            models.Index(fields=["prioridad", "estado"]),
            models.Index(fields=["categoria", "estado"]),
        ]

    def __str__(self) -> str:
        return f"{self.radicado} — {self.titulo}"


class Seguimiento(models.Model):
    pqr = models.ForeignKey(PQR, on_delete=models.CASCADE, related_name="seguimientos")
    descripcion = models.TextField()
    tipo_accion = models.CharField(
        max_length=30,
        choices=TipoAccionSeguimiento.choices,
        default=TipoAccionSeguimiento.COMENTARIO,
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seguimientos",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "seguimientos"
        ordering = ["fecha_registro"]

    def __str__(self) -> str:
        return f"{self.pqr_id} · {self.tipo_accion}"
