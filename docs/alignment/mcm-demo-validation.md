# Validación MCM-07-DEMO · Sprint 14 ALIGN

**Fecha:** 2026-07-10 · **Estado:** ✅ **Validada** contra producto post-ALIGN  
**Referencia:** [MCM-07-DEMO](/mcm/chapters/07-demo-comercial.md) · PLAY-001–005

---

## Resumen

| Pregunta | Resultado |
|----------|-----------|
| ¿Los flujos PLAY-003 existen en producto? | ✅ |
| ¿Las rutas coinciden con la nav alineada? | ✅ (con notas submenús) |
| ¿Hay copy desalineado en demo? | 🟡 mencionar submenús al presentar |
| ¿Promesas roadmap en demo? | ✅ sin cambio · evitar según MCM-07 §8 |

---

## PLAY-003 · Mantenimiento

| Paso demo (MCM §6–§7) | Ruta producto | Estado |
|------------------------|---------------|--------|
| Incidencia | `/incidencia` · `/incidencias` | ✅ |
| Crear OT | detalle incidencia → crear OT | ✅ |
| Activos | `/activos` (submenú Activos) | ✅ |
| Preventivos | `/ordenes/planeacion` · `/calendario` | ✅ |
| OT ciclo completo | `/ordenes` | ✅ |
| Repuestos | `/inventario` («Repuestos técnicos») | ✅ 🟡 solo OT correctiva |
| Historial activo | ficha `/activos/<id>` | ✅ |
| KPIs PLAY-004 | `/dashboard` o **Indicadores → Mantenimiento** (`/reportes`) | ✅ |

---

## PLAY-003 · Inventario comercial

| Paso demo (MCM §6–§7) | Ruta producto | Estado |
|------------------------|---------------|--------|
| Productos / stock | `/comercial/productos` | ✅ |
| Entrada mercancía | **Compras → Listado** · `/comercial/compras` | ✅ |
| CxP (mencionar si Finanzas) | **Compras → Cuentas por pagar** | ✅ |
| Venta POS | **Ventas → Listado** · `/comercial/ventas/nueva` | ✅ |
| Cartera | **Ventas → Por cobrar** | ✅ |
| Clientes | **Ventas → Clientes** | ✅ |
| Alertas bajo stock | dashboard · filtro productos | ✅ |
| KPIs PLAY-004 | `/comercial/dashboard` o **Indicadores → Inventario** | ✅ |

---

## Nav post-Sprint 14 (guía para presentador)

| Antes (genérico) | Hoy en producto |
|------------------|-----------------|
| «Menú Compras» | Submenú **Compras** → Listado · Cuentas por pagar |
| «Menú Ventas» | Submenú **Ventas** → Listado · Por cobrar · Clientes |
| «Reportes» (tenant mixto) | Submenú **Indicadores** → Mantenimiento · Inventario |
| «Equipos» | **Activos** |
| «Inventario técnico» | **Repuestos técnicos** |

No mostrar en demo: **Administración** (MCM-07 §8) salvo que el DMU lo pida explícitamente.

---

## Historias PLAY vs código

| Historia MCM §6 | Verificación Fase 8 |
|-----------------|---------------------|
| Máquina → incidencia → OT → repuestos → KPI | ✅ [09-workflows-audit.md](modules/09-workflows-audit.md) |
| Mercancía → stock → venta → alerta → compra | ✅ |

---

## Gaps · no prometer en demo

- Export Excel OT/activos
- Repuestos en OT preventiva
- CRM pipeline · Purchasing formal (OC)
- Transferencia repuesto ↔ producto comercial

→ Alineado con MCM-05 §5 y MRG badges 📋

---

## Conclusión

**MCM-07-DEMO sigue siendo válido.** Los flujos core coinciden con el producto alineado. Actualizar guion verbal: **submenús Compras, Ventas e Indicadores** (Sprint 14 nav).

→ [Checklist Sprint 14](checklist.md#cierre-sprint-14)
