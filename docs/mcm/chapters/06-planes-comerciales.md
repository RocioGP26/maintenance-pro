# MCM-06-PLAN · Planes comerciales

**Código:** MCM-06-PLAN · **Actualización:** 2026-07-29

**Oferta oficial:** Start · Business · Enterprise

**Frase de marca:** Toda la operación. Una sola plataforma.

> Los planes de Roustix son etapas de crecimiento dentro de la misma plataforma.

**Prerequisitos:** [MCM-01-POS](01-posicionamiento.md) · [MCM-03-ICP](03-icp-score.md) · [MCM-05-SECT](05-sectores.md)

---

## Filosofía comercial

La conversación no empieza preguntando qué funcionalidades quitar. Empieza identificando qué necesita la operación para avanzar hoy y cuál será su siguiente etapa.

| Plan | Enfoque | Perfil ideal | Resultado esperado |
|------|---------|--------------|--------------------|
| **Start** | Digitalizar el proceso prioritario | Empresa que reemplaza Excel, WhatsApp o cuadernos | Operación inicial digitalizada en menos de una semana |
| **Business** | Integrar procesos, equipos y sedes | Empresa que ya digitalizó una parte | Maintenance e Inventory operando en una plataforma |
| **Enterprise** | Gobernanza, escala y personalización | Organización con procesos complejos | Roustix como plataforma central de operación |

```
Start  →  Business  →  Enterprise
```

**Regla de venta:** el perfil operativo sugiere el plan inicial. El precio confirma el alcance; no sustituye el diagnóstico.

---

## Matriz oficial

| Dimensión | Start | Business | Enterprise |
|-----------|-------|----------|------------|
| **Precio mensual** | $1.000.000 COP | $1.500.000 COP | Cotización; no publicar precio interno |
| **Usuarios** | 20 | 50 | Según contrato |
| **Sedes** | 1 | 3 | Según contrato |
| **Módulos principales** | 1 | Hasta 2 | Todos los acordados |
| **Almacenamiento** | 1 GB | 5 GB | 20 GB ampliables |
| **Soporte** | Email | Chat | Dedicado + SLA según contrato |
| **Onboarding** | Self-service guiado | Guiado | Puesta en marcha acordada |

Los activos no se usan como restricción comercial. Los límites aplicables se gobiernan desde el catálogo de plataforma y el contrato vigente.

---

## Start · Comenzar a digitalizar

| Campo | Contenido |
|-------|-----------|
| **Enfoque** | Resolver primero el dolor operativo dominante |
| **Módulos** | Maintenance o Inventory |
| **Cliente típico** | PYME con una sede y un proceso prioritario |
| **Qué obtiene** | Registros consistentes, dashboard, roles esenciales y reportes |
| **Ruta a Business** | Segundo módulo, más de 20 usuarios o expansión a nuevas sedes |

**Historia de venta:** «No necesitas empezar con todo. Necesitas dejar de perder tiempo reconstruyendo la operación en Excel.»

---

## Business · Integrar la operación

| Campo | Contenido |
|-------|-----------|
| **Enfoque** | Unificar equipos y procesos que ya comenzaron a digitalizarse |
| **Módulos** | Hasta dos módulos principales |
| **Cliente típico** | Empresa en expansión con varios perfiles y hasta tres sedes |
| **Qué obtiene** | Operación coordinada, alertas, permisos por rol e indicadores por área |
| **Ruta a Enterprise** | Más sedes, todos los módulos, SLA, API, integraciones o gobernanza personalizada |

**Plan destacado comercial:** Business representa el punto de equilibrio para organizaciones que necesitan integrar más de un proceso.

---

## Enterprise · Gobernanza y personalización

| Campo | Contenido |
|-------|-----------|
| **Enfoque** | Operación compleja que requiere capacidad y acompañamiento acordados |
| **Módulos** | Todos los módulos incluidos en el contrato |
| **Cliente típico** | Organización multisede con TI, Finanzas y responsables operativos en la decisión |
| **Qué obtiene** | Soporte dedicado, SLA e integraciones según alcance |
| **Ruta** | Expansión por módulos, capacidad y servicios adicionales |

Enterprise no significa desarrollo completamente a medida. Los requerimientos fuera del producto se evalúan y cotizan por separado.

---

## Operación comercial durante el piloto

```text
trial 15 días → factura manual → registrar pago → activar o asignar plan
```

- El registro público siempre crea un trial sin tarjeta.
- SuperAdmin asigna o cambia manualmente Start, Business o Enterprise.
- El cambio de plan queda auditado y no genera factura automáticamente.
- La pasarela de pago está diferida a postpiloto.
- La clave técnica de Business continúa siendo `grow` para conservar compatibilidad.
- `profesional` / Scale es legacy, permanece oculto y no debe ofertarse.

---

## Señales de upgrade

| De → A | Señal |
|--------|-------|
| Start → Business | Segundo módulo, más de 20 usuarios o más de una sede |
| Business → Enterprise | Más de tres sedes, todos los módulos, SLA, API o integración empresarial |

---

## Fuentes de verdad

| Contenido | Fuente |
|-----------|--------|
| Precios, almacenamiento y límites | `PLANES_SEED` en `app/platform_config_service.py` |
| Oferta contractual | COM-01 |
| Servicios adicionales | COM-02 |
| Narrativa comercial | Este capítulo y MCM-04 |

> **Frase del capítulo:** La transformación comienza con un módulo. El crecimiento ocurre dentro de una sola plataforma.
