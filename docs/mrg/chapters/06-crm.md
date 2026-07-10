# MRG-06-CRM · CRM

**Código:** MRG-06-CRM · Sprint 10.6 · **Entregado (parcial)**

> El módulo **CRM** (Customer Relationship Management) centralizará la gestión comercial de clientes, contactos, oportunidades y actividades — convirtiéndose en el **punto de partida** del proceso comercial de Maintix.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Documentar el alcance funcional del módulo CRM de Maintix, describiendo el **estado actual**, la **evolución prevista** y su integración con Sales, Inventory y futuros módulos comerciales.

Actualmente Maintix dispone del **maestro de clientes** utilizado por Inventory y Sales. El CRM ampliará esta información para administrar todo el ciclo comercial.

**Estado:** 📋 **Módulo CRM en roadmap** · 🟡 **Maestro de clientes operativo en Inventory**

---

## 1 · Alcance

| Incluye (objetivo) | No incluye |
|--------------------|------------|
| Gestión de clientes | Facturación |
| Contactos | Servicio postventa |
| Oportunidades comerciales | Marketing Automation |
| Actividades comerciales | Help Desk |
| Pipeline de ventas | Gestión documental avanzada |
| Cotizaciones | ERP financiero |

---

## 2 · Estado actual vs objetivo

| Capacidad | Hoy | CRM objetivo |
|-----------|-----|--------------|
| Clientes | ✅ Maestro de clientes | ✅ Completo |
| Contactos | 🟡 Información básica | ✅ Múltiples contactos |
| Historial comercial | 🟡 Ventas realizadas | ✅ Completo |
| Oportunidades | ❌ | ✅ |
| Pipeline | ❌ | ✅ |
| Actividades | ❌ | ✅ |
| Cotizaciones | ❌ | ✅ |
| Integración Sales | 🟡 Cliente en POS | ✅ Flujo completo |

### Correspondencia hoy (Inventory / Sales)

| Capacidad | Implementación actual |
|-----------|----------------------|
| Cliente / cuenta | `InvCliente` — nombre, documento, teléfono, email, dirección |
| Historial comercial | Ventas (`InvVenta`) vinculadas al cliente |
| Saldo pendiente | Agregado desde ventas a crédito |
| Contactos múltiples | 📋 Roadmap |
| Oportunidades · pipeline | 📋 Roadmap |

→ [MRG-05 · Ventas](05-ventas.md)

---

## 3 · Entidades principales

| Entidad | Descripción |
|---------|-------------|
| **Cuenta (Cliente)** | Empresa o persona que mantiene relación comercial |
| **Contacto** | Persona perteneciente a una cuenta |
| **Oportunidad** | Posible negocio en seguimiento |
| **Actividad** | Llamada, reunión, visita o tarea |
| **Cotización** | Oferta comercial enviada |
| **Pipeline** | Flujo comercial configurable |

---

## 4 · Pipeline comercial

El proceso comercial seguirá una secuencia **configurable**:

```
Lead
    │
    ▼
Prospección
    │
    ▼
Calificación
    │
    ▼
Propuesta
    │
    ▼
Negociación
    │
    ├────────► Ganada
    │              │
    │              ▼
    │          Venta
    │
    └────────► Perdida
```

Cada empresa podrá **adaptar las etapas** a su proceso comercial.

> **Hoy:** el vendedor registra la venta directamente en POS con cliente del maestro — sin etapas intermedias de pipeline.

---

## 5 · Clientes y cuentas

El cliente será el **eje central** del CRM.

Cada cuenta podrá almacenar:

- información general
- contactos asociados
- historial comercial
- oportunidades abiertas
- ventas realizadas
- actividades programadas
- documentos relacionados

Una cuenta podrá tener **múltiples contactos**.

> **Hoy:** ficha única por `InvCliente` · historial vía ventas vinculadas · sin oportunidades ni actividades.

---

## 6 · Actividades comerciales

El CRM permitirá registrar todas las **interacciones** con el cliente.

**Ejemplos:**

- llamadas
- reuniones
- visitas
- correos
- tareas
- seguimientos

Cada actividad tendrá:

| Atributo | Uso |
|----------|-----|
| Responsable | Usuario o vendedor asignado |
| Fecha | Programada o realizada |
| Estado | Pendiente · completada · cancelada |
| Observaciones | Detalle de la interacción |

---

## 7 · Integración con Sales

El CRM será la **etapa previa** al proceso de venta:

```
Lead
      │
      ▼
Oportunidad
      │
      ▼
Cotización
      │
      ▼
Venta
      │
      ▼
Cliente activo
```

Las oportunidades **ganadas** podrán convertirse directamente en ventas.

→ [MRG-05 · Ventas](05-ventas.md) · [MRG-09 · Workflows](09-workflows.md)

---

## 8 · Integración con Inventory

El CRM **no administra productos**, pero utiliza el catálogo comercial para:

- generar cotizaciones
- consultar disponibilidad
- calcular valores
- preparar pedidos

**Inventory** continúa siendo el responsable del stock.

→ [MRG-03 · Inventario](03-inventario.md)

---

## 9 · Indicadores comerciales

| KPI | Descripción |
|-----|-------------|
| Oportunidades abiertas | Negocios en curso |
| Valor del pipeline | Monto potencial |
| Conversión | Oportunidades ganadas |
| Tiempo promedio de cierre | Ciclo comercial |
| Actividades pendientes | Seguimientos |
| Clientes activos | Base comercial |

Estos indicadores alimentarán el **Dashboard Comercial**.

→ [MRG-08 · Reportes](08-reportes.md)

> **Hoy:** KPIs limitados a ventas del período y cartera en dashboard Inventory — pipeline CRM en roadmap.

---

## 10 · Evolución prevista

| Funcionalidad | Estado |
|---------------|--------|
| Maestro de clientes | ✅ |
| Contactos múltiples | 📋 |
| Pipeline configurable | 📋 |
| Actividades | 📋 |
| Cotizaciones | 📋 |
| Agenda comercial | 📋 |
| Integración Sales | 📋 |
| Dashboard comercial | 📋 |

→ [MPA-05 · Roadmap módulos](/mpa/chapters/05-roadmap-modulos.md) · [MUX · Personas](/mux/personas.md) (PER-008 Cliente)

---

## 11 · Integración con otros módulos

```
CRM
 │
 ├────────► Sales
 │
 ├────────► Inventory
 │
 ├────────► Reports
 │
 └────────► Analytics (roadmap)
```

El CRM será el **origen** de toda la actividad comercial.

| Módulo | Relación |
|--------|----------|
| Sales | Oportunidad ganada → venta |
| Inventory | Catálogo en cotizaciones |
| Reports | KPIs comerciales |
| Finance | 📋 Roadmap |
| [MAG](/mag/) | Recursos `/api/v1/crm/*` (objetivo) |

---

## 12 · Buenas prácticas

| # | Recomendación |
|---|---------------|
| 1 | Mantener actualizada la información de cada cliente |
| 2 | Registrar todas las actividades comerciales |
| 3 | Actualizar el estado de cada oportunidad |
| 4 | Evitar oportunidades duplicadas |
| 5 | Utilizar cotizaciones vinculadas al CRM |
| 6 | Revisar periódicamente el pipeline comercial |

> **Hoy (pre-CRM):** mantener maestro `InvCliente` limpio y vincular ventas a crédito siempre a un cliente identificado.

---

## Relación con otros capítulos

| Capítulo | Relación |
|----------|----------|
| [MRG-05 · Ventas](05-ventas.md) | Conversión de oportunidades en ventas |
| [MRG-03 · Inventario](03-inventario.md) | Productos en cotizaciones |
| [MRG-08 · Reportes](08-reportes.md) | Indicadores comerciales |
| [MRG-09 · Workflows](09-workflows.md) | Lead → Oportunidad → Venta |
| [MCM · Propuesta de valor](/mcm/chapters/02-propuesta-de-valor.md) | Posicionamiento comercial |

---

## Exit Criteria

Este capítulo se considera **implementado (documentación)** cuando:

- [x] Alcance CRM objetivo documentado
- [x] Estado actual vs objetivo definido
- [x] Pipeline · entidades · integraciones descritas
- [x] Indicadores y evolución prevista documentados
- [ ] Existe un módulo CRM funcional en producto
- [ ] Cuentas y contactos múltiples operativos
- [ ] Pipeline configurable implementado
- [ ] Integración oportunidades → ventas
- [ ] Indicadores comerciales CRM en dashboard

**Cobertura documental:** parcial — especificación funcional + maestro clientes hoy.

---

## Filosofía del capítulo

El CRM no consiste únicamente en almacenar clientes. Su objetivo es convertir las **relaciones comerciales** en procesos **medibles y trazables**, permitiendo conocer el estado de cada oportunidad desde el primer contacto hasta la venta. Maintix integra este proceso con el resto de la plataforma para ofrecer una visión completa del ciclo comercial.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Módulo** | 📋 Roadmap |
| **Estado actual** | 🟡 Maestro de clientes en Inventory |
| **Integración futura** | Sales · Inventory · Reportes |
| **MRG** | v0.1.0 |
| **Siguiente capítulo** | MRG-07-ADMIN · Administración |

---

→ [MRG-07 · Administración](07-administracion.md) · [MRG-05 · Ventas](05-ventas.md) · [Índice MRG](/mrg/)
