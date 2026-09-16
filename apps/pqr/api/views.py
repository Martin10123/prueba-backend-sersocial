from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.pagination import StandardPagination
from apps.common.permissions import IsAuthenticatedAgent
from apps.pqr.api.serializers import (
    PQRCreateSerializer,
    PQRDetailSerializer,
    PQREstadoSerializer,
    PQRListSerializer,
    SeguimientoCreateSerializer,
    SeguimientoSerializer,
)
from container import get_container


class PQRListCreateView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        service = get_container().pqr_service
        filters = {
            "tipo": request.query_params.get("tipo"),
            "estado": request.query_params.get("estado"),
            "prioridad": request.query_params.get("prioridad"),
            "categoria": request.query_params.get("categoria"),
        }
        filters = {k: v for k, v in filters.items() if v}
        qs = service.list_pqrs(filters)
        paginator = StandardPagination()
        page = paginator.paginate_queryset(qs, request)
        serializer = PQRListSerializer(page, many=True, context={"request": request})
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = PQRCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pqr = get_container().pqr_service.create_pqr(serializer.validated_data.copy())
        return Response(
            PQRDetailSerializer(pqr, context={"reveal_private": True}).data,
            status=status.HTTP_201_CREATED,
        )


class PQRDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pqr_id: int):
        pqr = get_container().pqr_service.get_pqr(pqr_id)
        return Response(PQRDetailSerializer(pqr, context={"request": request}).data)


class PQREstadoView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAgent]

    def patch(self, request, pqr_id: int):
        serializer = PQREstadoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pqr = get_container().pqr_service.update_estado_prioridad(
            pqr_id=pqr_id,
            user=request.user,
            estado=serializer.validated_data.get("estado"),
            prioridad=serializer.validated_data.get("prioridad"),
        )
        return Response(PQRDetailSerializer(pqr, context={"request": request}).data)


class PQRBuscarView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        radicado = request.query_params.get("radicado", "")
        pqr = get_container().pqr_service.buscar_por_radicado(radicado)
        return Response(PQRDetailSerializer(pqr, context={"request": request}).data)


class SeguimientoListCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAgent]

    def get(self, request, pqr_id: int):
        items = get_container().seguimiento_service.list_by_pqr(pqr_id)
        return Response(SeguimientoSerializer(items, many=True).data)

    def post(self, request, pqr_id: int):
        serializer = SeguimientoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        item = get_container().seguimiento_service.add(
            pqr_id=pqr_id,
            descripcion=serializer.validated_data["descripcion"],
            tipo_accion=serializer.validated_data.get("tipo_accion"),
            user=request.user,
        )
        return Response(SeguimientoSerializer(item).data, status=status.HTTP_201_CREATED)


class StatsView(APIView):
    permission_classes = [IsAuthenticated, IsAuthenticatedAgent]

    def get(self, request):
        summary = get_container().stats_service.get_summary()
        return Response(summary)
