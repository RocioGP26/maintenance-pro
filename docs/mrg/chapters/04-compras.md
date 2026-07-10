# MRG-04-PUR · Compras

**Código:** MRG-04-PUR · Sprint 10.4 · **Entregado (parcial)**

> El módulo **Purchasing** administra el abastecimiento de productos y servicios mediante solicitudes, órdenes de compra, recepción de mercancía y proveedores — garantizando la disponibilidad de inventario y la trazabilidad de las adquisiciones.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Documentar el funcionamiento funcional del módulo **Purchasing**, responsable del ciclo completo de adquisición de bienes y servicios para la empresa.

Actualmente **parte del proceso se realiza desde el módulo Inventory**. En futuras versiones evolucionará hacia un módulo independiente completamente integrado con inventario, cuentas por pagar y analítica.

**Estado:** 📋 **Módulo Purchasing en roadmap** · 🟡 **Subflujo operativo en Inventory** (compras comerciales + CxP)

---

## 1 · Alcance

| Incluye | No incluye (hoy) |
|---------|------------------|
| Proveedores comerciales | Contabilidad financiera |
| Solicitudes de compra | Presupuesto empresarial |
| Órdenes de compra | Tesorería |
| Recepción de mercancía | Facturación electrónica |
| Actualización de stock | Gestión contractual avanzada |
| Cuentas por pagar (CxP) | |

> **Hoy en producto:** registro directo de **compra / entrada de mercancía**, proveedores comerciales, actualización de stock y CxP. Solicitudes, aprobaciones, OC formales y recepción parcial — **roadmap Purchasing**.

---

## 2 · Entidades principales

| Entidad | Descripción |
|---------|-------------|
| **Proveedor** | Empresa que suministra productos o servicios |
| **Solicitud de compra** | Necesidad interna pendiente de aprobación |
| **Orden de compra** | Documento enviado al proveedor |
| **Recepción** | Confirmación de mercancía recibida |
| **Detalle de compra** | Productos, cantidades y costos |
| **Condición de pago** | Contado, crédito o acuerdos comerciales |
| **Pago de compra** | Abono o liquidación sobre CxP |

### Correspondencia hoy (Inventory)

| Entidad MRG | Implementación actual |
|-------------|----------------------|
| Proveedor | `InvProveedor` |
| Orden / compra registrada | `InvCompra` |
| Detalle de compra | `InvCompraLinea` |
| Condición de pago | Contado / crédito · `estado_pago` |
| Pago | `InvCompraPago` |
| Solicitud · recepción parcial | 📋 Roadmap |

---

## 3 · Flujo de compra

El proceso completo sigue una secuencia estándar:

```
Necesidad
      │
      ▼
Solicitud de compra
      │
      ▼
Aprobación
      │
      ▼
Orden de compra
      │
      ▼
Proveedor
      │
      ▼
Recepción
      │
      ▼
Actualización del inventario
      │
      ▼
Pendiente de pago
```

Cada etapa queda registrada para **auditoría y trazabilidad**.

### Flujo simplificado (hoy en Inventory)

```
Alerta bajo stock / necesidad
      │
      ▼
Seleccionar proveedor
      │
      ▼
Registrar compra (líneas + IVA + totales)
      │
      ├──► Stock incrementado
      ├──► Costo de producto actualizado
      └──► CxP (si crédito) o pagada (si contado)
```

---

## 4 · Proveedores

Cada proveedor dispone de información comercial propia:

| Información | Descripción |
|-------------|-------------|
| Razón social | Nombre del proveedor |
| Documento | NIT u otro identificador |
| Contactos | Personas responsables |
| Teléfono y correo | Información comercial |
| Condiciones de pago | Crédito, contado, días |
| Estado | Activo o inactivo |

Un mismo proveedor puede abastecer **múltiples productos**.

> **Distinción MRG:** proveedor **comercial** (Purchasing / Inventory) ≠ proveedor de **servicio** (Maintenance · OT externa) — ver [MRG-02 · Maintenance](02-maintenance.md).

---

## 5 · Órdenes de compra

Una orden de compra representa el **compromiso formal de adquisición**.

### Contenido

- proveedor
- fecha
- productos solicitados
- cantidades
- precio unitario
- impuestos
- observaciones
- estado

### Estados (modelo Purchasing)

| Estado | Significado |
|--------|-------------|
| **Borrador** | En elaboración |
| **Pendiente** | Enviada al proveedor |
| **Parcial** | Recibida parcialmente |
| **Completada** | Totalmente recibida |
| **Cancelada** | Anulada |

### Estados de pago (hoy · CxP)

| Estado | Significado |
|--------|-------------|
| **Pendiente** | Factura con saldo por pagar |
| **Parcial** | Pagos parciales registrados |
| **Pagada** | Saldo liquidado |
| **Vencida** | Fecha límite superada (alerta dashboard) |

> **Hoy:** al registrar la compra el stock se actualiza en el mismo acto (recepción **completa** implícita). Estados de OC formal y recepción parcial — roadmap.

---

## 6 · Recepción de mercancía

Cuando llega una compra, Maintix registra la recepción.

| Tipo | Descripción |
|------|-------------|
| **Completa** | Toda la orden fue recibida |
| **Parcial** | Solo algunos productos llegaron |
| **Rechazada** | Mercancía no aceptada |

La recepción:

- incrementa el stock
- actualiza el costo del producto
- registra el movimiento de inventario
- conserva historial de recepción

> **Hoy:** recepción **completa** al confirmar `InvCompra`. Parcial y rechazada — roadmap Purchasing.

---

## 7 · Relación con Inventory

Purchasing alimenta directamente el inventario comercial:

```
Proveedor
      │
      ▼
Orden de compra
      │
      ▼
Recepción
      │
      ▼
Inventory
      │
      ▼
Stock actualizado
```

Toda compra genera **movimientos positivos** de inventario.

→ [MRG-03 · Inventario](03-inventario.md)

---

## 8 · Relación con Maintenance

Actualmente existen **dos tipos de adquisiciones**:

| Tipo | Destino |
|------|---------|
| Compra comercial | Inventory |
| Compra de repuestos técnicos | Maintenance |

En la hoja de ruta ambas utilizarán el mismo módulo **Purchasing**, diferenciándose únicamente por el **destino del inventario** (comercial vs técnico).

→ [MRG-02 · Maintenance](02-maintenance.md) · [MPA-05 · Roadmap módulos](/mpa/chapters/05-roadmap-modulos.md)

---

## 9 · Indicadores

| KPI | Descripción |
|-----|-------------|
| Compras del período | Valor total adquirido |
| Órdenes abiertas | Pendientes de recepción |
| Recepciones pendientes | Mercancía por recibir |
| Tiempo promedio de entrega | Días desde orden hasta recepción |
| Compras por proveedor | Distribución de adquisiciones |
| Productos más comprados | Ranking del período |
| CxP pendientes / vencidas | Obligaciones con proveedores |

Los indicadores alimentan los paneles ejecutivos de [MRG-08 · Reportes](08-reportes.md).

> **Hoy:** compras del período, CxP y alertas vencidas en dashboard comercial. KPIs de entrega y ranking — parcial o roadmap.

---

## 10 · Integración con otros módulos

```
Purchasing
      │
      ├────────► Inventory
      │
      ├────────► Maintenance
      │
      ├────────► Reports
      │
      └────────► Analytics (roadmap)
```

Purchasing actúa como el **punto de entrada** de productos a la organización.

---

## 11 · Casos de uso

### Compra para inventario comercial

```
Proveedor
      │
      ▼
Orden de compra
      │
      ▼
Recepción
      │
      ▼
Producto disponible para venta
```

### Compra de repuestos (objetivo unificado)

```
Proveedor
      │
      ▼
Orden de compra
      │
      ▼
Recepción
      │
      ▼
Repuesto disponible para OT
```

→ Cadena completa en [MRG-09 · Workflows](09-workflows.md)

---

## 12 · Buenas prácticas

| # | Recomendación |
|---|---------------|
| 1 | Mantener actualizado el catálogo de proveedores |
| 2 | Registrar siempre la recepción antes de modificar el stock |
| 3 | Utilizar órdenes de compra para toda adquisición |
| 4 | Evitar ajustes manuales de inventario cuando exista una compra asociada |
| 5 | Revisar periódicamente proveedores con mayor volumen de compras |
| 6 | Registrar condiciones de pago para facilitar futuras integraciones financieras |

---

## Relación con otros capítulos

| Capítulo | Relación |
|----------|----------|
| [MRG-03 · Inventario](03-inventario.md) | La recepción incrementa el stock |
| [MRG-05 · Ventas](05-ventas.md) | Los productos adquiridos pueden comercializarse |
| [MRG-08 · Reportes](08-reportes.md) | Indicadores de abastecimiento |
| [MRG-09 · Workflows](09-workflows.md) | Proceso compra → inventario → venta |
| [MAG](/mag/) | Futuros recursos `/api/v1/purchasing/*` |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] Flujo de compras documentado (modelo completo + estado actual)
- [x] Proveedores, órdenes y recepciones definidos
- [x] Actualización de inventario documentada
- [x] Indicadores funcionales establecidos
- [x] Relación con Maintenance e Inventory documentada
- [ ] Validación con operación comercial real
- [ ] Alineación MAG Purchasing v1

**Cobertura documental:** parcial — modelo objetivo + subflujo Inventory.

---

## Filosofía del capítulo

Comprar no consiste únicamente en adquirir productos. Significa garantizar que la operación disponga de los recursos correctos, en el momento adecuado y con **trazabilidad completa**. Maintix convierte cada compra en un proceso controlado, medible e integrado con el resto de la plataforma.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Módulo** | 📋 Roadmap (Purchasing) |
| **Integración actual** | 🟡 Parcial (desde Inventory) |
| **Relación** | Inventory · Maintenance |
| **MRG** | v0.1.0 |
| **Siguiente capítulo** | MRG-05-SALES · Ventas |

---

→ [MRG-05 · Ventas](05-ventas.md) · [MRG-03 · Inventario](03-inventario.md) · [Índice MRG](/mrg/)
