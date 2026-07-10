# MRG-05-SALES · Ventas

**Código:** MRG-05-SALES · Sprint 10.5 · **Entregado (parcial)**

> El módulo **Sales** administra el ciclo comercial de ventas mediante punto de venta (POS), clientes, documentos de venta, control de inventario y gestión de cobros — proporcionando trazabilidad desde la salida del producto hasta el recaudo.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Documentar el funcionamiento funcional del proceso de ventas de Maintix, incluyendo ventas de contado y crédito, administración de clientes, movimientos de inventario y evolución hacia **Sales Pro**.

Actualmente las ventas forman parte del módulo **Inventory** y evolucionarán hacia un módulo independiente altamente integrado.

**Estado:** 🟡 **Operativo dentro de Inventory** · **Sprint 14 ALIGN:** ✅ Cerrado (2026-07-10) · Sales Pro 📋 **Roadmap**

| Estado | Significado |
|--------|-------------|
| ✅ Producción | Implementado y alineado con subflujo documentado |
| 🟡 Parcial | Núcleo OK · Sales Pro / API en roadmap |
| 📋 Roadmap | Documentado · no implementado |

→ Auditoría Sprint 14: [ALIGN · Fase 4](../../alignment/modules/05-ventas-audit.md)

### Matriz de implementación (Sprint 14)

| Sección | Tema | Estado |
|---------|------|--------|
| §1 | Alcance | 🟡 |
| §2 | Entidades | ✅ |
| §3 | Flujo de venta | ✅ |
| §4 | POS | ✅ |
| §5 | Estados venta / cobro | 🟡 |
| §6 | Ventas a crédito · cartera | ✅ |
| §7 | Clientes | ✅ |
| §8 | Relación Inventory | ✅ |
| §9 | Sales Pro | 📋 |
| §10 | Indicadores | 🟡 |
| API | MAG `/api/v1/sales/*` | 📋 |

**Gaps abiertos (📋):** borrador/anulación · CxC dedicada · Sales Pro · API.

---

## 1 · Alcance · 🟡

| Incluye | No incluye (hoy) |
|---------|------------------|
| Punto de venta (POS) | CRM completo (→ MRG-06) |
| Ventas de contado | Facturación electrónica |
| Ventas a crédito | Cuentas por cobrar avanzadas |
| Abonos | Comisiones |
| Clientes | Gestión de campañas |
| Descuento automático de stock | Programas de fidelización |

---

## 2 · Entidades principales · ✅

| Entidad | Descripción |
|---------|-------------|
| **Cliente** | Persona o empresa que adquiere productos |
| **Venta** | Documento comercial generado por el POS |
| **Detalle de venta** | Productos vendidos |
| **Cobro** | Pago total o parcial de una venta |
| **Forma de pago** | Contado o crédito |
| **Saldo pendiente** | Valor aún por recaudar |

### Correspondencia hoy (Inventory)

| Entidad MRG | Implementación actual |
|-------------|----------------------|
| Cliente | `InvCliente` |
| Venta | `InvVenta` |
| Detalle de venta | `InvVentaLinea` |
| Cobro | `InvVentaCobro` |
| Forma de pago | `contado` · `credito` |
| Saldo pendiente | `total − monto_cobrado` · `estado_cobro` |

---

## 3 · Flujo de venta · ✅

```
Cliente
      │
      ▼
Selección de productos
      │
      ▼
Confirmación
      │
      ▼
Venta registrada
      │
      ├────────► Stock disminuye
      ├────────► Movimiento inventario
      ├────────► Historial cliente
      └────────► Cobro / saldo pendiente
```

Todo el proceso queda registrado para **auditoría**.

### Validaciones operativas

- Crédito **requiere cliente** identificado
- No se vende por encima del **stock disponible** (salvo configuración futura)
- Precio unitario desde catálogo o captura manual en POS

---

## 4 · Punto de venta (POS) · ✅

El POS permite realizar ventas de forma rápida.

**Proceso típico:**

1. Seleccionar cliente (opcional para ventas de mostrador)
2. Buscar productos
3. Agregar cantidades
4. Aplicar descuentos autorizados
5. Confirmar venta
6. Registrar forma de pago
7. Imprimir o enviar comprobante

> **Hoy:** formulario POS en `/comercial/ventas` · comprobante vía detalle de venta · impresión/PDF según evolución MRL.

---

## 5 · Estados de una venta · 🟡

### Modelo funcional (Sales)

| Estado | Significado |
|--------|-------------|
| **Borrador** | Venta en preparación |
| **Confirmada** | Venta registrada |
| **Parcialmente pagada** | Existen abonos |
| **Pagada** | Saldo cancelado |
| **Anulada** | Venta cancelada |

### Estados de cobro (hoy · Inventory)

| Estado | Significado |
|--------|-------------|
| **Pagada** | Cobro total registrado (contado o crédito liquidado) |
| **Pendiente** | Crédito sin abonos |
| **Parcial** | Abonos parciales · saldo pendiente |

> **Hoy:** al confirmar en POS la venta queda **confirmada** implícitamente. Estados `borrador` y `anulada` — roadmap Sales Pro. El control de cobro usa `estado_cobro`.

---

## 6 · Ventas a crédito · ✅

Cuando la forma de pago es **crédito**, Maintix registra automáticamente la obligación pendiente.

Cada venta puede tener:

| Campo | Uso |
|-------|-----|
| Valor total | Monto de la venta |
| Saldo pendiente | Total − monto cobrado |
| Historial de pagos | `InvVentaCobro` |
| Fecha de vencimiento | Plazo acordado con el cliente |
| Observaciones | Notas en venta o en cada cobro |

Los **abonos** reducen el saldo hasta completar el pago.

### Cartera por cobrar (cartera ligera) · ✅

Sin módulo **CxC** dedicado — equivalente operativo a CxP en Compras (MRG-04):

| Función | Ruta / comportamiento |
|---------|----------------------|
| Listado ventas | `/comercial/ventas` |
| Filtro por cobrar | `?cobro=pendiente` |
| Abonos | Detalle venta · `InvVentaCobro` |
| Nav | Submenú **Ventas** → Por cobrar |
| KPI | Ventas del día en dashboard |

**Estados de cobro:** Pagada · Pendiente · Abono parcial.

**Hoy en producto:** filas warning en listado · abono desde detalle · crédito exige cliente.

---

## 7 · Clientes · ✅

El maestro de clientes constituye la **base comercial** del tenant.

Cada cliente puede almacenar:

- identificación
- nombre
- dirección
- teléfonos
- correo electrónico
- historial de compras (ventas vinculadas)
- saldo pendiente (agregado desde ventas a crédito)
- última compra

Este catálogo evolucionará posteriormente hacia **CRM** — pipeline, contactos y oportunidades (→ [MRG-06 · CRM](06-crm.md)).

---

## 8 · Relación con Inventory · ✅

Cada venta genera automáticamente:

- **salida de inventario**
- **movimiento de stock** (decremento por línea)
- **actualización de existencias**
- **actualización de indicadores comerciales** (dashboard)

No es posible vender cantidades superiores al stock disponible, salvo configuración futura.

```
Inventory (stock)
      │
      ▼
Sales (POS)
      │
      ▼
Stock actualizado · KPIs comerciales
```

→ [MRG-03 · Inventario](03-inventario.md)

---

## 9 · Evolución Sales Pro · 📋

Sales Pro ampliará significativamente las capacidades actuales:

| Funcionalidad | Estado |
|---------------|--------|
| POS | ✅ |
| Crédito | ✅ |
| Abonos | ✅ |
| Listas de precios | 📋 |
| Promociones | 📋 |
| Cotizaciones | 📋 |
| Pedidos | 📋 |
| Vendedores | 📋 |
| Comisiones | 📋 |
| Facturación electrónica | 📋 |
| Integración CRM | 📋 |

---

## 10 · Indicadores · 🟡

| KPI | Descripción |
|-----|-------------|
| Ventas del período | Valor total vendido |
| Ticket promedio | Venta promedio |
| Productos más vendidos | Ranking |
| Clientes frecuentes | Compradores recurrentes |
| Cartera pendiente | Ventas a crédito abiertas |
| Rotación de inventario | Relación ventas / stock |

Los indicadores alimentan el **tablero comercial** y ejecutivo.

→ [MRG-08 · Reportes](08-reportes.md)

> **Hoy:** ventas del día en dashboard comercial · filtro cobros pendientes · exportaciones de catálogo. Ticket promedio, ranking y rotación — parcial o roadmap Analytics.

---

## 11 · Integración con otros módulos

```
Inventory
      │
      ▼
Sales
      │
      ├────────► Clientes
      ├────────► Dashboard
      ├────────► Reportes
      ├────────► CRM (roadmap)
      └────────► Finanzas (roadmap)
```

Sales representa el **punto de salida** de productos del inventario.

| Módulo | Relación |
|--------|----------|
| [MRG-04 · Compras](04-compras.md) | Reposición de stock vendido |
| [MRG-06 · CRM](06-crm.md) | Evolución del maestro de clientes |
| [MRG-09 · Workflows](09-workflows.md) | Compra → inventario → venta → cobro |
| [MAG](/mag/) | Futuros recursos `/api/v1/sales/*` |

---

## 12 · Buenas prácticas

| # | Recomendación |
|---|---------------|
| 1 | Registrar siempre el cliente cuando sea posible |
| 2 | Evitar modificar ventas confirmadas |
| 3 | Registrar inmediatamente los abonos |
| 4 | Mantener actualizado el catálogo de productos |
| 5 | Revisar diariamente ventas pendientes de cobro |
| 6 | Utilizar reportes para controlar la rotación de inventario |

---

## Relación con otros capítulos

| Capítulo | Relación |
|----------|----------|
| [MRG-03 · Inventario](03-inventario.md) | Productos y control de stock |
| [MRG-04 · Compras](04-compras.md) | Reposición de inventario |
| [MRG-06 · CRM](06-crm.md) | Evolución de clientes hacia oportunidades |
| [MRG-08 · Reportes](08-reportes.md) | Indicadores comerciales |
| [MRG-09 · Workflows](09-workflows.md) | Compra → Inventario → Venta → Cobro |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] Proceso completo de venta documentado
- [x] Ventas de contado y crédito descritas
- [x] Descuento automático de inventario documentado
- [x] Indicadores comerciales definidos
- [x] Evolución hacia Sales Pro documentada
- [x] Alineación UI/copy/menús vs producto (Sprint 14 · Fase 4)
- [ ] Validación con operación comercial real
- [ ] Alineación MAG Sales v1

**Cobertura documental:** parcial — núcleo operativo en Inventory + roadmap Sales Pro.

---

## Filosofía del capítulo

Vender no consiste únicamente en registrar una salida de inventario. Cada venta representa una **relación con el cliente**, una **actualización del inventario** y una **fuente de información** para la toma de decisiones. Maintix integra estos procesos para ofrecer una operación comercial trazable, consistente y preparada para evolucionar hacia un ecosistema completo de gestión empresarial.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Módulo Sales** | 🟡 Parcial · operativo |
| **Sales Pro** | 📋 Roadmap |
| **Sprint 14 ALIGN** | ✅ Cerrado 2026-07-10 |
| **MRG capítulo** | v1.0.1 |
| **Próximo paso** | Fase 5 · MRG-06 CRM ([ALIGN](../../alignment/)) |

---

→ [MRG-06 · CRM](06-crm.md) · [MRG-04 · Compras](04-compras.md) · [Índice MRG](/mrg/)
