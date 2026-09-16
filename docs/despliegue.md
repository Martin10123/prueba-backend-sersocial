# Guía de despliegue

No es obligatorio un despliegue real. Este procedimiento es reproducible en un VPS Ubuntu 22.04+ o en Render.

En producción: `DEBUG=False`, `RUN_SEED=False`, `SECRET_KEY` propio y Postgres con volumen persistente.

## A. VPS — Docker Compose + Nginx (recomendado)

El `Dockerfile` ya arranca **Gunicorn**. Nginx queda como reverse proxy (API + frontend estático) y TLS.

### 1. Servidor

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2 nginx certbot python3-certbot-nginx
sudo usermod -aG docker $USER
# cierra sesión y vuelve a entrar
```

### 2. Clonar backend

```bash
sudo mkdir -p /opt/pqr && sudo chown $USER:$USER /opt/pqr
cd /opt/pqr
git clone https://github.com/Martin10123/prueba-backend-sersocial.git backend
cd backend
cp .env.example .env
nano .env
```

Ajusta como mínimo:

```env
DEBUG=False
SECRET_KEY=genera-una-clave-larga
ALLOWED_HOSTS=api.tudominio.com,127.0.0.1
DATABASE_URL=postgres://pqr:CLAVE_FUERTE@db:5432/pqr_db
POSTGRES_PASSWORD=CLAVE_FUERTE
CORS_ALLOWED_ORIGINS=https://tudominio.com
RUN_SEED=False
NOTIFICATIONS_ENABLED=True
EMAIL_API_KEY=re_xxxxx
```

El `docker-compose.yml` usa el servicio `db` como host de Postgres. No uses `localhost` dentro del contenedor `api`.

### 3. Levantar API + Postgres

```bash
docker compose up -d --build
curl -f http://127.0.0.1:8000/api/health/
```

### 4. Frontend (build estático)

En el mismo VPS o en tu PC (y luego subes `dist/`):

```bash
git clone https://github.com/Martin10123/frontend-prueba-sersocial.git frontend
cd frontend
# Node 20+
corepack enable
pnpm install
echo "VITE_API_URL=https://api.tudominio.com" > .env.production
pnpm build
sudo mkdir -p /var/www/pqr
sudo cp -r dist/* /var/www/pqr/
```

`VITE_API_URL` es la URL pública del backend **sin** barra final. El cliente llama a `${VITE_API_URL}/api/...`.

### 5. Nginx

`/etc/nginx/sites-available/pqr`:

```nginx
server {
    listen 80;
    server_name tudominio.com;

    root /var/www/pqr;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}

server {
    listen 80;
    server_name api.tudominio.com;

    client_max_body_size 10m;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/pqr /etc/nginx/sites-enabled/pqr
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d tudominio.com -d api.tudominio.com
```

DNS: `A` de `tudominio.com` y `api.tudominio.com` al IP del VPS. Abre puertos 80 y 443. El compose publica la API en `8000` solo en localhost si cambias el bind; en el archivo actual está `8000:8000` (útil para pruebas). En un VPS endurecido puedes mapear `127.0.0.1:8000:8000`.

### 6. Actualizar

```bash
cd /opt/pqr/backend
git pull
docker compose up -d --build
# migraciones las corre el entrypoint
```

## B. VPS sin Docker (Gunicorn + Nginx + Postgres)

```bash
sudo apt install -y python3.12-venv python3-pip postgresql nginx
sudo -u postgres createuser pqr
sudo -u postgres createdb pqr_db -O pqr
```

```bash
git clone https://github.com/Martin10123/prueba-backend-sersocial.git
cd prueba-backend-sersocial
python3 -m venv venv
source venv/bin/activate
pip install -r Requirements.txt
cp .env.example .env
# DATABASE_URL=postgres://pqr:CLAVE@127.0.0.1:5432/pqr_db
python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

Unit systemd `/etc/systemd/system/pqr-api.service`:

```ini
[Unit]
Description=PQR Sersocial API
After=network.target postgresql.service

[Service]
User=www-data
WorkingDirectory=/opt/pqr/backend
EnvironmentFile=/opt/pqr/backend/.env
ExecStart=/opt/pqr/backend/venv/bin/gunicorn config.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 60
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now pqr-api
```

Nginx igual que en la sección A (`proxy_pass http://127.0.0.1:8000`).

## C. Render / Railway (alternativa)

1. Crea un Postgres gestionado y copia la `DATABASE_URL`.
2. Web Service desde el repo backend, runtime Docker (`Dockerfile`).
3. Variables: `SECRET_KEY`, `DEBUG=False`, `ALLOWED_HOSTS` (hostname de Render), `DATABASE_URL`, `CORS_ALLOWED_ORIGINS`, `RUN_SEED=False`.
4. Health check: `/api/health/`.
5. Frontend: Static Site en Render con `pnpm build` y `VITE_API_URL` apuntando al servicio API.

## Comprobación

- `GET https://api.tudominio.com/api/health/` → 200
- `GET https://api.tudominio.com/api/docs/` → Swagger
- Login demo (solo si dejaste seed en un ambiente de prueba, **nunca en producción**)
