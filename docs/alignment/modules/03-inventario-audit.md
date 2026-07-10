# Fase 2 · Auditoría MRG-03 · Inventario comercial

**Sprint 14.5–14.8** · **Estado:** ✅ **Fase 2 cerrada** (2026-07-10)  
**MRG:** [MRG-03-INV](/mrg/chapters/03-inventario.md)  
**Última revisión:** 2026-07-10

---

## 1 · Resumen ejecutivo

| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué existe? | Catálogo `InvProducto`, stock, ubicación, mínimos, import/export Excel, dashboard comercial, entradas/compras, ventas/POS, clientes, proveedores comerciales |
| ¿Qué hace? | Inventario comercial multi-tenant en `/comercial/*` · repuestos técnicos separados en `/inventario` (MRG-02) |
| ¿Qué falta? | Pantalla kardex dedicada · ajuste manual de stock · API MAG `/inventory/*` · rotación/BI |
| ¿Qué sobra? | — (CxP/ventas son MRG-04/05 pero comparten nav comercial) |
| ¿Qué difiere del MRG? | Nav «Inventario de Repuestos» vs «Repuestos técnicos» · API no expuesta · kardex implícito |

**Estado módulo:** ✅ **Producción** (web) · **Sprint 14 Fase 2:** ✅ **Cerrado**

---

## 2 · MRG §1 · Alcance

| Requisito | Ruta / código | Estado |
|-----------|---------------|--------|
| Catálogo productos SKU | `/comercial/productos` | ✅ |
| Stock y ubicación | campo `ubicacion` en producto | ✅ |
| Alertas stock mínimo | listado · dashboard · alertas campana | ✅ |
| Import/export Excel | import · export catálogo · plantilla · bajo stock | ✅ |
| Valorización inventario | dashboard KPI · sum(stock×costo) | ✅ |
| Repuestos técnicos (excluido) | `/inventario` · `SparePart` | ✅ MRG-02 |

---

## 3 · MRG §2–§3 · Entidades y kardex

| Entidad MRG | Implementación | Estado |
|-------------|----------------|--------|
| Producto | `InvProducto` | ✅ |
| Ubicación | campo texto `ubicacion` | ✅ |
| Movimiento | implícito vía `InvCompra` / `InvVenta` | 🟡 |
| Stock mínimo | `stock_minimo` + filtro `alerta=bajo` | ✅ |

**Kardex:** no hay pantalla dedicada — coherente con MRG §3. Movimientos reconstruibles desde compras y ventas.

**Regla venta > stock:** validada en `registrar_venta` (`service.py`).

---

## 4 · MRG §4 · Catálogo

| Operación | Estado | Notas |
|-----------|--------|-------|
| Alta producto | ✅ | `/comercial/productos/nuevo` |
| Edición | ✅ | |
| Baja lógica | ✅ | inactivar/activar |
| Precio venta y costo | ✅ | última compra actualiza costo |
| Multimoneda | ✅ | `precios_json` · tenant |
| Importación Excel | ✅ | `.xlsx` |
| Exportación catálogo | ✅ | vista actual |
| Export bajo stock | ✅ | |
| Alertas en listado | ✅ | badge + filtro + filas warning |

---

## 5 · MRG §5 · Valorización

| Indicador | Implementación | Estado |
|-----------|----------------|--------|
| Valor inventario | `kpis_dashboard_inventario` | ✅ |
| Productos activos | conteo en dashboard | ✅ |
| Rotación | — | 📋 Roadmap |

---

## 6 · MRG §6 · Distinción Mantenimiento vs Inventario

| Aspecto | Repuesto técnico | Producto comercial | Alineado |
|---------|------------------|-------------------|----------|
| Módulo clave | `mantenimiento` | `inventario` | ✅ |
| Entidad | `SparePart` | `InvProducto` | ✅ |
| Ruta | `/inventario` | `/comercial/productos` | ✅ |
| Proveedor | proveedor servicio OT | `InvProveedor` | ✅ |
| Nav sidebar | Mantenimiento | Inventario comercial | ✅ |

**Alineación Sprint 14:** menú mantenimiento → «Repuestos técnicos» (no «Inventario de Repuestos»).

---

## 7 · Menús y copy

| Elemento | Antes | MRG / objetivo | Estado |
|----------|-------|----------------|--------|
| Nav repuestos | Inventario de Repuestos | Repuestos técnicos | ✅ |
| Nav dashboard comercial | Resumen ventas | Dashboard inventario | ✅ |
| Sección sidebar | Inventario comercial | Inventario comercial | ✅ |
| Productos | Productos | Productos | ✅ |
| Entradas | Entradas / Compras | ✅ (MRG-04 subflujo) | ✅ |

---

## 8 · Permisos

| Área | Estado | Notas |
|------|--------|-------|
| Módulo `inventario` | ✅ | `@require_module(MODULO_INVENTARIO)` |
| Roles inventario | ✅ | `USER_ROLE_LABELS_INVENTARIO` · Vendedor |
| Repuestos técnicos | ✅ | permisos mantenimiento (`perm.crear` en listado) |

→ Sin matriz MRG-03 dedicada (roles en MRG-07 · permisos por módulo).

---

## 9 · API MAG

| Endpoint MAG | Implementado | Estado |
|--------------|--------------|--------|
| `GET /api/v1/inventory/products` | No | 📋 |
| `GET /api/v1/inventory/stock` | No | 📋 |
| `GET /api/v1/inventory/movements` | No | 📋 |

→ Solo API interna: `/comercial/api/productos/<id>/ultimo-costo`

---

## 10 · Checklist Fase 2 · ✅ Cerrada

| # | Área | Estado |
|---|------|--------|
| 1 | Menús | ✅ |
| 2 | Formularios producto | ✅ |
| 3 | Botones / CTAs | ✅ |
| 4 | Permisos módulo | ✅ |
| 5 | Rutas URL | ✅ |
| 6 | Dashboard KPIs | ✅ |
| 7 | Import/export Excel | ✅ |
| 8 | Alertas bajo stock | ✅ |
| 9 | API MAG | 📋 |
| 10 | MRG badges | ✅ |
| 11 | Distinción repuestos | ✅ |

---

## 11 · Rutas verificadas

```
/comercial/dashboard
/comercial/productos · /productos/nuevo · /productos/<id>/editar
/comercial/productos/export · /export/bajo-stock · /export/plantilla · /import
/comercial/compras · /compras/nueva · /compras/<id>
/comercial/ventas · /ventas/nueva · /ventas/<id>
/comercial/clientes · /comercial/proveedores · /comercial/cuentas-por-pagar
/inventario · /inventario/nuevo · /inventario/<id>/editar   ← MRG-02 repuestos
```

---

## 12 · Gaps abiertos (📋)

- Pantalla kardex / historial movimientos por producto
- Ajuste manual de stock (sin compra/venta)
- API MAG inventory (products · stock · movements)
- Análisis rotación inventario

---

## 13 · Próximos pasos

1. ~~**Cerrar alineación UI**~~ — ✅ 2026-07-10
2. ~~**Actualizar MRG-03**~~ — ✅ v1.0.1
3. **Fase 3** — MRG-04 Compras ([checklist](../checklist.md#fase-3--mrg-04--compras))

---

→ [Checklist maestro](../checklist.md) · [Matriz de estado](../status-matrix.md)
