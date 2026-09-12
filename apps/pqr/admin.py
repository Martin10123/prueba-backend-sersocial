from django.contrib import admin

from apps.pqr.models import PQR, Seguimiento, Solicitante


@admin.register(Solicitante)
class SolicitanteAdmin(admin.ModelAdmin):
    list_display = ("identificacion", "nombre", "apellido", "email", "created_at")
    search_fields = ("identificacion", "nombre", "apellido", "email")


class SeguimientoInline(admin.TabularInline):
    model = Seguimiento
    extra = 0
    readonly_fields = ("fecha_registro",)


@admin.register(PQR)
class PQRAdmin(admin.ModelAdmin):
    list_display = (
        "radicado",
        "tipo",
        "titulo",
        "estado",
        "prioridad",
        "categoria",
        "created_at",
    )
    list_filter = ("tipo", "estado", "prioridad", "categoria", "canal")
    search_fields = ("radicado", "titulo", "solicitante__identificacion")
    inlines = [SeguimientoInline]
    raw_id_fields = ("solicitante",)


@admin.register(Seguimiento)
class SeguimientoAdmin(admin.ModelAdmin):
    list_display = ("pqr", "tipo_accion", "usuario", "fecha_registro")
    list_filter = ("tipo_accion",)
    raw_id_fields = ("pqr", "usuario")
