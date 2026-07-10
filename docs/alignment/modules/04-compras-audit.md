# Fase 3 · Auditoría MRG-04 · Compras (Purchasing)

**Sprint 14.9–14.12** · **Estado:** ✅ **Fase 3 cerrada** (2026-07-10)  
**MRG:** [MRG-04-PUR](/mrg/chapters/04-compras.md)  
**Última revisión:** 2026-07-10

---

## 1 · Resumen ejecutivo

| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué existe? | Proveedores comerciales, registro compra/entrada (`InvCompra`), líneas, IVA, multimoneda, CxP, pagos parciales, alertas vencimiento |
| ¿Qué hace? | Subflujo Purchasing dentro de inventario comercial (`/comercial/compras`, `/cuentas-por-pagar`) |
| ¿Qué falta? | Solicitudes · aprobaciones · OC formal · recepción parcial · módulo Purchasing independiente · API MAG |
| ¿Qué sobra? | — |
| ¿Qué difiere del MRG? | Modelo documental completo vs flujo simplificado en producto (coherente con MRG §3) |

**Estado módulo:** 🟡 **Parcial** (subflujo Inventory) · **Sprint 14 Fase 3:** ✅ **Cerrado**

---

## 2 · MRG §1 · Alcance

| Requisito | Ruta / código | Estado |
|-----------|---------------|--------|
| Proveedores comerciales | `/comercial/proveedores` | ✅ |
| Registro compra / entrada | `/comercial/compras` | ✅ |
| Actualización stock | `registrar_entrada_mercancia` | ✅ |
| CxP | `/comercial/cuentas-por-pagar` | ✅ |
| Solicitudes / OC formal | — | 📋 |
| Contabilidad / tesorería | — | 📋 (excluido MRG) |

---

## 3 · MRG §2 · Entidades

| Entidad MRG | Implementación | Estado |
|-------------|----------------|--------|
| Proveedor | `InvProveedor` | ✅ |
| Orden / compra | `InvCompra` | ✅ |
| Detalle | `InvCompraLinea` | ✅ |
| Condición de pago | crédito/contado · fechas · `estado_pago` | ✅ |
| Pago | `InvCompraPago` | ✅ |
| Solicitud | — | 📋 |
| Recepción parcial | — | 📋 |

---

## 4 · MRG §3–§6 · Flujos

| Flujo MRG | Producto | Estado |
|-----------|----------|--------|
| Modelo completo (solicitud→OC→recepción) | Documentado · no implementado | 📋 |
| Flujo simplificado (alerta→proveedor→compra) | Implementado | ✅ |
| Recepción completa al registrar | Stock + costo en mismo acto | ✅ |
| Recepción parcial / rechazada | — | 📋 |
| Estados OC (borrador, pendiente…) | — | 📋 |
| Estados pago CxP | pendiente · parcial · pagada · vencida | ✅ |

---

## 5 · MRG §4 · Proveedores

| Campo / operación | Estado |
|-------------------|--------|
| Razón social · NIT | ✅ |
| Contactos · tel · email | ✅ |
| Alta / edición | ✅ |
| Distinción proveedor servicio (MRG-02) | ✅ copy en listado |
| Condiciones de pago por proveedor | 🟡 (por factura, no catálogo) |
| Baja / inactivar | 🟡 solo activos en listado |

---

## 6 · CxP · Auditoría detallada

| Requisito | Estado | Notas |
|-----------|--------|-------|
| Vista dedicada CxP | ✅ | `/comercial/cuentas-por-pagar` |
| KPI saldo / vencidas / por vencer | ✅ | `kpis_cxp` |
| Resumen por proveedor | ✅ | chips filtrables |
| Pago parcial / total | ✅ | modal compartido con detalle compra |
| Filtro compras por CxP | ✅ | `?alerta=por_vencer|vencidas` |
| Nav submenú Compras | ✅ | Listado · Cuentas por pagar |
| Integración dashboard | ✅ | `alertas_cxp_compras` |
| Contabilidad formal | 📋 | excluido MRG |

---

## 7 · MRG §9 · Indicadores

| KPI | Implementación | Estado |
|-----|----------------|--------|
| CxP pendientes / vencidas | dashboard · `cxp_list` · alertas | ✅ |
| Compras del período | 🟡 parcial en dashboard | 🟡 |
| Órdenes abiertas / recepciones pendientes | N/A (sin OC) | 📋 |
| Ranking proveedores / productos | — | 📋 |

---

## 8 · Menús y copy

| Elemento | Antes | Objetivo MRG | Estado |
|----------|-------|--------------|--------|
| Nav sidebar | Compras + CxP sueltos | Submenú Compras | ✅ |
| Listado compras | Entradas / compras a proveedor | Compras | ✅ |
| CTA principal | Registrar entrada | Registrar entrada | ✅ |
| Proveedores | Proveedores comerciales | ✅ distinto de servicio | ✅ |
| CxP | Cuentas por pagar (submenú) | ✅ | ✅ |

---

## 9 · API MAG

| Endpoint | Estado |
|----------|--------|
| `/api/v1/purchasing/orders` | 📋 |
| `/api/v1/purchasing/suppliers` | 📋 |

---

## 10 · Checklist Fase 3 · ✅ Cerrada

| # | Área | Estado |
|---|------|--------|
| 1 | Menús | ✅ |
| 2 | Formularios compra | ✅ |
| 3 | Proveedores | ✅ |
| 4 | CxP y pagos | ✅ |
| 5 | Rutas URL | ✅ |
| 6 | Stock al confirmar | ✅ |
| 7 | Alertas vencimiento | ✅ |
| 8 | Listado estado pago | ✅ |
| 9 | API | 📋 |
| 10 | MRG badges | ✅ |

---

## 11 · Rutas verificadas

```
/comercial/proveedores · /proveedores/nuevo · /proveedores/<id>/editar
/comercial/compras · /compras/nueva · /compras/<id> · /compras/<id>/editar
/comercial/cuentas-por-pagar · /cuentas-por-pagar/<id>/pago
/comercial/api/productos/<id>/ultimo-costo
```

---

## 12 · Gaps abiertos (📋)

- Módulo Purchasing independiente
- Solicitud · aprobación · OC formal · recepción parcial
- API MAG purchasing
- KPIs ranking compras / entrega

---

## 13 · Próximos pasos

1. ~~**Cerrar MRG-04 Fase 3**~~ — ✅ 2026-07-10
2. **Fase 4** — MRG-05 Ventas ([checklist](../checklist.md#fase-4--mrg-05--ventas))

---

→ [Checklist maestro](../checklist.md) · [Matriz de estado](../status-matrix.md)
