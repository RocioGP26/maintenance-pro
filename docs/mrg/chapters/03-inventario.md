# MRG-03-INV · Inventario

**Código:** MRG-03-INV · Sprint 10.3 · **Entregado**

> El módulo **Inventario** gestiona el catálogo comercial, stock, movimientos, alertas de mínimo y valorización — base para compras y ventas del tenant.

---

## Objetivo del capítulo

Documentar el inventario **comercial** de Roustix: productos, stock, kardex implícito y distinción con repuestos técnicos de Mantenimiento.

**Clave de módulo:** `inventario` · **Área producto:** `/comercial` · **Estado producto:** ✅ Producción · **Sprint 14 ALIGN:** ✅ Cerrado (2026-07-10)

| Estado | Significado |
|--------|-------------|
| ✅ Producción | Implementado y alineado con este manual |
| 🟡 Parcial | Implementado · gaps menores documentados |
| 📋 Roadmap | Documentado · no implementado |

→ Auditoría Sprint 14: [ALIGN · Fase 2](../../alignment/modules/03-inventario-audit.md)

### Matriz de implementación (Sprint 14)

| Sección | Tema | Estado |
|---------|------|--------|
| §1 | Alcance | ✅ |
| §2 | Entidades | ✅ |
| §3 | Stock y kardex | 🟡 |
| §4 | Catálogo | ✅ |
| §5 | Valorización | 🟡 |
| §6 | Distinción vs Mantenimiento | ✅ |
| API | MAG `/api/v1/inventory/*` | 📋 |

**Gaps abiertos (📋):** kardex dedicado · ajuste manual stock · API inventory · rotación BI.

---

## 1 · Alcance · ✅

| Incluye | No incluye |
|---------|------------|
| Catálogo de productos (SKU) | Repuestos técnicos de OT (→ MRG-02) |
| Stock y ubicación en bodega | Contabilidad de costos avanzada |
| Alertas de stock mínimo | MRP / producción |
| Import/export Excel | Purchasing unificado (→ MRG-04 roadmap doc) |
| Valorización de inventario | |

**Hoy en producto:** módulo activo con `@require_module(inventario)` · tenants solo-inventario redirigen dashboard a `/comercial/dashboard`.

---

## 2 · Entidades principales · ✅

| Entidad | Descripción | Modelo |
|---------|-------------|--------|
| **Producto** | SKU, nombre, precios, stock actual, stock mínimo | `InvProducto` |
| **Ubicación** | Pasillo, estante o zona en bodega | campo `ubicacion` |
| **Movimiento** | Entrada (compra) o salida (venta) | `InvCompra` / `InvVenta` |
| **Stock mínimo** | Umbral para alerta de reposición | `stock_minimo` |

---

## 3 · Stock y kardex · 🟡

Roustix no expone hoy una pantalla «kardex» dedicada, pero el **historial de movimientos** se reconstruye desde:

| Origen | Efecto en stock |
|--------|-----------------|
| Compra registrada | **Entrada** — aumenta stock y actualiza costo |
| Venta registrada | **Salida** — disminuye stock |
| Ajuste manual | 📋 Futuro / operación administrativa |

**Regla de negocio:** no se puede vender más unidades de las disponibles — validado en registro de venta.

**Hoy en producto:** stock inicial opcional al crear producto; lo habitual es entrada en Compras (MRG-04).

---

## 4 · Catálogo · ✅

### Operaciones

- Alta, edición y baja lógica de productos ✅
- Precio de venta y costo (desde última compra) ✅
- Multimoneda cuando el tenant la tiene activa ✅
- **Importación masiva** desde Excel ✅
- **Exportación** de catálogo y productos bajo stock ✅

### Alertas

Dashboard y listados destacan productos **bajo stock mínimo** para acción de compra.

**Hoy en producto:** filtro `?alerta=bajo` · badge en fila · export Excel bajo stock · alertas en campana header.

---

## 5 · Valorización · 🟡

| Indicador | Cálculo funcional | Estado |
|-----------|-------------------|--------|
| Valor inventario | Suma (stock × costo) por producto | ✅ dashboard |
| Productos activos | SKUs activos en catálogo | ✅ |
| Rotación | Análisis futuro (Sales Pro / BI) | 📋 |

---

## 6 · Distinción Mantenimiento vs Inventario · ✅

| | Repuesto técnico | Producto comercial |
|---|------------------|-------------------|
| Módulo | Mantenimiento (`mantenimiento`) | Inventario (`inventario`) |
| Uso | OT y mantenimiento | Venta al cliente final |
| Entidad | `SparePart` | `InvProducto` |
| Ruta | `/inventario` | `/comercial/productos` |
| Proveedor | Proveedor servicio | `InvProveedor` |
| Nav | **Repuestos técnicos** | **Productos** |

**No hay vínculo automático** entre ambos inventarios hoy.

---

## Relación

| Capítulo | Relación |
|----------|----------|
| MRG-02 | Repuestos técnicos · separados |
| MRG-04 | Compras incrementan stock |
| MRG-05 | Ventas decrementan stock |
| MRG-08 | Dashboard comercial · export Excel |

---

## Exit criteria · Sprint 14 Fase 2

- [x] Auditoría catálogo · stock · alertas · Excel
- [x] Distinción repuestos vs productos documentada
- [x] Nav alineado MRG §6
- [x] Alineación UI/copy/menús vs producto (Sprint 14 · Fase 2)
- [ ] Validación implementadores
- [ ] API MAG inventory

**Cobertura documental:** ✅ · **Implementación web:** ✅ · **API:** 📋

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Módulo producto** | ✅ Producción (web) |
| **Sprint 14 ALIGN** | ✅ Cerrado 2026-07-10 |
| **Cobertura documental** | ✅ v1.0.1 |
| **API MAG** | 📋 Pendiente |
| **MRG capítulo** | v1.0.1 |
| **Próximo paso** | Fase 3 · MRG-04 Compras ([ALIGN](../../alignment/)) |

---

→ [MRG-04 · Compras](04-compras.md) · [MRG-02 · Mantenimiento](02-maintenance.md) · [Índice MRG](/mrg/)
