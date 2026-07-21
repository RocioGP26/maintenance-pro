# Sprint 19 · Arquitectura de ejecución de mantenimiento

## 1 · Ownership

```text
Maintenance masters                 Maintenance Execution
Machine ──────────────────────────► AssetMeter ──► MeterReading
WorkOrder ────────────────────────► WorkOrderChecklist
Incident ───────────────┐                    │
Machine ────────────────┼────────► MaintenanceLogEntry
WorkOrder ──────────────┘                    │
User ─────────► performed_by / recorded_by  └──► MaintenanceLogAttachment
```

Maintenance conserva la propiedad de activos, OT e incidencias. La nueva
capacidad solo registra cómo se ejecutó, qué contexto se agregó y qué valores se
midieron. No duplica estados ni maestros existentes.

## 2 · Modelo lógico

| Modelo | Tabla propuesta | Campos principales |
|---|---|---|
| `MaintenanceProcedure` | `maintenance_procedures` | id, empresa_id, code, name, description, machine_type_id, active, timestamps |
| `MaintenanceProcedureVersion` | `maintenance_procedure_versions` | procedure_id, version, status, change_notes, published_by_id, published_at |
| `MaintenanceProcedureStep` | `maintenance_procedure_steps` | version_id, position, code, title, instructions, response_type, required, config_json |
| `MaintenanceProcedureEvent` | `maintenance_procedure_events` | empresa_id, procedure_id, version_id, event, actor_id, estados, detail, created_at |
| `WorkOrderChecklist` | `work_order_checklists` | empresa_id, work_order_id, procedure_version_id, status, assigned_technician_id, completed_at, reviewed_by_id, reviewed_at |
| `WorkOrderChecklistResponse` | `work_order_checklist_responses` | checklist_id, step_id, value_json, conformity, justification, resolution, firma, performed_by_user_id, recorded_by_user_id |
| `WorkOrderChecklistEvidence` | `work_order_checklist_evidences` | empresa_id, checklist_id, response_id, storage_key, mime_type, size, checksum, uploaded_by_id |
| `WorkOrderChecklistEvent` | `work_order_checklist_events` | empresa_id, checklist_id, event, actor_id, detail, created_at |
| `MaintenanceLogEntry` | `maintenance_log_entries` | empresa_id, work_order_id/incident_id/machine_id, entry_type, body, visibility, author_id, performed_by_user_id, created_at |
| `MaintenanceLogAttachment` | `maintenance_log_attachments` | entry_id/response_id, storage_key, original_name, mime_type, size, uploaded_by_id, checksum |
| `MaintenanceLogEvent` | `maintenance_log_events` | empresa_id, entry_id, event, actor_id, detail, created_at |
| `AssetMeter` | `asset_meters` | empresa_id, machine_id, code, name, meter_type, unit, decimals, active, rules_json |
| `MeterReading` | `meter_readings` | empresa_id, meter_id, value, measured_at, source, performed_by_user_id, recorded_by_user_id, idempotency_key, notes |
| `MeterEvent` | `meter_events` | empresa_id, meter_id, reading_id, event, actor_id, detail, created_at |

## 3 · Reglas de integridad

- Toda referencia cruzada debe pertenecer al mismo `empresa_id`; la FK no sustituye la validación tenant-safe del servicio.
- `MaintenanceProcedure.code` es único por tenant.
- La combinación `procedure_id + version` es única.
- Una versión publicada es inmutable; cualquier cambio crea una nueva versión.
- `MaintenanceProcedureStep.position` es única dentro de la versión.
- Una OT tiene máximo un checklist activo por versión de procedimiento.
- Una respuesta pertenece al paso y checklist de la misma versión.
- `performed_by_user_id` identifica al ejecutor; `recorded_by_user_id`, al usuario autenticado que guardó.
- Una entrada de bitácora apunta exactamente a uno entre OT, incidencia o activo.
- Los adjuntos guardan checksum y metadata; el archivo nunca define por sí mismo el tenant.
- Un medidor pertenece a un solo activo y no cambia de tipo o unidad después de recibir lecturas.
- `MeterReading.idempotency_key` es única por tenant cuando está presente.
- Las lecturas se conservan; una corrección genera una nueva lectura vinculada a la anterior.

## 4 · Procedimientos versionados

Estados de versión:

```text
draft ──► published ──► retired
  │
  └──► deleted (solo si nunca fue publicada ni utilizada)
```

Al asignar una versión a una OT, Roustix crea un `WorkOrderChecklist`. Las
respuestas se vinculan a los pasos inmutables de esa versión, por lo que una
actualización posterior del procedimiento no altera la historia de la OT.

## 5 · Tipos de paso

| Tipo | Valor esperado |
|---|---|
| `confirmation` | realizado / no realizado / no aplica |
| `text` | observación breve o diagnóstico |
| `number` | valor numérico con rango opcional |
| `choice` | opción de catálogo incluida en `config_json` |
| `measurement` | valor + unidad; puede relacionarse con un medidor |
| `evidence` | uno o más adjuntos obligatorios |
| `signature` | confirmación de identidad, fecha y propósito; no firma criptográfica en v1 |

La configuración del paso puede declarar límites, opciones, evidencia mínima y
si “no aplica” requiere justificación.

## 6 · Checklist de OT

El checklist es una instancia histórica. Su progreso se calcula en servidor:

```text
progreso = pasos obligatorios válidos / total de pasos obligatorios
```

No se considera completo si:

- falta un paso obligatorio;
- existe una no conformidad sin resolución o justificación aprobada;
- falta evidencia requerida;
- el paso de firma requerido no fue confirmado.

Completar el checklist permite solicitar la finalización de la OT, pero no
cierra administrativamente la orden; se conserva el flujo supervisor existente.

## 7 · Bitácora contextual

La bitácora combina entradas humanas y eventos del sistema en una línea de
tiempo, sin reemplazar `IncidentHistory`, jornadas ni auditoría.

Visibilidades iniciales:

- `internal`: técnicos, supervisores y administradores autorizados;
- `requester`: visible también para el reportante relacionado;
- `system`: evento generado por Roustix, no editable.

Las entradas son inmutables después de publicarse. Una corrección referencia la
entrada anterior y conserva ambas.

### Implementado en Sprint 19.4

La migración `jq8g4i60n93y` agrega entradas, adjuntos y eventos. El servicio
resuelve el contexto y aplica tenant, rol y relación operativa antes de consultar,
escribir o descargar. Los adjuntos se almacenan fuera de `static` y las entradas
visibles para el reportante se limitan a su propia incidencia.

## 8 · Medidores

Tipos iniciales:

- `cumulative`: horas, kilómetros, ciclos o producción acumulada;
- `gauge`: temperatura, presión, vibración u otro valor instantáneo.

Para acumulativos, una lectura menor a la anterior requiere un evento explícito
de reinicio, reemplazo o rollover. Para gauge, `rules_json` puede conservar rangos
de referencia, pero Sprint 19 no genera OT automáticamente.

### Implementado en Sprint 19.5

La migración `kr9h5j71o04z` incorpora medidores, lecturas y eventos. Las series
acumulativas se validan cronológicamente; las anomalías y valores instantáneos
fuera de rango requieren clasificación y justificación. Las correcciones crean
una lectura nueva. Los activos con `horas_operacion` reciben un horómetro
`RUNTIME_HOURS` y una lectura inicial idempotente, conservando el campo legado.

## 9 · Límites de servicio

```text
app/maintenance_execution/
├── __init__.py
├── models.py       # entidades de ejecución
├── service.py      # comandos y transiciones
├── queries.py      # lecturas tenant-safe
├── permissions.py  # capacidades específicas
├── routes.py       # UI Maintenance
├── audit.py        # eventos operativos
├── storage.py      # adjuntos y validaciones
└── events.py       # catálogo para Sprint 20
```

`app/routes.py` delegará progresivamente; no se añadirá la lógica nueva al
monolito de rutas. Los cambios de estado de OT seguirán pasando por el contrato
existente de Maintenance.

### Implementado en Sprint 19.1

El paquete `app/maintenance_execution/` contiene los modelos, servicios y rutas
del catálogo. La UI vive en `templates/maintenance_execution/` y la migración
canónica es `gm5d1f37k60v`. La asignación de una versión a una OT y las respuestas
de ejecución no forman parte de 19.1; se implementan en 19.2.

### Implementado en Sprint 19.2

La migración `hn6e2g48l71w` incorpora checklist, respuestas y eventos. La OT
conserva snapshots del procedimiento, mientras cada respuesta diferencia
`performed_by_user_id` de `recorded_by_user_id`. La validación de cierre se hace
en servidor y mantiene la OT en proceso si faltan pasos obligatorios.

### Implementado en Sprint 19.3

La migración `ip7f3h59m82x` agrega conformidad, resolución, confirmación de firma,
revisión y evidencias privadas. Los archivos se almacenan fuera de rutas públicas,
se validan por extensión, MIME, firma binaria y tamaño, y se descargan únicamente
después de revalidar tenant y relación operativa.

## 10 · Seguridad y almacenamiento

- Tipos permitidos iniciales: imágenes y PDF; formatos adicionales requieren decisión explícita.
- Tamaño máximo configurable con un límite seguro de plataforma.
- Nombre original solo es metadata; la clave de almacenamiento se genera en servidor.
- No se sirve una ruta recibida directamente del usuario.
- Toda descarga revalida tenant, rol y relación con la entidad.
- El checksum permite detectar duplicados y preservar integridad.
- Eliminación lógica; la política de retención física se definirá con límites por plan.
