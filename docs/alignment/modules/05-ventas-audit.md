# Fase 4 · Auditoría MRG-05 · Ventas (Sales)

**Sprint 14.13–14.16** · **Estado:** ✅ **Fase 4 cerrada** (2026-07-10)  
**MRG:** [MRG-05-SALES](/mrg/chapters/05-ventas.md)  
**Última revisión:** 2026-07-10

---

## 1 · Resumen ejecutivo

| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué existe? | POS (`/comercial/ventas/nueva`), listado, crédito/contado, abonos, clientes, descuento stock |
| ¿Qué hace? | Subflujo Sales dentro de inventario comercial |
| ¿Qué falta? | Borrador/anulación · CxC dedicada · listas precios · cotizaciones · API MAG · Sales Pro |
| ¿Qué sobra? | — |
| ¿Qué difiere del MRG? | Cartera por cobrar = filtro en listado (no pantalla CxC) — coherente con MRG §6 |

**Estado módulo:** 🟡 **Parcial** (núcleo operativo) · **Sprint 14 Fase 4:** ✅ **Cerrado**

---

## 2 · MRG §1 · Alcance

| Requisito | Ruta / código | Estado |
|-----------|---------------|--------|
| POS | `/comercial/ventas/nueva` | ✅ |
| Ventas contado | `forma_pago=contado` | ✅ |
| Ventas crédito | `forma_pago=credito` | ✅ |
| Abonos | `ventas_registrar_abono` · `InvVentaCobro` | ✅ |
| Clientes | `/comercial/clientes` | ✅ |
| Descuento stock | `registrar_venta` | ✅ |
| CRM / fidelización | — | 📋 MRG-06 |

---

## 3 · MRG §2–§3 · Entidades y flujo

| Entidad MRG | Implementación | Estado |
|-------------|----------------|--------|
| Cliente | `InvCliente` | ✅ |
| Venta | `InvVenta` | ✅ |
| Detalle | `InvVentaLinea` | ✅ |
| Cobro | `InvVentaCobro` | ✅ |
| Forma pago | contado · crédito | ✅ |
| Saldo pendiente | `saldo_pendiente` · `estado_cobro` | ✅ |

**Validaciones:** crédito requiere cliente ✅ · stock insuficiente bloquea venta ✅

---

## 4 · MRG §4–§5 · POS y estados

| Función | Estado |
|---------|--------|
| Búsqueda productos POS | ✅ |
| Multimoneda cobro | ✅ |
| Cliente opcional (contado) | ✅ |
| Estados cobro (pagada/pendiente/parcial) | ✅ |
| Borrador / anulada | 📋 Sales Pro |

---

## 5 · Cartera por cobrar · Auditoría

Analogía con CxP (MRG-04): **sin módulo CxC dedicado** — vista filtrada sobre ventas a crédito.

| Requisito | Estado | Notas |
|-----------|--------|-------|
| Filtro `?cobro=pendiente` | ✅ | listado ventas |
| Columnas saldo / estado cobro | ✅ | |
| Abono desde detalle | ✅ | |
| Nav submenú Ventas | ✅ | Listado · Por cobrar |
| KPI ventas hoy | ✅ | dashboard |
| CxC formal / vencimientos masivos | 📋 | roadmap |

---

## 6 · MRG §7 · Clientes

| Campo / operación | Estado |
|-------------------|--------|
| Alta / edición / baja lógica | ✅ |
| Búsqueda | ✅ |
| Vinculación venta | ✅ |
| Historial / saldo agregado en ficha | 🟡 parcial |
| Evolución CRM | 📋 MRG-06 |

---

## 7 · Menús y copy

| Elemento | Objetivo MRG | Estado |
|----------|--------------|--------|
| Nav | Submenú Ventas | ✅ |
| Listado | Ventas | ✅ |
| POS | Nueva venta | ✅ |
| Por cobrar | Cartera ligera | ✅ |
| Clientes | Entrada separada (→ CRM) | ✅ |

---

## 8 · API MAG

| Endpoint | Estado |
|----------|--------|
| `/api/v1/sales/orders` | 📋 |
| `/api/v1/sales/customers` | 📋 |

---

## 9 · Checklist Fase 4 · ✅ Cerrada

| # | Área | Estado |
|---|------|--------|
| 1 | Menús | ✅ |
| 2 | POS | ✅ |
| 3 | Crédito / abonos | ✅ |
| 4 | Clientes | ✅ |
| 5 | Stock al vender | ✅ |
| 6 | Cartera por cobrar | ✅ |
| 7 | Dashboard KPIs | ✅ |
| 8 | API | 📋 |
| 9 | MRG badges | ✅ |

---

## 10 · Rutas verificadas

```
/comercial/ventas · /ventas/nueva · /ventas/<id>
/comercial/ventas/<id>/abono
/comercial/clientes · /clientes/nuevo · /clientes/<id>/editar
```

---

## 11 · Gaps abiertos (📋)

- Sales Pro (cotizaciones, comisiones, FE)
- Anulación / borrador venta
- API MAG sales
- CxC dedicada (módulo finanzas)

---

## 12 · Próximos pasos

1. ~~**Cerrar MRG-05 Fase 4**~~ — ✅ 2026-07-10
2. **Fase 5** — MRG-06 CRM ([checklist](../checklist.md#fase-5--mrg-06--crm))

---

→ [Checklist maestro](../checklist.md) · [Matriz de estado](../status-matrix.md)
