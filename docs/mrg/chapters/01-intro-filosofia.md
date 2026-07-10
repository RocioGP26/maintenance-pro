# MRG-01-INTRO · Filosofía de Maintix

**Código:** MRG-01-INTRO · Sprint 10.1 · **Entregado**

> Maintix no es solo software de mantenimiento ni un ERP genérico. Es una **plataforma SaaS modular** para operar activos, inventario y procesos relacionados — con un solo tenant, un solo login y datos aislados por empresa.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Establecer qué es Maintix, qué problema resuelve y los principios funcionales que rigen todos los módulos. Este capítulo es la puerta de entrada al **Maintix Reference Guide (MRG)**.

---

## Principios del producto

Equivalente funcional a MAG-01, aplicado al **negocio** — no al contrato API:

| # | Principio | Significado |
|---|-----------|-------------|
| 1 | **Plataforma SaaS** | Suscripción por empresa; operación en la nube sin instalación local |
| 2 | **Tenant-first** | Toda operación ocurre en contexto de una empresa aislada |
| 3 | **Modular** | Módulos activables según contrato — no monolito rígido |
| 4 | **API-first** | Integración nativa vía contrato MAG · herramientas MSD |
| 5 | **Datos auditables** | Procesos registrados, trazables y medibles |
| 6 | **Integración nativa** | Módulos comparten tenant, roles y dashboards |
| 7 | **Escalable** | De un módulo a suite completa sin cambiar de plataforma |

Estos principios rigen MRG completo y guían implementación, soporte y capacitación.

---

## 1 · Qué es Maintix

Maintix es una plataforma **multi-empresa (SaaS)** orientada a la operación industrial y comercial:

| Aspecto | Descripción |
|---------|-------------|
| **Tipo** | Software como servicio (SaaS) |
| **Modelo** | Suscripción por empresa (tenant) |
| **Enfoque** | Operación real: activos, OT, inventario, compras, ventas |
| **Usuarios** | Gerentes, técnicos, bodegueros, vendedores, administradores |

Maintix unifica en una sola aplicación lo que muchas organizaciones hoy dispersan en hojas de cálculo, WhatsApp y sistemas desconectados.

---

## 2 · Qué problema resuelve

| Antes (sin Maintix) | Con Maintix |
|---------------------|-------------|
| OT en papel o Excel sin trazabilidad | Órdenes de trabajo con historial, técnicos y costos |
| Inventario desactualizado | Stock en tiempo real con alertas de mínimo |
| Compras sin vínculo al stock | Entrada de mercancía que actualiza catálogo y CxP |
| Ventas sin control de existencias | POS que descuenta stock y registra cobros |
| Datos mezclados entre sucursales o clientes | **Tenant-first:** cada empresa ve solo sus datos |
| Integraciones ad hoc | API documentada (MAG) + ecosistema desarrolladores (MSD) |

Maintix convierte la operación diaria en **procesos registrados, medibles y auditables**.

---

## 3 · Modelo SaaS

Cada **cliente de Maintix** es una **empresa (tenant)** con:

| Elemento | Función |
|----------|---------|
| **Suscripción** | Plan Start / Grow / Scale (ver MCM) |
| **Trial** | Período de prueba con datos de ejemplo |
| **Módulos activos** | Mantenimiento, Inventario u otros según contrato |
| **Usuarios y roles** | Equipo interno con permisos por rol |
| **Sedes** | Una o más ubicaciones físicas |
| **Sector** | Plantilla de onboarding (manufactura, comercio, etc.) |

La plataforma **Mantis** (operador de Maintix) gestiona tenants, facturación SaaS y soporte de plataforma — distinto del administrador de cada empresa cliente.

→ [MRG-07 · Administración](07-administracion.md) · [MCM · Planes comerciales](/mcm/chapters/06-planes-comerciales.md)

---

## 4 · Modularidad y evolución del producto

Maintix crece por **módulos operativos activables**, no por productos separados con marcas distintas.

### Evolución de la plataforma

```
Maintix

        Core Platform
              │
────────────────────────────────
Mantenimiento
Inventario
────────────────────────────────
Purchasing
Sales
CRM
Finance
Analytics
AI
```

La capa superior (**Core Platform**) incluye tenancy, auth, planes, onboarding y dashboards base. Los módulos de la primera franja están en **producción**; los de la segunda franja representan la **hoja de ruta** del producto.

### Madurez de módulos

| Módulo | Clave | Estado |
|--------|-------|--------|
| **Mantenimiento** | `mantenimiento` | 🟢 Producción |
| **Inventario** | `inventario` | 🟢 Producción |
| **Purchasing** | — | 🟡 Diseño |
| **Sales** | — | 🟡 Diseño |
| **CRM** | — | ⚪ Roadmap |
| **Finance** | — | ⚪ Roadmap |
| **Analytics** | — | ⚪ Roadmap |
| **AI** | — | ⚪ Roadmap |

**Leyenda:** 🟢 Producción · 🟡 Diseño (especificación / subflujos parciales) · ⚪ Roadmap

**Notas de hoy:**

- **Ventas** — POS y ventas operan dentro de Inventario; el módulo Sales unificado está en diseño.
- **Compras** — compras comerciales en Inventario; unificación con compras técnicas en diseño.

**Regla:** un tenant puede tener uno o varios módulos activos. El menú, el dashboard y los permisos se adaptan a los módulos contratados.

→ [MPA-02 · Ecosistema](/mpa/chapters/02-ecosistema.md) · [MPA-05 · Roadmap módulos](/mpa/chapters/05-roadmap-modulos.md)

---

## 5 · Tenant-first

Todo en Maintix ocurre en **contexto de empresa**:

| Principio | Implicación funcional |
|-----------|----------------------|
| Aislamiento de datos | Usuarios de Empresa A nunca ven datos de Empresa B |
| Configuración por tenant | Logo, moneda, zona horaria, campos personalizados |
| Roles por empresa | El mismo usuario puede existir en teoría en varias empresas (futuro); hoy: una empresa por sesión |
| API coherente | JWT incluye `empresa_id` — ver MAG-03 |
| Reportes y KPIs | Siempre agregados al tenant activo |

**Tenant-first** no es solo arquitectura: es cómo el usuario entiende que «mi empresa» es el universo de su operación.

---

## 6 · Suite documental oficial

MRG ocupa un lugar específico entre los manuales de Maintix. **Nomenclatura unificada** de toda la suite:

| Código | Documento | Audiencia | Pregunta |
|--------|-----------|-----------|----------|
| **MPA** | Maintix Platform Architecture | Arquitectos · equipo interno | ¿Cómo está construido? |
| **MAG** | Maintix API Guide | Integradores · desarrolladores | ¿Cómo me conecto por API? |
| **MSD** | Maintix SDK & Developer Portal | Desarrolladores externos | ¿Qué herramientas uso (SDK, CLI, Portal)? |
| **MRG** | Maintix Reference Guide | Clientes · implementadores · soporte · QA | **¿Cómo funciona el producto?** |
| **MCM** | Maintix Commercial Manual | Ventas · marketing | ¿Cómo se vende y posiciona? |
| **MUX** | Maintix User Experience | Diseño · producto | ¿Cómo debe sentirse la experiencia? |
| **MRL** | Maintix Report Language | Reportes · operaciones | ¿Cómo se estandarizan documentos y exportaciones? |

**MRG no habla de Flask ni SQLAlchemy.** Habla de activos, órdenes, stock, clientes y procesos.

---

## 7 · Mapa de capítulos MRG

| # | Capítulo | Contenido |
|---|----------|-----------|
| 01 | Introducción | Este capítulo |
| 02 | Mantenimiento | Activos · OT · preventivos · repuestos |
| 03 | Inventario | Productos · stock · kardex |
| 04 | Compras | Entradas · CxP |
| 05 | Ventas | POS · crédito · clientes |
| 06 | CRM | Pipeline · oportunidades (roadmap) |
| 07 | Administración | Usuarios · roles · configuración |
| 08 | Reportes | KPIs · dashboards · exportaciones |
| 09 | Workflows | Procesos end-to-end |
| 10 | Buenas prácticas | Implementación correcta |

---

## 8 · Quién debe leer MRG

| Perfil | Uso |
|--------|-----|
| **Cliente / gerente** | Entender alcance del producto y KPIs |
| **Implementador / consultor** | Configurar tenant, módulos y procesos |
| **Soporte** | Resolver dudas funcionales sin mirar código |
| **QA** | Casos de prueba alineados al negocio |
| **Nuevo desarrollador** | Contexto funcional antes de MPA/MAG |
| **Comercial** | Complemento a MCM — qué entrega el producto en la práctica |

---

## 9 · Distinciones importantes

Evitar confusiones frecuentes al documentar o implementar Maintix:

| Concepto A | Concepto B | Diferencia |
|------------|------------|------------|
| Repuesto técnico | Producto comercial | Mantenimiento vs Inventario — inventarios separados |
| Proveedor de servicio | Proveedor comercial | OT externa vs compra de mercancía |
| Compras (MRG-04) | Módulo Compras unificado | Hoy: subflujo de Inventario; futuro: módulo Purchasing |
| Cliente de venta | CRM | Hoy: maestro de clientes en ventas; futuro: pipeline y oportunidades |
| Admin empresa | Admin plataforma | Config tenant vs gestión Mantis |

---

## Evolución de MRG

Recorrido completo de la guía funcional — de filosofía a implementación:

```
MRG
│
├── 01 · Filosofía
├── 02 · Mantenimiento
├── 03 · Inventario
├── 04 · Purchasing
├── 05 · Sales
├── 06 · CRM
├── 07 · Administration
├── 08 · Reports
├── 09 · Workflows
└── 10 · Best Practices
```

Cada capítulo profundiza un dominio del producto; MRG-09 y MRG-10 conectan los módulos en procesos y buenas prácticas de despliegue.

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] Definición de Maintix y problema que resuelve
- [x] Principios del producto documentados
- [x] Modelo SaaS y evolución modular documentados
- [x] Tabla de madurez de módulos uniforme
- [x] Principio tenant-first explicado
- [x] Suite documental con nomenclatura oficial unificada
- [x] Mapa de capítulos · audiencias · evolución MRG

---

## Filosofía del capítulo

Una plataforma SaaS madura necesita tres capas de documentación: **arquitectura (MPA)**, **integración (MAG + MSD)** y **producto (MRG)**. MRG cierra la tercera — la que responde «¿qué hace Maintix en mi operación diaria?».

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **MRG** | v1.0.0 |
| **Sprint 10** | ✅ Completo |
| **Siguiente** | MRG-02-MAINT · Mantenimiento |

---

→ [MRG-02 · Mantenimiento](02-maintenance.md) · [MPA-02 · Ecosistema](/mpa/chapters/02-ecosistema.md) · [Índice MRG](/mrg/)
