# Flujo del ciclo de vida de una PQR

## Actores

| Actor | Qué puede hacer |
|-------|-----------------|
| Ciudadano / colaborador | Registrar PQR, consultar por radicado (sin login) |
| Agente | Listar, filtrar, ver PII, cambiar estado (salvo cerrar), prioridad y seguimiento |
| Supervisor / Admin | Todo lo del agente + **cerrar** la PQR |

## Estados y transiciones

```mermaid
stateDiagram-v2
    [*] --> Recibida: Ciudadano registra (web)
    Recibida --> EnGestion: Agente toma el caso
    EnGestion --> Recibida: Agente devuelve a bandeja
    EnGestion --> Resuelta: Agente resuelve
    Resuelta --> EnGestion: Reabre si falta gestión
    Resuelta --> Cerrada: Solo supervisor o admin
    Cerrada --> [*]
```

Reglas en código (`ALLOWED_TRANSITIONS` + validación de rol):

- `recibida` → `en_gestion`
- `en_gestion` → `resuelta` o `recibida`
- `resuelta` → `cerrada` o `en_gestion`
- `cerrada` → ninguna (estado final)
- Pasar a `cerrada` exige rol `supervisor` o `admin`

## Secuencia resumida

```mermaid
sequenceDiagram
    actor Ciudadano
    participant API
    actor Agente
    actor Supervisor

    Ciudadano->>API: POST /api/pqr/
    API-->>Ciudadano: 201 + radicado (recibida)
    API->>Ciudadano: Email (Resend o log)

    Agente->>API: PATCH .../estado (en_gestion)
    Agente->>API: POST .../seguimiento
    Agente->>API: PATCH .../estado (resuelta)
    API->>Ciudadano: Email de actualización

    Supervisor->>API: PATCH .../estado (cerrada)
    Note over Supervisor,API: Un agente recibe 403 si intenta cerrar
```

Cada cambio de estado o prioridad deja una fila en `seguimientos`. La creación deja un evento de sistema (`tipo_accion=sistema`).
