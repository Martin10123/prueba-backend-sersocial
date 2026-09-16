# PQR Sersocial — Backend

API REST (Django + DRF) para gestión de PQR de la Fundación Sersocial IPS. Capas: views → services → repositories, con inyección de dependencias en `container.py`.

Frontend (repo aparte): [frontend-prueba-sersocial](https://github.com/Martin10123/frontend-prueba-sersocial).

## Enlaces de entrega

Completa la fila del tablero cuando tengas la URL de Jira (`docs/jira.md`).

| Recurso | URL |
|---------|-----|
| Backend | https://github.com/Martin10123/prueba-backend-sersocial |
| Frontend | https://github.com/Martin10123/frontend-prueba-sersocial |
| Tablero Kanban (Jira) | https://martinsworkspace-45833364.atlassian.net/jira/software/projects/KAN/boards/1 |
| Historias de usuario | [docs/historias-de-usuario.md](docs/historias-de-usuario.md) |
| DER | [docs/der.md](docs/der.md) |
| Flujo del ciclo de vida | [docs/flujo-pqr.md](docs/flujo-pqr.md) |
| Decisiones de arquitectura | [docs/arquitectura.md](docs/arquitectura.md) |
| Guía para crear el Kanban | [docs/jira.md](docs/jira.md) |
| Guía de despliegue | [docs/despliegue.md](docs/despliegue.md) |
| Colección Postman | [docs/api/PQR_Sersocial.postman_collection.json](docs/api/PQR_Sersocial.postman_collection.json) |
| Swagger local | http://127.0.0.1:8000/api/docs/ |

## Uso de IA

Se utilizó **Cursor** como asistente de desarrollo (autocompletado, scaffolding de capas Django/DRF, Docker, tests, documentación de análisis y README).

Alcance: apoyo en código, estructura del proyecto y redacción de artefactos. Las reglas de negocio (transiciones, roles, PII, seed) y la revisión de que el MVP cumpla la prueba las validó el candidato ejecutando la API, el frontend y `pytest`.

No se usó IA para el tablero Jira: ese tablero se crea a mano con la guía de `docs/jira.md`.

## Decisiones de arquitectura (resumen)

- **Django + DRF** y **PostgreSQL 16**: stack deseable de la prueba, migraciones e integridad referencial.
- **Capas** views → services → repositories; composition root en `container.py`.
- **React + Vite** en repo separado para las 4 pantallas del MVP.
- **JWT** para agentes; el ciudadano registra y consulta sin login.
- Detalle en [docs/arquitectura.md](docs/arquitectura.md) (1 página).

## Requisitos

- Python **3.12** (3.11+ compatible)
- PostgreSQL **16** (Docker Compose o instalación local)
- Docker Desktop (recomendado)
- Dependencias: ver `Requirements.txt` (Django 5, DRF, SimpleJWT, gunicorn, pytest, ruff, black)

## Variables de entorno

```bash
cp .env.example .env
```

En Windows: `copy .env.example .env`.

`DATABASE_URL` para Postgres en el host:

```env
DATABASE_URL=postgres://pqr:pqr@localhost:5432/pqr_db
```

Dentro de Compose el host de la base es `db`, no `localhost` (ya va en `docker-compose.yml`).

## Opción A — Docker Compose (recomendado, ~5 min)

Levanta Postgres + API (migrate, collectstatic, seed y Gunicorn):

```bash
docker compose up --build
```

- API: http://127.0.0.1:8000/api/
- Health: http://127.0.0.1:8000/api/health/
- Swagger: http://127.0.0.1:8000/api/docs/
- Postgres: `localhost:5432` (user/pass/db: `pqr` / `pqr` / `pqr_db`)

Solo base de datos (Django en el host):

```bash
docker compose up -d db
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Detener: `docker compose down`.

## Opción B — Local sin contenedor API

Con Postgres en `localhost:5432`:

```bash
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/macOS: source venv/bin/activate
pip install -r Requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Frontend (segundo terminal)

```bash
git clone https://github.com/Martin10123/frontend-prueba-sersocial.git
cd frontend-prueba-sersocial
pnpm install
cp .env.example .env
pnpm dev
```

App: http://127.0.0.1:5173 — `VITE_API_URL=http://127.0.0.1:8000`.

## Credenciales demo (seed)

| Email | Password | Rol |
|-------|----------|-----|
| agente@sersocial.test | Agente123! | agente |
| supervisor@sersocial.test | Super123! | supervisor |
| admin@sersocial.test | Admin123! | admin |

Login: `POST /api/auth/login/` con `{"email":"...","password":"..."}`. Solo supervisor/admin pueden **cerrar** una PQR.

## Tests y lint

```bash
pytest
ruff check .
black --check .
```

## Endpoints principales

- `GET /api/health/`
- `GET/POST /api/pqr/` (listado paginado: `page`, `page_size`)
- `GET /api/pqr/{id}/`
- `PATCH /api/pqr/{id}/estado/`
- `GET/POST /api/pqr/{id}/seguimiento/`
- `GET /api/pqr/buscar/?radicado=`
- `GET /api/stats/`
- `POST /api/auth/login/` · `POST /api/auth/refresh/` · `GET /api/auth/me/`

Django usa **barra final**. Notificaciones: con `EMAIL_API_KEY` se llama a Resend; si va vacío, solo se registra en log.
