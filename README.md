# PQR Sersocial — Backend

API REST (Django + DRF) para gestión de PQR. Capas: views → services → repositories, con DI en `container.py` y logs con `structlog`.

## Requisitos

- Python 3.11+
- PostgreSQL 16 (vía Docker Compose o instalación local)
- Docker Desktop (opcional, recomendado)

## Variables de entorno

```bash
copy .env.example .env
```

`DATABASE_URL` apunta a PostgreSQL:

```env
DATABASE_URL=postgres://pqr:pqr@localhost:5432/pqr_db
```

## Opción A — Docker Compose (recomendado)

Levanta Postgres + API (migrate, collectstatic, seed y gunicorn):

```bash
docker compose up --build
```

- API: http://127.0.0.1:8000/api/
- Health: http://127.0.0.1:8000/api/health/
- Swagger: http://127.0.0.1:8000/api/docs/
- Postgres: `localhost:5432` (user/pass/db: `pqr` / `pqr` / `pqr_db`)

Solo base de datos (si corres Django en el host):

```bash
docker compose up -d db
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Detener:

```bash
docker compose down
```

## Opción B — Local sin contenedor API

Con Postgres accesible en `localhost:5432`:

```bash
python -m venv venv
venv\Scripts\activate
pip install -r Requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

## Credenciales demo (seed)

| Email | Password | Rol |
|-------|----------|-----|
| agente@sersocial.test | Agente123! | agente |
| supervisor@sersocial.test | Super123! | supervisor |
| admin@sersocial.test | Admin123! | admin |

Login: `POST /api/auth/login/` con `{"email":"...","password":"..."}`.

## Tests

```bash
pytest
```

## Endpoints principales

- `GET /api/health/`
- `GET/POST /api/pqr/`
- `GET /api/pqr/{id}/`
- `PATCH /api/pqr/{id}/estado/`
- `GET/POST /api/pqr/{id}/seguimiento/`
- `GET /api/pqr/buscar/?radicado=`
- `GET /api/stats/`
- `POST /api/auth/login/` · `POST /api/auth/refresh/` · `GET /api/auth/me/`
