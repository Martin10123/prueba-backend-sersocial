# Guía: tablero Kanban en Jira

La prueba pide un tablero **accesible para revisión** con columnas Por hacer / En progreso / Hecho. Jira Cloud Free no siempre permite un enlace 100 % público: lo habitual es **invitar al evaluador como Viewer** y pegar la URL del tablero en el README.

## 1. Crear el sitio

1. Entra a [https://www.atlassian.com/software/jira](https://www.atlassian.com/software/jira) y crea una cuenta (correo Gmail/institucional).
2. Elige **Jira Software** → plan **Free**.
3. Nombre del sitio: `pqr-sersocial` (queda `pqr-sersocial.atlassian.net`).
4. Si pregunta el tipo de trabajo, elige **Software development**.

## 2. Crear el proyecto Kanban

1. **Projects** → **Create project**.
2. Plantilla: **Kanban**.
3. **Project type:** Team-managed (más simple).
4. Nombre: `PQR Sersocial`.
5. Key: `PQR`.
6. Create.

## 3. Columnas del tablero

En el tablero: **...** (más) → **Board settings** / **Configure board** → **Columns**.

Deja exactamente tres columnas (renombra las que trae la plantilla):

| Columna Jira | Estado |
|--------------|--------|
| Por hacer    | To Do |
| En progreso  | In Progress |
| Hecho        | Done |

Si aparece una cuarta (p. ej. Backlog), elimínala o fusiona su estado en **Por hacer**.

## 4. Crear las tareas (copia y pega)

En el tablero: **Create**. Tipo: **Task**. Crea **una issue por fila**. Descripción breve opcional.

Cuando termines de crearlas, arrástralas **todas a Hecho** (el trabajo de esta prueba ya está hecho).

| Resumen | Descripción corta |
|---------|-------------------|
| HU: ciudadano registra PQR | Formulario web + `POST /api/pqr/` |
| HU: consultar PQR por radicado | Buscador + `GET /api/pqr/buscar/` |
| HU: listar y filtrar PQR | Filtros tipo/estado/prioridad/categoría |
| HU: cambiar estado y prioridad | Flujo Recibida → En gestión → Resuelta → Cerrada |
| HU: seguimiento interno | Comentarios de agente autenticado |
| HU: supervisor cierra PQR | Solo supervisor/admin cierran |
| HU: panel de estadísticas | Conteos por estado y tipo |
| DER y modelo SQL | Entidades Solicitante, PQR, Seguimiento, Usuario |
| Diagrama de flujo del ciclo de vida | Transiciones y actores |
| Decisiones de arquitectura | Django, PostgreSQL, capas, React |
| API REST PQR | Endpoints obligatorios del MVP |
| Autenticación JWT y roles | Agente / supervisor / admin |
| Frontend 4 pantallas | Listado, alta, detalle, estadísticas |
| Tests pytest y seed | Datos demo + colección Postman |
| Docker Compose | Postgres + API + healthcheck |
| Integración email (Resend) | Notificación al crear/cambiar estado |
| README y guía de despliegue | Ejecución local y VPS |

## 5. Dejar el tablero revisable

**Opción A (recomendada en Free):**

1. Project **Settings** → **Access** / **People**.
2. **Add people** → correo del evaluador.
3. Rol: **Viewer** (solo lectura).
4. Copia la URL del tablero. Ejemplo:

```text
https://pqr-sersocial.atlassian.net/jira/software/projects/PQR/boards/1
```

**Opción B:** si tu sitio permite **Open** / anyone with the link, actívalo en Access y usa esa misma URL.

Pega la URL en la tabla **Enlaces de entrega** del `README.md` de backend y frontend (reemplaza el texto pendiente).

## 6. Qué enviar en el correo de la prueba

- URL del repositorio backend
- URL del repositorio frontend
- URL del tablero Jira
- Correo con el que invitaste al evaluador (si usaste la opción A)
- Credenciales demo del seed
