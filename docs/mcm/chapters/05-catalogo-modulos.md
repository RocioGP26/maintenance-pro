# MCM-05-MODULES · Catálogo de módulos

**Código:** MCM-05-MODULES · Sprint 11.5 · **Entregado**

> Maintix no se vende como un conjunto de aplicaciones independientes. Se presenta como una **plataforma empresarial modular**, donde cada módulo resuelve una necesidad específica y todos comparten la misma experiencia, autenticación y datos del tenant.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MCM-01-INTRO](01-intro-filosofia-comercial.md) · [MCM-03-MARKETS](03-sectores-mercados.md) · [MRG-01 · Filosofía](/mrg/chapters/01-intro-filosofia.md) · [MPA](/mpa/)

---

## Objetivo del capítulo

Presentar el **catálogo funcional de módulos** disponibles, su **estado de madurez** y cómo se utilizan dentro de la estrategia comercial.

Este capítulo ayuda al equipo comercial a explicar:

- Qué puede implementar el cliente **hoy**
- Qué forma parte del **roadmap**
- Cómo un cliente puede **crecer sin cambiar de plataforma**

---

## 1 · Filosofía modular

Cada módulo resuelve un **problema concreto**.

Todos comparten:

| Elemento compartido | Significado comercial |
|---------------------|----------------------|
| **Mismo tenant** | Una empresa · datos aislados · una facturación |
| **Mismos usuarios** | Un equipo · permisos por rol |
| **Mismo inicio de sesión** | Un acceso · no cinco URLs distintas |
| **Mismo diseño (MUX)** | Misma experiencia · misma curva de aprendizaje |
| **Misma plataforma SaaS** | Actualizaciones · soporte · planes unificados |

El cliente **no compra aplicaciones separadas**.

Compra una **plataforma que evoluciona** junto con su operación.

**Pilar de marca:**

> *La transformación comienza con un módulo. El crecimiento ocurre dentro de una sola plataforma.*

→ Arquitectura: [MPA](/mpa/) · Core Platform en [MRG-01](/mrg/chapters/01-intro-filosofia.md)

---

## 2 · Módulos en producción

| Módulo | Clave | Estado | Puerta comercial |
|--------|-------|--------|------------------|
| **Mantenimiento** | `mantenimiento` | ✅ Producción | Activos · OT · Preventivos |
| **Inventario** | `inventario` | ✅ Producción | Stock · Compras · Ventas |

Estos dos módulos constituyen la **primera versión comercial completa** de Maintix.

**Mensaje comercial:** hoy el cliente puede operar mantenimiento **o** inventario comercial en producción — no prometer más allá de esta frontera sin aclarar roadmap.

---

## 3 · Mantenimiento

### Problema que resuelve

Controlar **activos físicos** durante todo su ciclo de vida.

### Beneficios

| Área | Capacidad |
|------|-----------|
| Órdenes de trabajo | Ciclo completo · estados · asignación |
| Mantenimiento preventivo | Calendario · alertas · cumplimiento |
| Incidencias | Registro · trazabilidad |
| Técnicos | Roles · tiempos · responsables |
| Repuestos | Consumo en OT *(expansión con Inventario)* |
| Indicadores | Disponibilidad · MTTR · OT abiertas |

### Cliente ideal

Industria · manufactura · talleres · flotas · facilities · servicios con activos críticos.

**Frase de venta:** *«La planta deja de depender de la memoria del técnico.»*

→ [MRG-02 · Mantenimiento](/mrg/chapters/02-maintenance.md) · Sectores: [MCM-03-MARKETS §3](03-sectores-mercados.md#3--industria-y-manufactura)

---

## 4 · Inventario

### Problema que resuelve

Mantener controlado el **inventario comercial** — stock, movimientos, compras y ventas.

### Beneficios

| Área | Capacidad |
|------|-----------|
| Catálogo | Productos · precios · unidades |
| Stock | Tiempo real · mínimos · kardex |
| Compras | Proveedores · recepción · CxP operativa |
| Ventas | POS · descuento automático de stock |
| Clientes | Maestro comercial · historial |
| Cartera básica | Cobros · saldo pendiente |

### Cliente ideal

Comercio · distribución · agro · ferreterías · mayoristas · retail con bodega.

**Frase de venta:** *«Deja de vender a ciegas.»*

**Operativo hoy en Inventario:** compras y ventas integradas — evolución hacia módulos **Purchasing** y **Sales Pro** en roadmap.

→ [MRG-03 · Inventario](/mrg/chapters/03-inventario.md) · [MRG-04 · Compras](/mrg/chapters/04-compras.md) · [MRG-05 · Ventas](/mrg/chapters/05-ventas.md)

---

## 5 · Roadmap de módulos

| Módulo | Estado | Notas comerciales |
|--------|--------|-------------------|
| **Purchasing** | 📋 Diseño | Compras unificadas · OC · recepción — subflujo hoy en Inventario |
| **CRM** | 📋 Diseño | Pipeline · oportunidades — especificación MRG-06 |
| **Sales Pro** | 📋 Evolución | POS avanzado · crédito · comisiones |
| **Analytics** | 📋 Roadmap | BI · consolidado · KPIs multisede |
| **Finance** | 📋 Roadmap | Contabilidad avanzada · integración ERP |
| **IAM avanzado** | 📋 Roadmap | Gobernanza · permisos extendidos · Enterprise |

**Regla comercial crítica:** estos módulos **no deben venderse como funcionalidades disponibles** hasta entrar oficialmente en producción.

**Frase aprobada cuando preguntan por roadmap:**

> *«Hoy resolvemos mantenimiento e inventario en producción. El resto está documentado en MRG — crecemos contigo en la misma plataforma, sin migraciones.»*

→ [MRG-06 · CRM](/mrg/chapters/06-crm.md) · [MPA · Roadmap](/mpa/)

---

## 6 · Cómo crece un cliente

La plataforma evoluciona **sin migraciones ni reinstalaciones**:

```
Mantenimiento
        │
        ▼
Mantenimiento + Inventario
        │
        ▼
Purchasing
        │
        ▼
CRM
        │
        ▼
Analytics
```

| Etapa | Plan típico | Señal |
|-------|-------------|-------|
| Un módulo | **Start** | Primer dolor resuelto |
| Dos módulos | **Grow** | Planta + bodega · repuestos + OT |
| Multisede + roadmap | **Scale / Enterprise** | Compras · CRM · analytics |

→ Planes: [MCM-04-PLANS](04-planes-saas.md) · Onboarding: [MCM-06-ONBOARD](06-onboarding-implementacion.md)

---

## 7 · Cómo presentar los módulos

El vendedor debe comenzar por el **principal dolor operativo** — **no por el catálogo**.

| Cliente dice… | Respuesta comercial |
|---------------|---------------------|
| *«Tenemos demasiadas fallas.»* | *«Comencemos con **Mantenimiento**.»* |
| *«No sabemos cuánto inventario tenemos.»* | *«Comencemos con **Inventario**.»* |
| *«Tenemos planta y bodega desconectadas.»* | *«¿Qué les duele más hoy — equipos o stock? Empezamos por ahí.»* |

**En demo (MCM-07):** PLAY-003 muestra **un flujo completo** del módulo de entrada — no un tour de menús.

---

## 8 · Qué NO hacer

| ❌ Evitar | ✅ Conversación correcta |
|----------|-------------------------|
| «Tenemos siete módulos.» | «Resolvemos su operación — empezamos por lo que más duele.» |
| «Nuestro ERP hace de todo.» | «Una plataforma modular — activas lo que necesitas hoy.» |
| «Compre el paquete completo.» | «Plan **Start** con un módulo · trial 15 días.» |
| Listar roadmap como si fuera producción | Honestidad: producción vs diseño vs roadmap (§5) |

**Pregunta guía:**

> *¿Qué parte de la operación necesita recuperar primero?*

---

## 9 · Relación entre módulos

| Módulo | Relación |
|--------|----------|
| **Mantenimiento** | Consume repuestos técnicos *(→ Inventario)* |
| **Inventario** | Administra productos comerciales |
| **Purchasing** | Alimenta Inventario · abastecimiento unificado |
| **CRM** | Alimenta ventas · pipeline comercial |
| **Sales Pro** | Evolución del POS y ciclo comercial |
| **Analytics** | Consolida KPIs de todos los módulos |
| **Administración** | Gestiona usuarios · sedes · tenant |

**Administración** no es un módulo vendible por separado — es **Core Platform** incluido en todos los planes.

→ [MRG-07 · Administración](/mrg/chapters/07-administracion.md) · [MRG-09 · Workflows](/mrg/chapters/09-workflows.md)

---

## 10 · Evolución comercial

Cada nuevo módulo **aumenta el valor** de la plataforma. **No sustituye** al anterior.

```
Start
  │
  ▼
Mantenimiento
  │
Inventario
  │
CRM
  │
Analytics
  │
Enterprise Platform
```

**No se trata de vender más módulos.**

Se trata de **acompañar el crecimiento** de la operación del cliente.

| Documento | Rol |
|-----------|-----|
| **MCM-04-PLANS** | Start → Grow → Scale → Enterprise |
| **MCM-03-MARKETS** | Puerta de entrada por sector |
| **MRG** | Qué hace cada módulo en detalle |
| **MPA** | Cómo se conectan arquitectónicamente |
| **MAG / MSD** | Integraciones cuando el cliente escala |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] Catálogo comercial documentado
- [x] Estado de cada módulo definido
- [x] Roadmap claramente diferenciado
- [x] Estrategia de crecimiento modular documentada
- [x] Relación con MRG y MPA establecida

---

## Filosofía del capítulo

Cada módulo aporta valor **por sí mismo**.

Pero el verdadero potencial de Maintix aparece cuando todos trabajan sobre la **misma plataforma**.

No se trata de vender más módulos.

Se trata de **acompañar el crecimiento de la operación** del cliente.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Catálogo comercial** | ✅ Definido |
| **Roadmap** | ✅ Documentado |
| **Material comercial** | 🟡 En preparación *(brochures y fichas por módulo)* |

---

**Próximo capítulo:** [MCM-06-ONBOARD · Implementación y onboarding](06-onboarding-implementacion.md)

---

*MCM-05-MODULES · Maintix Commercial Manual · Sprint 11 · 2026*
