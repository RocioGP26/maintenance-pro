# Sprint 19 · Contratos de estados, permisos y eventos

## 1 · Estados

### Versión de procedimiento

| Estado | Transiciones permitidas |
|---|---|
| `draft` | editar, publicar, eliminar si nunca fue usada |
| `published` | retirar; no editar ni eliminar |
| `retired` | consultar y reutilizar únicamente en OT históricas |

### Checklist de OT

| Estado | Significado |
|---|---|
| `pending` | creado, sin ejecución iniciada |
| `in_progress` | existe al menos una respuesta válida |
| `blocked` | no conformidad o dependencia impide continuar |
| `completed` | pasos obligatorios y evidencias válidos |
| `reviewed` | supervisor validó la ejecución |
| `void` | anulado con motivo y auditoría; nunca eliminado |

Transiciones:

```text
pending → in_progress ↔ blocked → completed → reviewed
   └──────────────────────────────────────────────→ void
```

### Conformidad de paso

`conforming` · `nonconforming` · `not_applicable` · `pending_review`

## 2 · Capacidades

| Capacidad | Propósito |
|---|---|
| `maintenance.procedures.view` | Consultar procedimientos publicados |
| `maintenance.procedures.manage` | Crear borradores y editar pasos |
| `maintenance.procedures.publish` | Publicar o retirar versiones |
| `maintenance.checklists.view` | Consultar ejecución relacionada |
| `maintenance.checklists.execute` | Responder checklist propio/asignado |
| `maintenance.checklists.record_for_technician` | Registrar en nombre del ejecutor identificado |
| `maintenance.checklists.review` | Revisar no conformidades y ejecución completa |
| `maintenance.log.view_internal` | Consultar entradas internas |
| `maintenance.log.write` | Crear entradas y adjuntos permitidos |
| `maintenance.log.publish_requester` | Hacer una entrada visible al reportante |
| `maintenance.meters.view` | Consultar medidores y lecturas |
| `maintenance.meters.manage` | Crear, configurar o desactivar medidores |
| `maintenance.meters.record` | Registrar lecturas propias |
| `maintenance.meters.record_for_technician` | Registrar lectura delegada |

## 3 · Matriz de rol inicial

| Acción | Técnico | Supervisor/Jefe | Admin tenant | Solicitante |
|---|:---:|:---:|:---:|:---:|
| Ver procedimiento publicado relacionado | ✅ | ✅ | ✅ | — |
| Crear/editar borrador | — | ✅ | ✅ | — |
| Publicar/retirar versión | — | ✅ | ✅ | — |
| Ejecutar checklist asignado | ✅ | ✅ | ✅ | — |
| Registrar por otro técnico | — | ✅ | ✅ | — |
| Revisar y aprobar ejecución | — | ✅ | ✅ | — |
| Escribir bitácora interna | ✅ | ✅ | ✅ | — |
| Publicar al reportante | — | ✅ | ✅ | — |
| Ver entrada marcada para reportante | — | ✅ | ✅ | ✅ propia |
| Registrar lectura | ✅ asignado | ✅ | ✅ | — |
| Configurar medidor | — | ✅ | ✅ | — |

El rol no sustituye la relación con la entidad: un técnico solo accede a OT,
incidencias y activos permitidos por las reglas operativas existentes.

## 4 · Contrato de autoría

En comandos delegables, el backend recibe `performed_by_user_id`; el
`recorded_by_user_id` siempre se obtiene de `current_user` y nunca del formulario.

Validaciones:

- ambos usuarios pertenecen al tenant;
- el ejecutor está activo y tiene relación operativa válida;
- el registrador posee la capacidad delegada cuando los IDs son diferentes;
- la auditoría describe “registrado por X en nombre de Y”.

## 5 · Eventos de dominio

Sprint 19 emite eventos auditables, pero no ejecuta reglas automáticas:

| Evento | Momento |
|---|---|
| `maintenance.procedure.published` | se publica una versión |
| `maintenance.checklist.started` | primera respuesta válida |
| `maintenance.checklist.blocked` | aparece una no conformidad bloqueante |
| `maintenance.checklist.completed` | se cumplen requisitos de ejecución |
| `maintenance.checklist.reviewed` | supervisor valida |
| `maintenance.log.entry_created` | se agrega contexto humano |
| `maintenance.meter.reading_created` | se registra una lectura |
| `maintenance.meter.reading_flagged` | lectura viola secuencia o rango y queda justificada |

Payload mínimo común:

```json
{
  "event_id": "uuid",
  "event_type": "maintenance.checklist.completed",
  "occurred_at": "2026-07-21T14:00:00Z",
  "empresa_id": 17,
  "actor_id": 81,
  "entity_type": "work_order_checklist",
  "entity_id": 552,
  "correlation_id": "uuid",
  "schema_version": 1
}
```

## 6 · Auditoría mínima

Registrar:

- creación, edición de borrador, publicación y retiro de procedimiento;
- inicio, bloqueo, finalización, revisión y anulación de checklist;
- creación y corrección de respuesta;
- ejecutor y registrador de cada respuesta o lectura;
- entrada de bitácora, visibilidad y adjuntos;
- creación, cambio permitido y desactivación de medidor;
- lectura aceptada, rechazada, corregida o marcada;
- descarga o acceso a evidencia sensible cuando aplique.

## 7 · Contrato UI inicial

```text
Administración → Mantenimiento → Procedimientos
OT → pestaña Ejecución → Checklist
OT / Incidencia / Activo → pestaña Bitácora
Activo → pestaña Medidores y lecturas
```

La pantalla de checklist debe mostrar progreso, pasos pendientes, autoría y no
conformidades sin obligar a abrir modales encadenados. En móvil se prioriza la
ejecución de un paso a la vez y la carga de evidencia.

## 8 · Contrato API futuro

Las rutas conceptuales reservadas son:

- `/api/v1/maintenance/procedures`
- `/api/v1/maintenance/work-orders/{id}/checklist`
- `/api/v1/maintenance/log-entries`
- `/api/v1/maintenance/assets/{id}/meters`
- `/api/v1/maintenance/meters/{id}/readings`

Sprint 19 implementa primero servicios internos y UI. Exponer escritura pública,
scopes, rate limits y webhooks pertenece a Sprint 22.

