# MRG-04-PUR · Compras

**Código:** MRG-04-PUR · Sprint 16.5 · **Purchasing operativo**

> El módulo **Purchasing** administra el abastecimiento de productos y servicios mediante solicitudes, órdenes de compra, recepción de mercancía y proveedores — garantizando la disponibilidad de inventario y la trazabilidad de las adquisiciones.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Documentar el funcionamiento funcional del módulo **Purchasing**, responsable del ciclo completo de adquisición de bienes y servicios para la empresa.

Purchasing opera el ciclo solicitud → aprobación → OC → recepción → CxP. Inventory conserva los maestros de productos/proveedores, el stock y las obligaciones/pagos compatibles.

**Estado:** ✅ **Sprint 16 completo** · compatibilidad legacy activa

| Estado | Significado |
|--------|-------------|
| ✅ Producción | Implementado y alineado con subflujo documentado |
| 🟡 Parcial | Subflujo OK · modelo Purchasing completo en roadmap |
| 📋 Roadmap | Documentado · no implementado |

→ Auditoría Sprint 14: [ALIGN · Fase 3](../../alignment/modules/04-compras-audit.md)

### Matriz de implementación (Sprint 14)

| Sección | Tema | Estado |
|---------|------|--------|
| §1 | Alcance | ✅ |
| §2 | Entidades | ✅ |
| §3 | Flujo de compra | ✅ |
| §4 | Proveedores | ✅ |
| §5 | Órdenes de compra | ✅ |
| §5 · CxP | Cuentas por pagar | ✅ |
| §6 | Recepción | ✅ |
| §7 | Relación Inventory | ✅ |
| §8 | Relación Maintenance | ✅ |
| §9 | Indicadores | ✅ |
| §10–§12 | Integración · casos · buenas prácticas | ✅ doc |
| API | MAG `/api/v1/purchasing/*` | 📋 |

**Gap abierto:** API MAG Purchasing continúa planificada; UI, modelos, MRL y migración están operativos.

---

## 1 · Alcance · 🟡

| Incluye | No incluye (hoy) |
|---------|------------------|
| Proveedores comerciales | Contabilidad financiera |
| Solicitudes de compra | Presupuesto empresarial |
| Órdenes de compra | Tesorería |
| Recepción de mercancía | Facturación electrónica |
| Actualización de stock | Gestión contractual avanzada |
| Cuentas por pagar (CxP) | |

> **Hoy:** Purchasing formal está operativo. Las entradas directas permanecen visibles como compatibilidad legacy durante la transición.

---

## 2 · Entidades principales · 🟡

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
| Solicitud | `PurSolicitud` · `PurSolicitudLinea` |
| Orden de compra | `PurOrdenCompra` · `PurOrdenLinea` |
| Recepción parcial | `PurRecepcion` · `PurRecepcionLinea` |

---

## 3 · Flujo de compra · 🟡

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

## 4 · Proveedores · ✅

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

## 5 · Órdenes de compra · 🟡

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

### Cuentas por pagar (CxP) · ✅

Pantalla operativa para **obligaciones con proveedores** derivadas de compras a crédito — no es un módulo aparte, sino la vista de tesorería sobre `InvCompra` con saldo pendiente.

| Función | Ruta / comportamiento |
|---------|----------------------|
| Listado CxP | `/comercial/cuentas-por-pagar` |
| KPIs | Saldo total · por vencer (7 d.) · vencidas |
| Filtros | Por proveedor · alerta vencimiento |
| Registrar pago | Modal · parcial o total · `InvCompraPago` |
| Enlace compra | Desde factura → detalle de entrada |
| Nav | Submenú bajo **Compras** → Cuentas por pagar |

**Estados de pago:** Pendiente · Abono parcial · Pagada · alerta **Vencida** (fecha límite superada).

**Hoy en producto:** alertas en dashboard inventario · campana header · filtros en listado de compras · pagos AJAX desde CxP y detalle de compra.

---

## 6 · Recepción de mercancía · 🟡

Cuando llega una compra, Roustix registra la recepción.

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

## 7 · Relación con Inventory · ✅

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

## 8 · Relación con Maintenance · ✅

Actualmente existen **dos tipos de adquisiciones**:

| Tipo | Destino |
|------|---------|
| Compra comercial | Inventory |
| Compra de repuestos técnicos | Maintenance |

En la hoja de ruta ambas utilizarán el mismo módulo **Purchasing**, diferenciándose únicamente por el **destino del inventario** (comercial vs técnico).

→ [MRG-02 · Maintenance](02-maintenance.md) · [MPA-05 · Roadmap módulos](/mpa/chapters/05-roadmap-modulos.md)

---

## 9 · Indicadores · 🟡

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
- [x] Alineación UI/copy/menús vs producto (Sprint 14 · Fase 3)
- [ ] Validación con operación comercial real
- [ ] Alineación MAG Purchasing v1

**Cobertura documental:** parcial — modelo objetivo + subflujo Inventory.

---

## Filosofía del capítulo

Comprar no consiste únicamente en adquirir productos. Significa garantizar que la operación disponga de los recursos correctos, en el momento adecuado y con **trazabilidad completa**. Roustix convierte cada compra en un proceso controlado, medible e integrado con el resto de la plataforma.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Módulo Purchasing** | 📋 Roadmap |
| **Subflujo Inventory** | 🟡 Parcial · operativo |
| **Sprint 14 ALIGN** | ✅ Cerrado 2026-07-10 |
| **MRG capítulo** | v1.0.2 |
| **Próximo paso** | Fase 4 · MRG-05 Ventas ([ALIGN](../../alignment/)) |

---

→ [MRG-05 · Ventas](05-ventas.md) · [MRG-03 · Inventario](03-inventario.md) · [Índice MRG](/mrg/)
