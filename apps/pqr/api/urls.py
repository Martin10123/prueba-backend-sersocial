from django.urls import path

from apps.pqr.api.views import (
    PQRBuscarView,
    PQRDetailView,
    PQREstadoView,
    PQRListCreateView,
    SeguimientoListCreateView,
    StatsView,
)

urlpatterns = [
    path("pqr/buscar/", PQRBuscarView.as_view(), name="pqr-buscar"),
    path("pqr/", PQRListCreateView.as_view(), name="pqr-list-create"),
    path("pqr/<int:pqr_id>/", PQRDetailView.as_view(), name="pqr-detail"),
    path("pqr/<int:pqr_id>/estado/", PQREstadoView.as_view(), name="pqr-estado"),
    path(
        "pqr/<int:pqr_id>/seguimiento/",
        SeguimientoListCreateView.as_view(),
        name="pqr-seguimiento",
    ),
    path("stats/", StatsView.as_view(), name="stats"),
]
