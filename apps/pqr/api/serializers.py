from rest_framework import serializers

from apps.common.privacy import (
    mask_email,
    mask_identifier,
    mask_phone,
    request_is_agent,
)
from apps.pqr.models import (
    CanalPQR,
    EstadoPQR,
    PrioridadPQR,
    PQR,
    Seguimiento,
    Solicitante,
    TipoAccionSeguimiento,
    TipoPQR,
)


class SolicitanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Solicitante
        fields = (
            "id",
            "nombre",
            "apellido",
            "identificacion",
            "email",
            "telefono",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class SolicitanteInputSerializer(serializers.Serializer):
    nombre = serializers.CharField(max_length=120)
    apellido = serializers.CharField(max_length=120)
    identificacion = serializers.CharField(max_length=50)
    email = serializers.EmailField()
    telefono = serializers.CharField(max_length=30, required=False, allow_blank=True, default="")


class SeguimientoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source="usuario.nombre", read_only=True, default=None)

    class Meta:
        model = Seguimiento
        fields = (
            "id",
            "descripcion",
            "tipo_accion",
            "fecha_registro",
            "usuario_id",
            "usuario_nombre",
        )
        read_only_fields = fields


class SeguimientoCreateSerializer(serializers.Serializer):
    descripcion = serializers.CharField()
    tipo_accion = serializers.ChoiceField(
        choices=TipoAccionSeguimiento.choices,
        required=False,
        default=TipoAccionSeguimiento.COMENTARIO,
    )


class PQRListSerializer(serializers.ModelSerializer):
    solicitante_nombre = serializers.SerializerMethodField()

    class Meta:
        model = PQR
        fields = (
            "id",
            "radicado",
            "tipo",
            "titulo",
            "categoria",
            "prioridad",
            "estado",
            "canal",
            "solicitante_id",
            "solicitante_nombre",
            "created_at",
            "updated_at",
        )

    def get_solicitante_nombre(self, obj: PQR) -> str:
        if _reveal_private(self.context):
            return f"{obj.solicitante.nombre} {obj.solicitante.apellido}"
        return obj.solicitante.nombre


def _reveal_private(context: dict) -> bool:
    if context.get("reveal_private"):
        return True
    return request_is_agent(context.get("request"))


class PQRDetailSerializer(serializers.ModelSerializer):
    solicitante = serializers.SerializerMethodField()
    seguimientos = serializers.SerializerMethodField()

    class Meta:
        model = PQR
        fields = (
            "id",
            "radicado",
            "tipo",
            "titulo",
            "descripcion",
            "categoria",
            "prioridad",
            "estado",
            "canal",
            "solicitante",
            "seguimientos",
            "created_at",
            "updated_at",
        )

    def get_solicitante(self, obj: PQR) -> dict:
        data = SolicitanteSerializer(obj.solicitante).data
        if _reveal_private(self.context):
            return data
        apellido = data.get("apellido") or ""
        return {
            **data,
            "apellido": f"{apellido[:1]}." if apellido else "",
            "identificacion": mask_identifier(data.get("identificacion", "")),
            "email": mask_email(data.get("email", "")),
            "telefono": mask_phone(data.get("telefono") or ""),
        }

    def get_seguimientos(self, obj: PQR) -> list:
        if not _reveal_private(self.context):
            return []
        return SeguimientoSerializer(obj.seguimientos.all(), many=True).data


class PQRCreateSerializer(serializers.Serializer):
    tipo = serializers.ChoiceField(choices=TipoPQR.choices)
    titulo = serializers.CharField(max_length=200)
    descripcion = serializers.CharField()
    categoria = serializers.CharField(max_length=100)
    prioridad = serializers.ChoiceField(
        choices=PrioridadPQR.choices,
        required=False,
        default=PrioridadPQR.MEDIA,
    )
    canal = serializers.ChoiceField(
        choices=CanalPQR.choices,
        required=False,
        default=CanalPQR.WEB,
    )
    solicitante = SolicitanteInputSerializer()


class PQREstadoSerializer(serializers.Serializer):
    estado = serializers.ChoiceField(choices=EstadoPQR.choices, required=False)
    prioridad = serializers.ChoiceField(choices=PrioridadPQR.choices, required=False)

    def validate(self, attrs):
        if not attrs.get("estado") and not attrs.get("prioridad"):
            raise serializers.ValidationError("Debe enviar estado y/o prioridad.")
        return attrs
