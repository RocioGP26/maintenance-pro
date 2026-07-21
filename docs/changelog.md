# Changelog · Roustix Documentation Suite

> Este changelog pertenece a la documentación. Los cambios de la aplicación se
> registran por separado en [`/CHANGELOG.md`](../CHANGELOG.md).

## [1.22.0] — 2026-07-21 · Sprint 22.0 · API pública y Webhooks

### Added
- Charter y arquitectura de integraciones públicas tenant-safe.
- Contrato REST v1 para activos, incidencias, OT, medidores y lecturas.
- Diseño de API keys con scopes, hash, expiración, rotación y revocación.
- Catálogo inicial de webhooks con outbox, HMAC, reintentos e idempotencia.
- Derechos técnicos configurables para API y webhooks.
- Roadmap de implementación Sprint 22.1–22.5.

### Status
- ✅ Sprint 22.0 documental finalizado.
- 📋 Siguiente: Sprint 22.1 · credenciales de integración.

---

## [1.21.0] — 2026-07-21 · Sprint 21 · Asset Health

### Added
- Puntaje explicable de salud por activo con cuatro factores ponderados.
- Confianza de datos, razones accionables y bandas operativas.
- Portafolio con filtros, detalle por factor e historial de snapshots.
- Actualización transaccional desde lecturas, OT, incidencias y automatizaciones.
- Alerta de activos en riesgo y migración `nu2k8m04r37c`.

### Changed
- El dashboard reemplaza el gráfico simple de estados por Asset Health real.

### Status
- ✅ Sprint 21 finalizado.
- 📋 Siguiente: Sprint 22 · API pública, webhooks y derechos técnicos por plan.

---

## [1.20.0] — 2026-07-21 · Sprint 20 · Maintenance Automation

### Added
- Reglas configurables de umbral por medidor y tenant.
- Control de cruce, enfriamiento e idempotencia por regla + lectura.
- Acciones de aviso interno y creación automática de OT.
- Destinatarios por rol, historial de evaluaciones y auditoría.
- Migración Alembic `ls0i6k82p15a` y pruebas del motor.
- Alertas personales por novedades de bitácora y centro de lectura contextual.

### Changed
- `Completada` representa trabajo técnico terminado y pendiente de validación.
- `Cerrada` queda reservada al administrador o supervisor y es el único estado
  que cierra definitivamente un ticket vinculado.
- La campana administrativa muestra las OT pendientes de cierre.
- Migración complementaria `mt1j7l93q26b` para entregas de bitácora.

### Status
- ✅ Sprint 20 finalizado.
- 📋 Siguiente: Sprint 21 · Asset Health avanzado y analítica de condición.

---

## [1.19.5] — 2026-07-21 · Sprint 19.5 · Meters & Closure

### Added
- Medidores acumulativos e instantáneos por activo con rangos de referencia.
- Lecturas históricas con ejecutor, registrador, fecha efectiva y OT opcional.
- Validación y justificación de regresiones, reinicios, rollover y valores fuera de rango.
- Correcciones inmutables, eventos auditables y migración idempotente de horas de operación.
- Migración Alembic `kr9h5j71o04z` y cierre integral de Sprint 19.

### Status
- ✅ Sprint 19 finalizado.
- 📋 Siguiente: Sprint 20 · disparadores de mantenimiento y automatizaciones configurables.

---

## [1.19.4] — 2026-07-21 · Sprint 19.4 · Context Log

### Added
- Bitácora común para órdenes de trabajo, incidencias y activos.
- Visibilidad interna o dirigida al reportante de la incidencia.
- Entradas inmutables y correcciones vinculadas al original.
- Adjuntos privados con validación, checksum y descarga autorizada.
- Auditoría de creación, carga y descarga.
- Migración Alembic `jq8g4i60n93y` y pruebas tenant-safe.

### Status
- ✅ Sprint 19.4 finalizado.
- 📋 Siguiente: Sprint 19.5 · medidores, lecturas, integración y cierre.

---

## [1.19.3] — 2026-07-21 · Sprint 19.3 · Evidence & Review

### Added
- Evidencias privadas con validación de contenido, límite de tamaño y checksum.
- Conformidad, justificación obligatoria y resolución supervisada de hallazgos.
- Confirmación de firma exclusiva del técnico autenticado.
- Revisión formal del checklist y auditoría de descargas y decisiones.
- Migración Alembic `ip7f3h59m82x` y pruebas de seguridad y autoría.

### Status
- ✅ Sprint 19.3 finalizado.
- 📋 Siguiente: Sprint 19.4 · bitácora contextual y archivos adjuntos.

---

## [1.19.2] — 2026-07-21 · Sprint 19.2 · Executable Work Order Checklist

### Added
- Asignación de procedimientos publicados a órdenes de trabajo.
- Checklist histórico con snapshots y progreso calculado en servidor.
- Respuestas con autoría técnica y registro delegado auditables.
- Acceso del técnico limitado a la OT asignada.
- Bloqueo de finalización de la OT cuando faltan pasos obligatorios.
- Migración Alembic `hn6e2g48l71w` y pruebas de tenant, roles y progreso.

### Status
- ✅ Sprint 19.2 finalizado.
- 📋 Siguiente: Sprint 19.3 · evidencias, no conformidades, firma y auditoría.

---

## [1.19.1] — 2026-07-21 · Sprint 19.1 · Procedure Catalog

### Added
- Catálogo tenant-safe de procedimientos de mantenimiento.
- Versiones inmutables con estados borrador, publicada y retirada.
- Pasos ordenados con siete tipos de respuesta y configuración JSON validada.
- Historial auditable de creación, edición, publicación y retiro.
- Pantallas y permisos para gestión administrativa y consulta operativa.
- Migración Alembic `gm5d1f37k60v` y pruebas de integridad, tenant y roles.

### Status
- ✅ Sprint 19.1 finalizado.
- 📋 Siguiente: Sprint 19.2 · checklist ejecutable dentro de la OT.

---

## [1.19.0] — 2026-07-21 · Sprint 19.0 · Maintenance Execution Design

### Added
- Charter de procedimientos, checklists, bitácora contextual y medidores.
- Arquitectura tenant-safe y modelos propuestos de ejecución.
- Estados, permisos, autoría delegada y catálogo de eventos para Sprint 20.
- Matriz de migración para OT históricas, `checklist_registro`, `IncidentHistory` y horas de operación.

### Status
- ✅ Sprint 19.0 formalizado · sin lógica de negocio nueva.
- 📋 Siguiente: Sprint 19.1 · catálogo y versionado de procedimientos.

---

## [1.18.0] — 2026-07-14 · Sprint 18 · Seguridad e Identidad

### Added
- Gestión de sesiones, expiración, revocación y auditoría de identidad.
- Política configurable por tenant y administración de sesiones activas.

### Status
- ✅ Sprint 18 cerrado.

---

## [1.17.0] — 2026-07-11 · Sprint 16.5 · Purchasing cierre

### Added
- Migración idempotente `InvCompra` → solicitud + OC + recepción, sin mover stock.
- Script seguro con `--dry-run` por defecto y `--apply` explícito.
- Compatibilidad legacy, reconciliación, MRG/MAG y navegación alineadas.

### Status
- ✅ Sprint 16 completo · Purchasing operativo.

---

## [1.16.4] — 2026-07-11 · Sprint 16.4 · CxP e indicadores

### Added
- CxP por cada recepción aceptada, sin duplicar movimientos de stock.
- Vencimientos, pagos parciales y vínculo recepción → `InvCompra`.
- Dashboard Purchasing con saldos, vencidas, por vencer y OC abiertas.
- Excel MRL de CxP formal con trazabilidad a recepción.

### Status
- ✅ Sprint 16.4 finalizado · siguiente: migración y alineación 16.5.

---

## [1.16.3] — 2026-07-11 · Sprint 16.3 · Recepciones

### Added
- Recepciones totales, parciales y rechazadas con trazabilidad por línea.
- Confirmación idempotente y control de sobre-recepción.
- Actualización de stock únicamente por cantidades aceptadas.
- Estados OC `parcial` y `recibida`; recepciones confirmadas son inmutables.

### Status
- ✅ Sprint 16.3 finalizado · CxP permanece para Sprint 16.4.

---

## [1.16.2] — 2026-07-11 · Sprint 16.2 · Órdenes de compra

### Added
- Conversión única de solicitud aprobada a orden de compra.
- Proveedor, snapshots de línea, moneda, precios, IVA y totales server-side.
- Estados borrador → emitida → enviada con auditoría.
- DOC-006 PDF MRL; borradores identificados con watermark.

### Status
- ✅ Sprint 16.2 finalizado · recepción y stock permanecen fuera de alcance.

---

## [1.16.1] — 2026-07-11 · Sprint 16.1 · Solicitudes

### Added
- Solicitudes de compra tenant-safe con líneas de catálogo o descripción libre.
- Ciclo borrador → enviada → aprobada/rechazada y auditoría `PurEvento`.
- Permisos específicos, navegación y migración aditiva `pur_*`.

### Status
- ✅ Sprint 16.1 finalizado · sin OC, recepciones, stock ni CxP nuevas.

---

## [1.16.0] — 2026-07-11 · Sprint 16.0 · Purchasing Design

### Added
- Charter, arquitectura, contratos y matriz de migración de Purchasing.
- Sub-sprints 16.0–16.5, estados, permisos, contrato MAG y artefactos MRL.

### Status
- ✅ Sprint 16.0 formalizado · sin cambios de esquema o negocio.

---

## [1.15.0] — 2026-07-10 · Sprint 15.0 · MRL Foundation (documentación)

### Added
- **Sprint 15 · MRL Foundation — Report & Document Engine**
- MRL v1.1.0 docs: `SPRINT15-REPORT.md`, `architecture.md`, `standards.md`, `roadmap.md`, `templates/`
- Charter sub-sprints 15.0–15.5 · Definition of Done · sprints desbloqueados 16–20

### Changed
- MRL README — sección Sprint 15 e índice implementación
- MRL strategy.md — enlace a arquitectura Sprint 15
- MRL-10-ROAD cap. 10 — sección v1.1 implementación

### Status
- ✅ Sprint 15.0 documentación formalizada · código 15.1+ pendiente

---

## [1.14.0] — 2026-07-10 · MDO v1.0.0 · Sprint 13 finalizado

### Added
- **MDO v1.0.0** — Roustix Documentation Operations completo (10 capítulos)
- **MDO-08** · Portal Documental · **MDO-09** · Búsqueda · **MDO-10** · Cierre y gobernanza

### Changed
- MDO v0.7.0 → **v1.0.0**

### Status
- ✅ Sprint 13 finalizado · MDO v1.0.0

---

## [1.13.0] — 2026-07-10 · MDO · Sprint 13 en curso

### Added
- **MDO v0.1.0** — Roustix Documentation Operations · infraestructura `/mdo/`
- **MDO-01** – **MDO-07** · capítulos fundacionales

### Status
- 🚧 Sprint 13 en curso (histórico)

---

## [1.12.0] — 2026-07-10 · MKT v1.0.0 · Sprint 12 finalizado

### Added
- **MKT v1.0.0** — Manual de Marketing completo (10 capítulos)
- **MKT-10** · Guía de Estilo y Gobernanza de Marca · proceso editorial · auditoría

### Status
- ✅ Sprint 12 finalizado · MKT v1.0.0

---

## [1.11.0] — 2026-07-10 · MKT v0.9.0 · Sprint 12 en curso

### Added
- **MKT v0.1.0** — Sales Enablement & Marketing Assets
- **MKT-01** · Identidad y mensajes de marca — Biblia de Marketing
- **MKT-02** · Elevator Pitch y guiones — 30 s · 1 min · 2 min · 5 sectores
- **MKT-03** · Casos de éxito · biblioteca `mtx-case/` · MTX-CASE-001–006
- **MKT-04** · Presentación comercial oficial · 12 slides · guía presentador
- **MKT-05** · Landing Page y sitio web · arquitectura · CTAs · SEO
- **MKT-06** · Secuencias Email · Trial 15 d · Demo · Lead · Onboarding
- **MKT-07** · Brochure y material comercial · One Pager · fichas
- **MKT-08** · Kit Partners · modelo canal · certificación · Deal Registration
- **MKT-09** · Estrategia de Contenidos y Redes Sociales · pilares · calendario
- Estructura `docs/mkt/` · portada `/mkt/` · `mkt_routes.py`

### Status
- 🟡 Sprint 12 en curso · MKT-10 planificado

---

## [1.10.0] — 2026-07-10 · MCM v1.0.0 · Sprint 11 finalizado

### Added
- **Roustix Commercial Manual v1.0.0** — 10 capítulos + Appendix
- MCM-10-PARTNERS · portada `/mcm/` · checklist cierre Sprint 11

### Changed
- MCM alineado MRG v1.0 · versión oficial v1.0.0 (Sprint 11)

---

## [1.9.0] — 2026-07-10 · MCM v1.1 · Sprint 11 en curso

### Added
- **MCM v1.1.0** — 10 capítulos comerciales realineados con MRG v1.0
- MCM-01-INTRO · MCM-05-MODULES · MCM-06-ONBOARD · MCM-08-FAQ · MCM-10-BEST
- Apéndices ICP · DMU · casos · GTM (legacy Sprint 5)

### Changed
- MCM descongelado · índice HTML Sprint 11 · nomenclatura capítulos

---

## [1.8.0] — 2026-07-10 · MRG v1.0 · Sprint 10 completo

### Added
- **MRG v1.0.0** — 10 capítulos · guía funcional del producto
- Lenguaje funcional Mantenimiento · Inventario · adopción · cierre Sprint 10

---

## [1.7.0] — 2026-07-10 · Sprint 10 · MRG iniciado

### Added
- **MRG v0.1.0** — Roustix Reference Guide · guía funcional del producto
- MRG-01-INTRO · estructura 10 capítulos · `/mrg/` · `mrg_routes.py`
- Borradores MRG-02 – MRG-10 alineados a producto actual

---

## [1.6.0] — 2026-07-10 · MSD v1.0 · Sprint 9 completo

### Added
- MSD-09-PUB · publicación · distribución · CI/CD · changelog ecosistema
- **MSD v1.0.0** — 9 capítulos entregados · cierre Sprint 9

---

## [1.5.7] — 2026-07-10 · MSD-08 Colecciones

### Added
- MSD-08-COLL · Postman · Insomnia · docs/api/collections/

---

## [1.5.6] — 2026-07-10 · MSD-07 Quick Start

### Added
- MSD-07-QS · guía onboarding · ejemplos multi-lenguaje

---

## [1.5.5] — 2026-07-10 · MSD-06 Sandbox y API Explorer

### Added
- MSD-06-SBOX · sandbox · API Explorer · tenant empresa-demo

---

## [1.5.4] — 2026-07-10 · MSD-05 Roustix CLI

### Added
- MSD-05-CLI · roustix-cli · automatización · códigos de salida

---

## [1.5.3] — 2026-07-10 · MSD-04 SDK oficiales

### Added
- MSD-04-SDK · estrategia Python · JS · PHP · generación OpenAPI

---

## [1.5.2] — 2026-07-10 · MSD-03 OpenAPI 3.1

### Added
- MSD-03-OAPI · openapi.v1.yaml ampliado · runtime `/api/v1/openapi.json`

---

## [1.5.1] — 2026-07-10 · MSD-02 Developer Portal

### Added
- **MSD v0.2.0** — MSD-02-PORT · portal como contenedor del ecosistema
- Árbol navegación · mapa capítulos · fases implementación

---

## [1.5.0] — 2026-07-10 · Sprint 9 · MSD iniciado

### Added
- **MSD v0.1** — Roustix SDK & Developer Portal · `/msd/`
- MSD-01-PHIL · estructura 9 capítulos · strategy · NOMENCLATURE
- Blueprint `msd_routes.py` · placeholder `openapi.v1.yaml`
- Catálogo docs hub actualizado · MAG Sprint 8 cerrado

---

## [1.4.1] — 2026-07-10 · MAG v1.0 completo

### Changed
- **MAG v1.0.12** — MAG-10-LIM entregado · Sprint 8 **100% completado**
- Índice `/mag/` · suite docs · ecosystem actualizados

---

## [1.4.0] — 2026-07-10 · Sprint 8 · MAG

### Added
- **MAG v1.0** — Roustix API Guide (10 capítulos) · `/mag/`
- Filosofía API · JWT · multi-tenant · recursos `/api/v1`
- Errores · versionado · webhooks · ejemplos · rate limits
- Par MPA (interno) ↔ MAG (externo) documentado

---

## [1.3.1] — 2026-07-10 · MRL complementos

### Added
- **MRL v1.0.1** — complementos 11–13
- MRL-11-META · metadata documento
- MRL-12-TPL · versionado plantillas (`MRL-TPL-001` …)
- MRL-13-A11Y · accesibilidad impresión / escala de grises

---

## [1.3.0] — 2026-07-10 · Sprint 7 · MRL + Fundación 1.0

### Documentation Foundation 1.0
- **MPA v1.0** congelado — Sprint 6 completo
- [RELEASE-FOUNDATION-1.0.md](RELEASE-FOUNDATION-1.0.md)
- Tag recomendado: `docs-foundation-1.0`

### Added · Sprint 7
- **MRL v1.0** — Roustix Report Language (10 capítulos) · `/mrl/`
- DOC-001 – DOC-010 · bloques MRL-HDR/TBL/KPI/CHT
- Estándares PDF (ReportLab) · Excel · CSV

---

## [1.2.0] — 2026-07-10 · Documentación como producto

### Added
- [DOCUMENTATION-PRODUCT.md](DOCUMENTATION-PRODUCT.md) — manifiesto: docs como producto independiente
- [VERSIONS.md](VERSIONS.md) — registro oficial de versiones por manual
- [CROSS-REFERENCES.md](CROSS-REFERENCES.md) — matriz MBB ↔ MDL ↔ MUX ↔ MCM ↔ MPA
- [publishing/README.md](publishing/README.md) — plan MkDocs / Docusaurus para sitio público

### Changed
- [VERSIONING.md](VERSIONING.md) — ampliado con flujo de release documental
- Suite oficial **v1.1** · MPA v1.0.2 en desarrollo

### MPA (desde 1.1.0)
- MPA-01 refinado (Sprint 6.1) · MPA-11 capas · MPA-12 Constitución

---

## [1.1.0] — 2026-07-10 · Sprint 6 · MPA

### Added
- **MPA v1.0** — Roustix Platform Architecture (10 capítulos) · `/mpa/`
- Reorganización suite **01–10**: MPA (05), MRL (06), MAG (07), SDK (08), Developer (09), Release Notes (10)
- Hubs: `developer/`, `sdk/`, `release-notes/`

### Changed
- `architecture/` y `roadmap/` → redirigen a MPA
- Índice maestro `/docs/` actualizado

---

## [1.0.0] — 2026-07-10 · Release interno `docs-v1.0`

### Primera edición oficial congelada

| Manual | Versión | Estado |
|--------|---------|--------|
| Brand Book (MBB) | v2.0 | ✔ Congelado |
| MDL | v1.0 | ✔ Congelado |
| MUX | v1.2 | ✔ Congelado |
| MCM | v1.0 | ✔ Congelado |

### Added
- **Índice maestro** — `/docs/` · [index.html](index.html) · [README.md](README.md)
- [RELEASE-v1.0.md](RELEASE-v1.0.md) — notas del release interno
- [VERSIONING.md](VERSIONING.md) — política de congelamiento y bumps
- Hubs **07 API** · **08 Architecture** · **09 Roadmap** (placeholders)
- Enlaces cruzados Roustix Docs en catálogos MBB · MDL · MUX · MCM

### Contexto
- MCM Sprint 5 completo (10 capítulos)
- MUX cultura UX Laws · DEC · COPY · MEASURE · RESEARCH
- MDL independiente · Brand Book v2.0 sin capítulos técnicos embebidos

→ Tag Git: **`docs-v1.0`**
