# Decisiones de arquitectura

Sistema PQR en dos repositorios: API Django y SPA React. Objetivo: un MVP claro, reproducible en local y alineado a la prueba (capas, SQL, JWT, Docker).

## Backend: Django 5 + DRF

Se eligió **Django + Django REST Framework** (opción deseable de la prueba) porque el dominio es CRUD con reglas de negocio (transiciones de estado, roles, PII) y Django cubre ORM, migraciones, admin y autenticación sin ensamblar piezas a mano. FastAPI habría servido para la API, pero habría que armar persistencia y admin aparte en el mismo plazo.

Python **3.12** (compatible con el requisito 3.11+). Servidor de aplicación: **Gunicorn** + **WhiteNoise** para estáticos.

## Persistencia: PostgreSQL 16

**PostgreSQL** es el motor de referencia (SQL relacional pedido). Las relaciones PQR–solicitante–seguimiento necesitan integridad referencial (`PROTECT` / `CASCADE` / `SET NULL`). SQLite queda como fallback si no hay `DATABASE_URL`, pero Docker Compose levanta Postgres. Acceso vía `DATABASE_URL` (`django-environ` + `psycopg2`).

## Estructura de capas

```
views (API) → services → repositories → modelos Django
```

- **Views:** HTTP, permisos, serialización.
- **Services:** reglas (radicado, transiciones, notificaciones).
- **Repositories:** queries.
- **`container.py`:** composition root; inyección por constructor. Las vistas piden servicios con `get_container()`.

Auth de agentes: **JWT** (SimpleJWT). El ciudadano no inicia sesión para crear o consultar por radicado.

## Frontend: React + Vite + TypeScript

SPA (opción deseable). Consume la API con Axios. Rutas: listado, alta, detalle, estadísticas. Validación de alta con Zod. Login de agentes en modal. Estadísticas y gestiones internas exigen JWT.

## Integración externa

Puerto `NotificationPort`: si hay `EMAIL_API_KEY` se llama a **Resend**; si no, se registra el envío en logs. No bloquea el flujo PQR si el correo falla.

## Qué se descartó

- Monolito con plantillas Django: la prueba valora React y un API REST explícito.
- ORM directo en las vistas: dificulta tests y el cierre de transiciones.
- Kubernetes / CI: fuera del MVP; Docker Compose cubre el bonus de entorno único.
