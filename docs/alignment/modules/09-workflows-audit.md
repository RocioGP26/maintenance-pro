# Fase 8 · Auditoría MRG-09 · Flujos transversales

**Sprint 14.29–14.32** · **Estado:** ✅ **Fase 8 cerrada** (2026-07-10)  
**MRG:** [MRG-09-WORKFLOWS](/mrg/chapters/09-workflows.md)  
**Última revisión:** 2026-07-10

---

## 1 · Resumen ejecutivo

| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué existe? | Flujos mantenimiento · incidencia→OT · preventivos · repuestos · compra/venta/stock · onboarding · IAM |
| ¿Qué hace? | Conecta módulos con acciones encadenadas y stock automático |
| ¿Qué falta? | CRM pipeline · Purchasing formal · repuestos en OT preventiva · transferencia repuesto↔producto · webhooks |
| ¿Qué sobra? | — |
| ¿Qué difiere del MRG? | Consumo repuestos solo OT **correctiva**; abastecimiento directo sin OC |

**Estado módulo:** 🟡 **Parcial** · **Sprint 14 Fase 8:** ✅ **Cerrado**

→ Auditorías por módulo: Fases 1–7 en `docs/alignment/modules/`

---

## 2 · MRG §1 · Filosofía

| Principio | Estado |
|-----------|--------|
| Procesos vs pantallas aisladas | ✅ |
| Trazabilidad entre pasos | 🟡 |
| Reducir trabajo manual | ✅ stock OT · compra · venta |
| Indicadores al cierre | ✅ dashboard |

---

## 3 · MRG §2 · Flujo Mantenimiento

| Paso | Implementación | Estado |
|------|----------------|--------|
| Activo registrado | `/activos` CRUD | ✅ |
| Plan preventivo | OT preventiva anual · `/ordenes/planeacion` | ✅ |
| Generación OT | `crear_programacion_preventiva_anio` | ✅ |
| Asignación técnico | campo `technician_id` OT | ✅ |
| Trabajo / cierre | estados OT · `work_order_status` | ✅ |
| Consumo repuestos | `_guardar_repuestos_orden` | 🟡 solo correctiva |
| Historial activo | ficha activo OT + incidencias | 🟡 sin costos repuesto agregados |

**Rutas:** `/activos` · `/ordenes` · `/ordenes/planeacion` · `/calendario`

---

## 4 · MRG §3 · Flujo incidencias

| Paso | Implementación | Estado |
|------|----------------|--------|
| Registrar incidencia | `/incidencia` · `/incidencias` | ✅ |
| Supervisor revisa | permisos `can_manage_incidents` | ✅ |
| Resuelta sin OT | `POST /incidencias/<id>/resolver` | ✅ |
| Crear OT | `POST /incidencias/<id>/crear-ot` | ✅ |
| Vínculo incidencia↔OT | `inc.work_order_id` | ✅ |
| Tipo OT desde prioridad | crítica → emergencia · resto → correctivo | ✅ |

---

## 5 · MRG §4 · Flujo abastecimiento

| Paso | Implementación | Estado |
|------|----------------|--------|
| Producto bajo stock | dashboard · filtro · alertas | ✅ |
| Alerta operativa | KPI bajo stock comercial | ✅ |
| Registro compra | `/comercial/compras` | ✅ |
| Entrada mercancía | `registrar_entrada_mercancia` | ✅ |
| Actualización stock | `producto.stock += cantidad` | ✅ |
| CxP al registrar | `InvCompra` estado_pago | ✅ |
| Solicitud / OC formal | — | 📋 |

---

## 6 · MRG §5–§6 · Ventas y ciclo comercial

| Paso | Implementación | Estado |
|------|----------------|--------|
| Venta POS | `/comercial/ventas/nueva` · `registrar_venta` | ✅ |
| Salida inventario | validación stock · descuento automático | ✅ |
| Contado | cobro total al confirmar | ✅ |
| Crédito + abonos | `InvVentaCobro` | ✅ |
| Cliente en venta | `InvCliente` | ✅ |
| Proveedor → compra → inv → venta → cobro | flujo completo | ✅ |

---

## 7 · MRG §7–§8 · Onboarding e IAM

| Paso | Implementación | Estado |
|------|----------------|--------|
| Wizard onboarding | `/onboarding` | ✅ |
| Sector · datos ejemplo | `onboarding_service` | ✅ |
| Crear usuario | `/equipo` | ✅ |
| Roles y permisos | `permissions.py` | ✅ |
| Módulos por tenant | `Empresa.modulos` | ✅ |

---

## 8 · MRG §9 · Integración entre módulos

| Origen → Destino | Estado |
|------------------|--------|
| Mantenimiento → Reportes | ✅ KPIs `/dashboard` |
| Inventario → Ventas | ✅ stock al vender |
| Compras → Inventario | ✅ entrada mercancía |
| Administración → Todos | ✅ permisos |
| CRM → Ventas | 📋 |
| Repuesto técnico ↔ producto comercial | separados · sin transferencia | ✅ doc |

---

## 9 · MRG §10–§12 · Roadmap · trazabilidad · automatización

| Tema | Estado |
|------|--------|
| CRM → cotización → venta | 📋 |
| CxP avanzado | 🟡 pagos parciales hoy |
| Facturación electrónica | 📋 |
| BI / webhooks MAG | 📋 |
| OT preventivas programadas | ✅ |
| Stock compra/venta automático | ✅ |
| Sync estados OT por fecha | ✅ `sincronizar_estados_ordenes` |
| Alertas stock mínimo | ✅ |
| `TenantActivityLog` | 🟡 login · acciones limitadas |
| Historial producto (kardex UI) | 🟡 implícito en líneas compra/venta |

---

## 10 · Checklist Fase 8 · ✅ Cerrada

| # | Flujo | Estado |
|---|-------|--------|
| 1 | Incidencia → OT | ✅ |
| 2 | OT preventiva | ✅ |
| 3 | Consumo repuestos | 🟡 correctiva |
| 4 | Compra → inventario | ✅ |
| 5 | Venta → inventario | ✅ |
| 6 | Onboarding | ✅ |
| 7 | IAM / permisos | ✅ |
| 8 | MRG badges | ✅ |

---

## 11 · Rutas verificadas

```
/incidencia · /incidencias/<id>/crear-ot · /incidencias/<id>/resolver
/ordenes · /ordenes/planeacion · /calendario
/comercial/compras · /comercial/ventas/nueva
/onboarding · /equipo
```

**Código clave:** `incidencias_crear_ot` · `registrar_entrada_mercancia` · `registrar_venta` · `_guardar_repuestos_orden`

---

## 12 · Gaps abiertos (📋)

- Repuestos en OT preventiva / emergencia
- Purchasing formal (solicitud · OC · recepción parcial)
- CRM pipeline → venta
- Transferencia repuesto técnico ↔ producto comercial
- Kardex visible por producto · auditoría acciones ampliada
- Webhooks MAG operativos

---

## 13 · Próximos pasos

1. ~~**Cerrar MRG-09 Fase 8**~~ — ✅ 2026-07-10
2. **Cierre Sprint 14** — checklist transversal · validación MCM demo

---

→ [Checklist maestro](../checklist.md) · [Matriz de estado](../status-matrix.md)
