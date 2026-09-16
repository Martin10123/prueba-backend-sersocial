import pytest
from rest_framework.test import APIClient

from apps.accounts.models import User, UserRole
from apps.pqr.models import EstadoPQR, PrioridadPQR, TipoPQR


@pytest.fixture
def api():
    return APIClient()


@pytest.fixture
def agente(db):
    user = User.objects.create_user(
        email="agente@test.com",
        password="Agente123!",
        nombre="Agente Test",
        rol=UserRole.AGENTE,
    )
    return user


def _payload(**overrides):
    data = {
        "tipo": TipoPQR.PETICION,
        "titulo": "Prueba PQR",
        "descripcion": "Descripción de prueba",
        "categoria": "General",
        "prioridad": PrioridadPQR.MEDIA,
        "canal": "web",
        "solicitante": {
            "nombre": "Juan",
            "apellido": "Lopez",
            "identificacion": "999888777",
            "email": "juan@example.com",
            "telefono": "3000000000",
        },
    }
    data.update(overrides)
    return data


@pytest.mark.django_db
def test_crear_pqr(api):
    response = api.post("/api/pqr/", _payload(), format="json")
    assert response.status_code == 201
    body = response.json()
    assert body["radicado"].startswith("PQR-")
    assert body["estado"] == EstadoPQR.RECIBIDA
    assert body["solicitante"]["identificacion"] == "999888777"


@pytest.mark.django_db
def test_transicion_invalida(api, agente):
    created = api.post("/api/pqr/", _payload(solicitante={
        "nombre": "A",
        "apellido": "B",
        "identificacion": "111222333",
        "email": "a@example.com",
        "telefono": "",
    }), format="json")
    pqr_id = created.json()["id"]

    api.force_authenticate(user=agente)
    response = api.patch(
        f"/api/pqr/{pqr_id}/estado/",
        {"estado": EstadoPQR.CERRADA},
        format="json",
    )
    assert response.status_code == 400
    assert response.json()["code"] == "invalid_transition"


@pytest.mark.django_db
def test_buscar_por_radicado(api):
    created = api.post("/api/pqr/", _payload(solicitante={
        "nombre": "C",
        "apellido": "D",
        "identificacion": "444555666",
        "email": "c@example.com",
        "telefono": "",
    }), format="json")
    radicado = created.json()["radicado"]

    response = api.get("/api/pqr/buscar/", {"radicado": radicado})
    assert response.status_code == 200
    body = response.json()
    assert body["radicado"] == radicado
    assert body["solicitante"]["identificacion"] != "444555666"
    assert body["solicitante"]["identificacion"].endswith("5666")
    assert body["seguimientos"] == []


@pytest.mark.django_db
def test_detalle_publico_enmascara_pii(api):
    created = api.post("/api/pqr/", _payload(), format="json")
    pqr_id = created.json()["id"]

    public = api.get(f"/api/pqr/{pqr_id}/")
    assert public.status_code == 200
    body = public.json()
    assert body["solicitante"]["identificacion"] != "999888777"
    assert body["solicitante"]["email"] != "juan@example.com"
    assert body["seguimientos"] == []


@pytest.mark.django_db
def test_detalle_agente_ve_pii_y_seguimientos(api, agente):
    created = api.post("/api/pqr/", _payload(), format="json")
    pqr_id = created.json()["id"]

    api.force_authenticate(user=agente)
    private = api.get(f"/api/pqr/{pqr_id}/")
    assert private.status_code == 200
    body = private.json()
    assert body["solicitante"]["identificacion"] == "999888777"
    assert body["solicitante"]["email"] == "juan@example.com"
    assert len(body["seguimientos"]) >= 1


@pytest.mark.django_db
def test_filtro_categoria_parcial(api):
    api.post("/api/pqr/", _payload(), format="json")
    response = api.get("/api/pqr/", {"categoria": "gene"})
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert len(body["results"]) == 1
    assert body["results"][0]["solicitante_nombre"] == "Juan"


@pytest.mark.django_db
def test_listado_paginado(api):
    for i in range(3):
        api.post(
            "/api/pqr/",
            _payload(
                titulo=f"PQR {i}",
                solicitante={
                    "nombre": "N",
                    "apellido": "A",
                    "identificacion": f"70070070{i}",
                    "email": f"n{i}@example.com",
                    "telefono": "",
                },
            ),
            format="json",
        )
    page1 = api.get("/api/pqr/", {"page": 1, "page_size": 2})
    assert page1.status_code == 200
    body = page1.json()
    assert body["count"] == 3
    assert len(body["results"]) == 2
    assert body["next"] is not None
    page2 = api.get("/api/pqr/", {"page": 2, "page_size": 2})
    assert page2.status_code == 200
    assert len(page2.json()["results"]) == 1


@pytest.mark.django_db
def test_seguimiento_requiere_agente(api):
    created = api.post("/api/pqr/", _payload(), format="json")
    pqr_id = created.json()["id"]
    response = api.get(f"/api/pqr/{pqr_id}/seguimiento/")
    assert response.status_code in (401, 403)
