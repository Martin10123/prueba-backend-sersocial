import django_filters

from apps.pqr.models import PQR


class PQRFilter(django_filters.FilterSet):
    tipo = django_filters.CharFilter(field_name="tipo")
    estado = django_filters.CharFilter(field_name="estado")
    prioridad = django_filters.CharFilter(field_name="prioridad")
    categoria = django_filters.CharFilter(field_name="categoria", lookup_expr="iexact")

    class Meta:
        model = PQR
        fields = ("tipo", "estado", "prioridad", "categoria")
