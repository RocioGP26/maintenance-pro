# Fase 1 · Auditoría MRG-02 · Mantenimiento

**Sprint 14.1–14.4** · **Estado:** ✅ **Fase 1 cerrada** (2026-07-10)  
**MRG:** [MRG-02-MAINT](/mrg/chapters/02-maintenance.md)  
**Última revisión:** 2026-07-10

---

## 1 · Resumen ejecutivo

| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué existe? | Activos, tipos, OT, preventivo, calendario, incidencias, repuestos técnicos, técnicos, proveedores servicio |
| ¿Qué hace? | CMMS multi-tenant operativo con sector templates y campos personalizados |
| ¿Qué falta? | Jerarquía padre/hijo en UI · baja de activo · estado OT «En espera» · historial completo (incidencias, costos) |
| ¿Qué sobra? | Terminología legacy «equipo/máquina/Programador» *(corregido parcialmente)* |
| ¿Qué difiere del MRG? | Gaps documentados en matriz §4–§6 · API CRUD · export Excel |

**Estado módulo:** 🟡 **Parcial** · **Sprint 14 Fase 1:** ✅ **Cerrado**

---

## 1.2 · Incidencias y permisos (2026-07-10)

### Incidencias §9

| Requisito MRG | Estado |
|---------------|--------|
| Solicitante reporta (área, prioridad, activo detenido) | ✅ |
| Supervisor revisa | 🟡 Sin UI asignación |
| Resolución documentada | ✅ |
| Crear OT vinculada | ✅ Admin/Superadmin |
| Prioridad + criticidad activo | 🟡 Prioridad sí; regla cruce 📋 |
| Evidencia fotográfica | 📋 Próximamente en UI |

**Copy alineado:** equipo → activo en formulario, listado y detalle.

### Permisos §2

→ Matriz completa: [02-permissions-matrix.md](02-permissions-matrix.md)

Helpers añadidos: `can_report_incident` · `can_manage_incidents` · `can_create_work_order`

### Historial activo §5 (ampliado)

- OT (últimas 10) + incidencias (últimas 5) en ficha editar activo

### Dashboard y reportes §10 / MRG-08

→ Detalle: [02-reports-audit.md](02-reports-audit.md)

### API MAG § / MRG-02

→ Detalle: [02-api-audit.md](02-api-audit.md)

- Alias `/api/v1/*` sobre legacy
- `GET maintenance/assets` · `work-orders` · `admin/summary`
- Login/`me` con `modules` y `expires_in`

---

## 2 · Mapa MRG ↔ implementación

### §3 · Entidades

| Entidad MRG | Modelo / ruta | Estado |
|-------------|---------------|--------|
| Activo | `Machine` · `/activos` | ✅ |
| Tipo de activo | `MachineType` · `/activos/tipos` | ✅ *(labels alineados)* |
| Campo personalizado | `CampoPersonalizado` · `/configuracion/campos` | ✅ |
| Ubicación | `Machine.ubicacion` · `area` | ✅ |
| Criticidad | `criticidad` · `es_critico` | ✅ |
| OT | `WorkOrder` · `/ordenes` | ✅ |
| Técnico | `Technician` · `/equipo` | ✅ |
| Proveedor servicio | `Proveedor` · `/proveedores` | ✅ |
| Repuesto | `SparePart` · `/inventario` | ✅ |
| Plan preventivo | `PreventiveMaintenancePlan` | ✅ |
| Incidencia | `/incidencias` | 🟡 *(auditoría Fase 1.2)* |

### §4 · Activos

| Requisito MRG | Implementación | Estado |
|---------------|----------------|--------|
| Estados operativos (3) | `MachineStatus` operativo · mantenimiento · falla | ✅ |
| Criticidad baja–crítica | `CRITICIDAD_CHOICES` | ✅ |
| Ciclo de vida | Registro + operación + OT | 🟡 |
| Retiro / baja | Sin baja lógica formal | 📋 Roadmap |
| Jerarquía padre/hijo | `parent_machine_id` en modelo, sin UI | 🟡 |

### §5 · Historial del activo

| Requisito | Implementación | Estado |
|-----------|----------------|--------|
| OT vinculadas | Panel en ficha editar activo (últimas 10) | 🟡 *(añadido Sprint 14)* |
| Incidencias en historial | No en ficha activo | 📋 |
| Costos acumulados | En OT, no agregados en activo | 🟡 |
| Repuestos por OT | En OT | ✅ |

### §6 · Órdenes de trabajo

| Requisito MRG | Código | Estado |
|---------------|--------|--------|
| Tipos: correctiva · preventiva · emergencia | `WorkOrderType` | ✅ |
| Estados programada · abierta · en_proceso · vencida · completada · cerrada | `WorkOrderStatus` | ✅ |
| «Asignada» | Implícito al asignar técnico/proveedor | ✅ *(doc)* |
| «En espera» | No enum dedicado | 📋 Roadmap |
| Label «Completada» | `wo_status_meta` · jornadas | ✅ *(alineado)* |
| Jornadas | `WorkOrderJornada` | ✅ |
| Repuestos | `WorkOrderRepuesto` | ✅ |
| Costos | estimado / real + repuestos | ✅ |
| Supervisor | `supervisor_technician_id` | ✅ |

---

## 3 · Alineación aplicada (2026-07-10)

### Menús (`base.html`)

| Antes | Después (MRG) |
|-------|---------------|
| Equipos | Listado de activos |
| Tipos de máquina | Tipos de activo |
| Programador | Órdenes de trabajo |
| Calendario Maestro | Calendario |

### Copy y mensajes

- Flash routes: «tipo de máquina» → «tipo de activo»
- Listado activos: «X equipos» → «X activos»
- OT list: botón «Nueva» → «Nueva OT»
- OT form: «máquina/equipo» → «activo»
- Dashboard: «equipos críticos» → «activos críticos»
- Estado OT: «Completado» → «Completada»
- Tipos catálogo: badges On/Off → Activo/Inactivo

### Completar (MRG §5)

- Historial OT en ficha de activo (editar) — últimas 10 + enlace a listado filtrado

---

## 4 · Gaps pendientes (prioridad)

| ID | Gap | MRG | Acción | Prioridad |
|----|-----|-----|--------|-----------|
| G1 | Jerarquía activo padre/hijo sin UI | §4 | Selector en formulario activo | P2 |
| G2 | Baja / retiro de activo | §4 | Campo `activo` o status baja | 📋 |
| G3 | Estado OT «En espera» | §6 | Nuevo enum + transiciones | 📋 |
| G4 | Historial completo (incidencias, costos) | §5 | Panel ampliado en activo | P2 |
| G5 | Matriz permisos MRG §2 ↔ roles plataforma | §2 | Documentar + validar middleware | P1 |
| G6 | Exportación PDF/Excel OT | §6 / MRG-08 | Revisar `/reportes` | P2 |
| G7 | API MAG mantenimiento vs rutas | MAG | Contraste Sprint 14.1b | P2 |
| G8 | Incidencias — auditoría pantallas | §9 | Copy + permisos | 🟡 Fase 1.2 |

---

## 5 · Checklist Fase 1 · ✅ Cerrada

| # | Área | Estado |
|---|------|--------|
| 1 | Menús | ✅ |
| 2 | Formularios activos | ✅ |
| 3 | Formularios OT | ✅ |
| 4 | Botones | ✅ |
| 5 | Permisos | ✅ |
| 6 | Rutas URL | ✅ |
| 7 | Estados OT | 🟡 «En espera» 📋 |
| 8 | Dashboard KPIs | ✅ |
| 9 | Reportes | 🟡 export 📋 |
| 10 | API MAG | 🟡 GET v1 · CRUD 📋 |
| 11 | MRG badges | ✅ v1.0.2 |

---

## 6 · Rutas verificadas

```
/activos · /activos/nuevo · /activos/<id>/editar · /activos/tipos
/ordenes · /ordenes/nueva · /ordenes/<id>/editar · /ordenes/planeacion
/calendario · /incidencias · /inventario · /proveedores · /equipo
/configuracion/campos · /dashboard · /reportes
```

---

## 7 · Próximos pasos

1. ~~**Cerrar MRG-02**~~ — ✅ 2026-07-10
2. **Fase 2** — MRG-03 Inventario ([checklist](../checklist.md#fase-2--mrg-03--inventario))

---

→ [Checklist maestro](../checklist.md) · [Matriz de estado](../status-matrix.md)
