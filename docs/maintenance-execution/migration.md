# Sprint 19 · Compatibilidad y migración

## 1 · Principio

Sprint 19 es una evolución aditiva. Ninguna OT, incidencia, jornada, informe,
repuesto o lectura existente debe perderse o reinterpretarse silenciosamente.

## 2 · Matriz de compatibilidad

| Capacidad actual | Decisión Sprint 19 |
|---|---|
| `Machine.checklist_registro` | Se conserva como validación del alta del activo; no se convierte en procedimiento técnico |
| `Machine.horas_operacion` | Se conserva durante transición; puede sembrar un medidor “Horómetro” y una lectura inicial |
| `PreventiveMaintenancePlan.actividad` | Puede sugerir un procedimiento, pero no se migra automáticamente sin revisión |
| `WorkOrder.titulo/descripcion` | Continúa como alcance de la OT; no se reemplaza por el procedimiento |
| `WorkOrderJornada` | Permanece como registro de tiempo y costos; puede mostrarse en timeline como evento de solo lectura |
| `WorkOrderInforme` | Permanece como informe técnico; no se transforma en comentario |
| `IncidentHistory` | Sigue siendo historial de estados; se proyecta en timeline sin duplicar filas |
| Adjuntos existentes | Permanecen en su almacenamiento actual; migración física fuera de 19.0 |
| OT históricas | No reciben checklist obligatorio retroactivo |

## 3 · Migración de horas de operación

La migración propuesta para `Machine.horas_operacion` es idempotente:

1. seleccionar activos del tenant con valor no nulo;
2. crear un `AssetMeter` acumulativo con código `runtime_hours` si no existe;
3. crear una lectura inicial con `source=legacy_migration`;
4. conservar el valor original durante al menos todo Sprint 19;
5. registrar ID de migración e idempotency key por activo;
6. comparar ambos valores antes de retirar el campo legacy en un sprint futuro.

No se inventa fecha de medición histórica: la lectura se marca como importada y
con fecha efectiva de migración, conservando el valor de origen en metadata.

## 4 · Activación gradual

### Fase A · Modelos inactivos

- Ejecutar migraciones aditivas.
- No exigir checklist a ninguna OT.
- Validar tenant, índices y rollback.

### Fase B · Piloto por tenant

- Activar catálogo de procedimientos.
- Crear checklists solo para OT nuevas que seleccionen procedimiento.
- Permitir salida segura al flujo anterior.

### Fase C · Reglas operativas

- Configurar tipos de OT que requieren procedimiento.
- Bloquear solicitud de finalización únicamente para checklists creados.
- Medir adopción, pasos omitidos y no conformidades.

### Fase D · Cierre

- Sembrar medidores elegibles. ✅
- Validar métricas y auditoría. ✅
- Cerrar Sprint 19.5 después de validar migración y suite completa. ✅

La migración `kr9h5j71o04z` ejecuta la siembra idempotente. El código
`RUNTIME_HOURS` y la clave `legacy-runtime-hours-machine-{id}` evitan duplicar
el medidor o su lectura inicial. El campo legado se conserva para rollback
operativo y comparación durante la transición.

## 5 · Rollback

- Desactivar UI y obligatoriedad mediante configuración.
- Conservar tablas y datos; no ejecutar `DROP` en rollback operativo.
- Las OT continúan con jornadas, repuestos y cierre actual.
- Los checklists creados quedan consultables en solo lectura.
- Las lecturas importadas no se copian de vuelta sobre el maestro automáticamente.

## 6 · Validaciones obligatorias

- Migración repetida no crea procedimientos, medidores ni lecturas duplicadas.
- Ninguna fila cruza `empresa_id`.
- Una OT histórica puede abrirse y cerrarse con el flujo previo.
- Una OT con checklist activo respeta validaciones nuevas.
- El registro delegado conserva ejecutor y registrador distintos.
- El timeline no duplica `IncidentHistory`, jornadas o cambios de estado.
- Rollback lógico no elimina evidencias ni lecturas.
