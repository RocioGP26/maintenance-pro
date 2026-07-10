# MRG-03-INV · Inventario

**Código:** MRG-03-INV · Sprint 10.3 · **Planificado**

> El módulo **Inventario** gestiona el catálogo comercial, stock, movimientos, alertas de mínimo y valorización — base para compras y ventas del tenant.

---

## Objetivo del capítulo

Documentar el inventario **comercial** de Maintix: productos, stock, kardex implícito y distinción con repuestos técnicos de Mantenimiento.

**Estado:** ✅ **Producción** · clave `inventario` · área `/comercial`

---

## 1 · Alcance

| Incluye | No incluye |
|---------|------------|
| Catálogo de productos (SKU) | Repuestos técnicos de OT (→ MRG-02) |
| Stock y ubicación en bodega | Contabilidad de costos avanzada |
| Alertas de stock mínimo | MRP / producción |
| Import/export Excel | Purchasing unificado (roadmap) |
| Valorización de inventario | |

---

## 2 · Entidades principales

| Entidad | Descripción |
|---------|-------------|
| **Producto** | SKU, nombre, precios, stock actual, stock mínimo |
| **Ubicación** | Pasillo, estante o zona en bodega |
| **Movimiento** | Entrada (compra) o salida (venta) — implícito en transacciones |
| **Stock mínimo** | Umbral para alerta de reposición |

---

## 3 · Stock y kardex

Maintix no expone hoy una pantalla «kardex» dedicada, pero el **historial de movimientos** se reconstruye desde:

| Origen | Efecto en stock |
|--------|-----------------|
| Compra registrada | **Entrada** — aumenta stock y actualiza costo |
| Venta registrada | **Salida** — disminuye stock |
| Ajuste manual | Futuro / operación administrativa |

**Regla de negocio:** no se puede vender más unidades de las disponibles (salvo configuración futura de negativo).

---

## 4 · Catálogo

### Operaciones

- Alta, edición y baja lógica de productos
- Precio de venta y costo (desde última compra)
- Multimoneda cuando el tenant la tiene activa
- **Importación masiva** desde Excel
- **Exportación** de catálogo y productos bajo stock

### Alertas

Dashboard y listados destacan productos **bajo stock mínimo** para acción de compra.

---

## 5 · Valorización

| Indicador | Cálculo funcional |
|-----------|-------------------|
| Valor inventario | Suma (stock × costo) por producto |
| Productos activos | SKUs con movimiento o stock > 0 |
| Rotación | Análisis futuro (Sales Pro / BI) |

---

## 6 · Distinción Mantenimiento vs Inventario

| | Repuesto técnico | Producto comercial |
|---|------------------|-------------------|
| Módulo | Mantenimiento | Inventario |
| Uso | OT y mantenimiento | Venta al cliente final |
| Entidad | SparePart | InvProducto |
| Proveedor | Proveedor servicio | InvProveedor |

**No hay vínculo automático** entre ambos inventarios hoy.

---

## Relación

| Capítulo | Relación |
|----------|----------|
| MRG-04 | Compras incrementan stock |
| MRG-05 | Ventas decrementan stock |
| MRG-08 | Dashboard comercial · export Excel |

---

→ [MRG-04 · Compras](04-compras.md) · [MRG-02 · Mantenimiento](02-maintenance.md)
