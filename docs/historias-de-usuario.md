# Historias de usuario — PQR Sersocial

Criterio de aceptación alineado al MVP de la prueba.

## HU-01 — Registrar una PQR

**Como** ciudadano o colaborador  
**quiero** registrar una solicitud con tipo, categoría, datos de contacto, descripción y prioridad  
**para** dejar constancia formal de una petición, queja o reclamo.

**Criterios**

- El formulario valida campos obligatorios en el cliente y el API rechaza payloads inválidos.
- Se genera un número de radicado único (`PQR-YYYYMMDD-####`).
- El estado inicial es `recibida`.
- Si el solicitante ya existe (misma identificación), se reutiliza el registro.

## HU-02 — Consultar por radicado

**Como** ciudadano  
**quiero** buscar mi PQR por número de radicado  
**para** conocer su estado sin necesidad de login.

**Criterios**

- `GET /api/pqr/buscar/?radicado=` devuelve el detalle o 404.
- En vista pública se enmascaran identificación, email y teléfono.

## HU-03 — Listar y filtrar PQR

**Como** agente interno  
**quiero** ver el listado y filtrar por tipo, estado, prioridad y categoría  
**para** priorizar la cola de trabajo.

**Criterios**

- `GET /api/pqr/` acepta query params `tipo`, `estado`, `prioridad`, `categoria`, `page` y `page_size`.
- El listado de la pantalla de inicio consume esos filtros.

## HU-04 — Ver detalle e historial

**Como** agente  
**quiero** abrir una PQR y ver datos del caso, del solicitante y el historial de seguimiento  
**para** decidir el siguiente paso.

**Criterios**

- `GET /api/pqr/{id}/` incluye solicitante.
- El historial interno (`seguimientos`) solo se revela a usuarios autenticados con rol de agente o superior.

## HU-05 — Cambiar estado y prioridad

**Como** agente  
**quiero** actualizar estado y/o prioridad respetando el flujo  
**para** gestionar el ciclo de vida del caso.

**Criterios**

- Flujo: Recibida → En gestión → Resuelta → Cerrada.
- Transiciones inválidas responden 400 (`invalid_transition`).
- Cada cambio queda registrado como seguimiento.

## HU-06 — Agregar seguimiento interno

**Como** agente  
**quiero** dejar comentarios internos en una PQR  
**para** documentar gestiones, llamadas o evidencias.

**Criterios**

- `POST /api/pqr/{id}/seguimiento/` requiere JWT.
- La entrada guarda descripción, tipo de acción, fecha y usuario.

## HU-07 — Cerrar PQR (supervisor / admin)

**Como** supervisor o administrador  
**quiero** ser el único rol que puede pasar una PQR a `cerrada`  
**para** controlar el cierre formal del caso.

**Criterios**

- Un agente que intente cerrar recibe 403.
- Supervisor y admin pueden cerrar desde `resuelta`.

## HU-08 — Ver estadísticas

**Como** agente o supervisor  
**quiero** ver cantidades de PQR por estado y por tipo  
**para** tener una lectura rápida de la operación.

**Criterios**

- `GET /api/stats/` requiere autenticación.
- La pantalla `/estadisticas` muestra conteos o gráficos.
