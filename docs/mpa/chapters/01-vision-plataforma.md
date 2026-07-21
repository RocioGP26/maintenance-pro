# MPA-01-VIS · Visión de plataforma

**Código:** MPA-01-VIS · Sprint 6.1  
**Audiencia:** Desarrolladores · arquitectos · producto · futuros miembros del equipo  
**Frase de plataforma:** Toda la operación. Una sola plataforma.

> Si el **Brand Book (MBB)** explica la identidad de la **marca**,  
> **MPA-01** explica la identidad del **producto**.

---

## 0 · Identidad de marca vs identidad de producto

Roustix tiene dos narrativas complementarias. No compiten: se refuerzan.

| Dimensión | Documento | Pregunta | Ejemplo |
|-----------|-----------|----------|---------|
| **Marca** | MBB · MCM | ¿Quiénes somos? ¿Cómo lo comunicamos? | Historia dual, voz, pilares, trial 15 días |
| **Producto** | **MPA** | ¿Qué construimos? ¿Cómo crece? | EMP, módulos, tenancy, roadmap 2030 |

**Regla para el equipo:** cuando alguien nuevo pregunta «¿qué es Roustix?», la respuesta comercial vive en [MCM-01-POS](/mcm/chapters/01-posicionamiento.md). La respuesta de **ingeniería y producto** vive aquí.

---

## 1 · ¿Qué es realmente Roustix?

Roustix no es un repositorio Flask. No es un dashboard de OT. No es una tienda con inventario.

**Roustix es una Enterprise Management Platform (EMP)** — una plataforma SaaS multi-tenant que permite a las empresas latinoamericanas **controlar, organizar y optimizar su operación** activando solo los módulos que necesitan hoy, con espacio para crecer mañana **sin cambiar de sistema**.

### Definición operativa (producto)

```
Roustix = Plataforma única
        + Tenants aislados (empresas)
        + Módulos activables (Maintenance, Inventory, …)
        + Roles y permisos por tenant
        + Datos compartidos bajo las mismas reglas
        + Experiencia unificada (MUX + MDL)
```

### Lo que el producto promete (técnicamente)

| Promesa | Cómo se cumple en código |
|---------|--------------------------|
| Una sola plataforma | Un despliegue, un codebase, `empresa_id` en cada entidad |
| Empieza simple | Onboarding con un módulo · sector → plantilla |
| Crece sin migrar | `modulos_activos_json` · nuevos blueprints, mismo login |
| Misma historia de datos | OT, stock y futuros módulos bajo un tenant |
| LatAm primero | Español, monedas regionales, realidad Excel/WhatsApp |

### Lo que Roustix **no** promete (hoy)

- ❌ Reemplazar un ERP financiero completo en el día uno
- ❌ Consultoría ilimitada por cliente
- ❌ Customización que rompe el modelo multi-tenant
- ❌ Un producto distinto por industria (forks de código)

---

## 2 · La pregunta que abre todo el MPA

**¿Cómo está construido Roustix y hacia dónde crecerá?**

MPA-01 responde la primera mitad en términos de **identidad**. Los capítulos 02–10 responden el **cómo** y el **hacia dónde** con mapas, módulos, SaaS, integraciones y roadmap.

Sin esta base, el equipo tiende a:

- Diseñar features como si Roustix fuera un CMMS con extras
- Duplicar lógica por sector en lugar de plantillas
- Tratar cada módulo nuevo como mini-producto aislado
- Subestimar el costo de romper tenancy o permisos

**MPA-01 es el cimiento.** Todo capítulo posterior asume que Roustix es una EMP.

---

## 3 · ¿Por qué no es solo un software de mantenimiento?

### Qué es un CMMS

Un **CMMS** (Computerized Maintenance Management System) gestiona un dominio acotado:

| Capacidad típica | En Roustix hoy |
|------------------|----------------|
| Activos y equipos | ✅ Módulo **Maintenance** |
| Órdenes de trabajo | ✅ Correctivas y preventivas |
| Calendario preventivo | ✅ Planeación mensual |
| Repuestos técnicos | ✅ Inventario de mantenimiento |
| Proveedores de servicio | ✅ |

Hasta aquí, Roustix **parece** un CMMS. Y para muchas empresas industriales, **Maintenance es la puerta de entrada correcta**.

### Por qué esa etiqueta es insuficiente

| Limitación del CMMS como categoría | Realidad Roustix |
|-----------------------------------|------------------|
| Define el producto por un módulo | Maintenance es **uno** de N módulos |
| Expansión = comprar otro software | Expansión = activar Inventory, CRM, … |
| Usuario = técnico de planta | Usuario = gerente, vendedor, admin, bodeguero |
| Datos aislados del comercio | Mismo tenant puede tener OT **y** ventas |
| Arquitectura mono-vertical | Multi-tenant · modular · sector = configuración |

### Origen que lo explica

El módulo Maintenance nació en 🇨🇴 Colombia de experiencia industrial real. Pero la decisión de producto fue **no quedarse ahí**: el mismo dolor de «información dispersa» apareció en 🇻🇪 Venezuela en comercio e inventario — y nació **Inventory**.

**Conclusión de producto:** si diseñas una feature pensando solo en OT y activos, pregúntate: *¿esto sirve a la plataforma entera o solo a un vertical?*

---

## 4 · ¿Por qué no es un ERP tradicional?

### Qué es un ERP (en la práctica PyME LatAm)

Un **ERP** tradicional intenta ser el sistema nervioso de **toda** la empresa:

- Contabilidad, nómina, producción, compras, ventas, activos fijos, reportes legales…
- Implementación de meses, consultores, parametrización profunda
- Contrato largo antes de ver valor operativo
- Curva de adopción alta para equipos que aún viven en Excel

### Con quién **no** competimos

Roustix **no** compite primero con SAP, Oracle ni suites contables completas.

Compite con el **caos operativo**:

| Enemigo real | Síntoma |
|--------------|---------|
| Excel | Versiones distintas, sin historial confiable |
| WhatsApp | Decisiones sin registro |
| Cuadernos y memoria | Conocimiento que se va con la persona |
| Herramientas sueltas | Mantenimiento en un lado, ventas en otro |

### Contraste directo

| ERP tradicional | Roustix EMP |
|-----------------|-------------|
| Todo o nada | **Modular** — Start con un dolor |
| Finanzas al centro | **Operación al centro** — finanzas consolidadas después |
| Meses hasta valor | Días a semanas por módulo |
| Consultoría obligatoria | Onboarding guiado + plantillas sectoriales |
| Cambiar de ERP = proyecto | Activar módulo = configuración |
| Enterprise desde día 1 | Start → Grow → Scale ([MCM-06](/mcm/chapters/06-planes-comerciales.md)) |

**Conclusión de producto:** Roustix es **operación primero**. Finance (futuro) se apoya en datos operativos ya confiables — no al revés.

---

## 5 · ¿Qué significa ser una Enterprise Management Platform?

**EMP** no es un acrónimo de marketing. Es una **decisión de arquitectura**.

### Desglose · Enterprise

| Aspecto | En Roustix |
|---------|------------|
| Unidad de negocio | **Empresa** (tenant) con usuarios, roles, sedes |
| Aislamiento | `empresa_id` · middleware tenancy |
| Escala organizacional | De 10 a 500+ empleados (ICP MCM-03) |
| Gobernanza | Planes, límites, suspensión, auditoría plataforma |
| Multi-sede | `Sede` dentro del tenant |

**Enterprise** aquí no significa «solo corporativos». Significa que el producto está pensado para **organizaciones reales con estructura**, no para un usuario suelto con una hoja de cálculo.

### Desglose · Management

| Aspecto | En Roustix |
|---------|------------|
| Objeto de gestión | Operación: activos, stock, compras, ventas, personas |
| Métricas | Dashboards, KPIs, reportes PDF (MRL) |
| Procesos | OT, preventivos, entradas, ventas, CxP… |
| Toma de decisiones | Visibilidad en tiempo operativo, no solo cierre contable |

**Management** = ayudar a **dirigir la operación diaria**, no solo archivarla.

### Desglose · Platform

| Aspecto | En Roustix |
|---------|------------|
| Una base tecnológica | Un codebase · un despliegue |
| Módulos = capacidades | `mantenimiento`, `inventario`, futuros en `modules.py` |
| Extensión sin fork | Nuevo blueprint, mismo tenant, mismos usuarios |
| Ecosistema futuro | API, SDK, marketplace, integraciones (MPA-06) |
| Cultura de construcción | MUX Laws · MDL · filosofía MPA-09 |

**Platform** es la palabra más importante. Es lo que diferencia a Roustix de «un software que hace X».

### La definición en una frase

> Una plataforma modular que ayuda a las empresas a **controlar, organizar y optimizar su operación** mediante módulos activables sobre una sola base tecnológica.

(Alineada con [MCM-01-POS](/mcm/chapters/01-posicionamiento.md) — marca y producto dicen lo mismo.)

### EMP · Lo que sí y lo que no

| ❌ No es EMP | ✅ Sí es EMP |
|-------------|-------------|
| Micro-productos con login distinto | Un tenant, un acceso, módulos activables |
| Fork por industria (`roustix-mineria`) | Plantillas sectoriales sobre mismo código |
| CMMS + inventario pegados | Módulos con contrato tenancy común |
| Feature sin dueño de plataforma | Todo feature declara módulo y permiso |
| Migración al crecer | Activación de módulo |

---

## 6 · Origen dual → decisión de arquitectura

La historia del Brand Book no es decorativa. Es la **justificación** de la EMP.

| Origen | País | Dolor | Módulo | Clave técnica |
|--------|------|-------|--------|---------------|
| Industrial | 🇨🇴 Colombia | Activos, OT, disponibilidad | **Maintenance** | `mantenimiento` |
| Comercial | 🇻🇪 Venezuela | Stock, compras, ventas | **Inventory** | `inventario` |

**Decisión de plataforma (irreversible):** unificar ambos en una sola EMP, no mantener dos aplicaciones.

Eso implica:

1. Un solo modelo `Empresa`
2. Un solo flujo de login
3. Un solo menú que se adapta a módulos activos
4. Un solo roadmap de producto (MPA-05, MPA-10)

→ Historia de marca: [MBB](/brandbook/#historia-origen) · Comercial: [MCM-01](/mcm/chapters/01-posicionamiento.md)

---

## 7 · Principios inmutables del producto

Estos principios no cambian con el sprint. Cambian los módulos; no la naturaleza de Roustix.

| # | Principio | Implicación |
|---|-----------|-------------|
| 1 | **Una plataforma** | No crear «Roustix Lite» ni «Roustix CMMS Edition» |
| 2 | **Tenant primero** | Toda entidad de negocio tiene `empresa_id` |
| 3 | **Módulo explícito** | Registrar en `modules.py` antes de exponer rutas |
| 4 | **Sector = configuración** | Plantillas, no tablas duplicadas |
| 5 | **Operación antes que contabilidad** | Finance viene cuando hay datos operativos |
| 6 | **LatAm primero** | Español, realidad PYME, integraciones regionales |
| 7 | **Crecimiento interno** | Nuevo módulo, no nuevo producto |
| 8 | **UX no negociable** | MUX Laws aplican a todo módulo nuevo |

---

## 8 · Visión a 10 años (2026 – 2036)

Esta visión conecta MPA-01 con [MPA-10-2030](10-roadmap-2030.md). Es **dirección estratégica**, no compromiso de fecha.

### Horizonte 2026–2028 · Fundación y expansión operativa

| Año | Estado del producto |
|-----|---------------------|
| **2026** | Maintenance + Inventory en producción · MPA v1 · Documentation Suite |
| **2027** | CRM, Purchasing, Sales Pro · webhooks tempranos |
| **2028** | Finance, Analytics, IAM · datos operativos consolidados |

**Meta:** ser la EMP de referencia para PyMEs LatAm que superaron Excel.

### Horizonte 2029–2031 · Ecosistema abierto

| Año | Estado del producto |
|-----|---------------------|
| **2029** | API pública estable · marketplace de integraciones |
| **2030** | Mobile GA · AI operativo (sugerencias, consultas) |
| **2031** | Conectores ERP regionales maduros |

**Meta:** Roustix como **hub operativo** que se conecta al ecosistema financiero y analítico del cliente.

### Horizonte 2032–2036 · Plataforma enterprise

| Año | Estado del producto |
|-----|---------------------|
| **2032–2034** | Escala 10 000+ empresas · infra documentada (MPA-08) |
| **2035–2036** | AI Platform · predicción preventiva · compliance enterprise |

**Meta:** la EMP que las empresas latinoamericanas **no necesitan reemplazar** al crecer.

### Norte que no cambia en 10 años

- Una plataforma, no fragmentación
- Modularidad sobre monolito
- Operación confiable antes que feature hype
- La misma frase: **Toda la operación. Una sola plataforma.**

---

## 9 · Implicaciones por rol

| Rol | Qué hacer con MPA-01 |
|-----|----------------------|
| **Desarrollador** | Antes de codear: ¿esto sirve al tenant completo? ¿En qué módulo vive? |
| **Arquitecto** | Validar que nuevas capacidades encajan en EMP, no en silos |
| **Producto** | Priorizar por dolor operativo y puerta de entrada (MCM), no por etiqueta CMMS |
| **Nuevo en el equipo** | Leer MPA-01 → MPA-03 → MUX Laws → MDL |
| **Comercial** | No contradecir MCM-01; MPA confirma la misma EMP con vocabulario técnico |

---

## 10 · Checklist · ¿Esta decisión respeta la visión?

Antes de aprobar un diseño o feature significativo:

- [ ] ¿Se puede activar/desactivar por módulo sin afectar otros tenants?
- [ ] ¿Respeta `empresa_id` y permisos en servidor?
- [ ] ¿Usa MDL y cumple MUX Laws?
- [ ] ¿Evita duplicar lógica por sector?
- [ ] ¿Aporta a la plataforma completa, no solo a un vertical?
- [ ] ¿Podría explicarse en una frase alineada con EMP?

Si alguna respuesta es **no**, rediseñar antes de merge.

---

## 11 · Frase rectora · De marca a código

**Toda la operación. Una sola plataforma.**

| Capa | Traducción |
|------|------------|
| Marca (MBB) | Promesa al cliente |
| Comercial (MCM) | Cómo se vende la promesa |
| **Producto (MPA)** | **Cómo se cumple en arquitectura** |
| UX (MUX) | Cómo se siente al usarla |
| UI (MDL) | Cómo se ve |

---

## Cierre

Las empresas no necesitan otro software aislado. Necesitan **una plataforma que crezca con su operación**.

MPA-01 fija esa verdad para el equipo que la construye.

**Próximo capítulo:** [MPA-02-ECO · Ecosistema Roustix](02-ecosistema.md) — el mapa oficial de módulos y capacidades.

---

*MPA-01-VIS · Roustix Platform Architecture · Sprint 6.1 · 2026*
