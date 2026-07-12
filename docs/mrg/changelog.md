# MRG Changelog

## [1.1.0] — 2026-07-11 · Sprint 16 · Purchasing

### Changed
- MRG-04-PUR pasa de parcial a operativo.
- Solicitudes, OC, recepción parcial, stock, CxP e indicadores alineados.
- Compatibilidad y migración legacy documentadas.

---

## [1.0.9] — 2026-07-10 · Sprint 14 · Cierre MRG-09-WORKFLOWS (ALIGN Fase 8)

### Changed
- **MRG-09-WORKFLOWS** v1.0.1 — matriz §1–§12 · badges · notas «hoy en producto» · ALIGN ✅ cerrado
- Auditoría Fase 8 · [09-workflows-audit.md](../alignment/modules/09-workflows-audit.md)

### Producto (verificación)
- Flujos core confirmados en código: incidencia→OT · preventivos · compra/venta/stock · onboarding · IAM
- Sin cambios de producto (solo documentación)

---

## [1.0.8] — 2026-07-10 · Sprint 14 · Cierre MRG-08-REPORTS (ALIGN Fase 7)

### Changed
- **MRG-08-REPORTS** v1.0.1 — matriz §1–§9 · badges · ALIGN ✅ cerrado
- Auditoría Fase 7 · [08-reportes-audit.md](../alignment/modules/08-reportes-audit.md) · consolida [02-reports-audit.md](../alignment/modules/02-reports-audit.md)

### Producto (alineación)
- Submenú **Indicadores** → Mantenimiento (`/reportes`) + Inventario comercial (`/comercial/dashboard`)
- Copy MRG-08 §4 en `/reportes` · enlace cruzado a dashboard comercial

---

## [1.0.7] — 2026-07-10 · Sprint 14 · Cierre MRG-07-ADMIN (ALIGN Fase 6)

### Changed
- **MRG-07-ADMIN** v1.0.1 — matriz §1–§10 · matriz IAM transversal · ALIGN ✅ cerrado
- Auditoría Fase 6 · [07-permissions-matrix.md](../alignment/modules/07-permissions-matrix.md)

### Producto (alineación)
- Submenú **Administración** → Usuarios y roles · Configuración · Campos

---

## [1.0.6] — 2026-07-10 · Sprint 14 · Cierre MRG-06-CRM (ALIGN Fase 5)

### Changed
- **MRG-06-CRM** v1.0.1 — matriz §1–§10 · maestro clientes vs roadmap · ALIGN ✅ cerrado
- Auditoría Fase 5 en `docs/alignment/modules/06-crm-audit.md`

### Producto (alineación)
- **Clientes** bajo submenú Ventas · copy pre-CRM en listado

---

## [1.0.5] — 2026-07-10 · Sprint 14 · Cierre MRG-05-SALES (ALIGN Fase 4)

### Changed
- **MRG-05-SALES** v1.0.1 — matriz §1–§10 · cartera por cobrar §6 · ALIGN ✅ cerrado
- Auditoría Fase 4 en `docs/alignment/modules/05-ventas-audit.md`

### Producto (alineación)
- Submenú **Ventas** → Listado · **Por cobrar** (cartera ligera)
- Copy POS simplificado

---

## [1.0.4] — 2026-07-10 · Sprint 14 · Cierre MRG-04-PUR (ALIGN Fase 3)

### Changed
- **MRG-04-PUR** v1.0.2 — subsección CxP §5 · matriz §5·CxP
- Auditoría Fase 3 · gaps OC/solicitudes/API documentados

### Producto (alineación)
- Nav «Compras» · listado con estado pago y filtros CxP
- Submenú **Compras** → Listado · **Cuentas por pagar** · sección MRG §5 CxP

---

## [1.0.3] — 2026-07-10 · Sprint 14 · Cierre MRG-03-INV (ALIGN Fase 2)

### Changed
- **MRG-03-INV** v1.0.1 — matriz §1–§6 · badges · Sprint 14 ALIGN ✅ cerrado
- Auditoría Fase 2 · gaps API/kardex/ajuste documentados

### Producto (alineación)
- Nav: «Repuestos técnicos» · «Dashboard inventario» (MRG §6)
- Filtro «Bajo stock» en listado · enlace desde dashboard

---

## [1.0.2] — 2026-07-10 · Sprint 14 · Cierre MRG-02-MAINT (ALIGN Fase 1)

### Changed
- **MRG-02-MAINT** v1.0.2 — matriz de implementación por sección (§1–§11 · API)
- Badges ✅/🟡/📋 en encabezados de sección · Sprint 14 ALIGN marcado ✅ cerrado
- Exit criteria actualizados · gaps abiertos documentados (jerarquía · baja activo · en espera OT · export · API CRUD)
- Prosa §10 «activos» (antes equipos) · notas «hoy en producto» §4–§9

### Added
- Enlace a auditorías Sprint 14 en `docs/alignment/modules/`

---

## [1.0.1] — 2026-07-10 · Sprint 14 · Alineación documental (inicio)

### Changed
- **MRG-02-MAINT** — estado producto 🟢 → 🟡 Parcial; leyenda de estados de implementación
- Artefactos Sprint 14 en `docs/alignment/` (checklist · matriz · auditoría Fase 1)

---

## [1.0.0] — 2026-07-10 · MRG v1.0 · Sprint 10 completo

### Added
- **MRG-08-REPORTS** · **MRG-10-BEST** completos
- Adopción del sistema · evolución continua · cierre Sprint 10

### Changed
- Nomenclatura funcional: **Mantenimiento** · **Inventario** (prosa MRG)
- **MRG v1.0.0** — 10 capítulos · catálogo `/mrg/` · suite docs v1.8.0

---

## [0.1.7] — 2026-07-10 · MRG-09 Flujos de trabajo (parcial)

### Added
- **MRG-09-WORKFLOWS** completo — filosofía · Maintenance · incidencias · comercial
- Onboarding · admin · integración módulos · trazabilidad · automatización

---

## [0.1.6] — 2026-07-10 · MRG-07 Administración

### Added
- **MRG-07-ADMIN** completo — tenant vs Mantis · roles · onboarding · seguridad
- Gestión usuarios · sedes · configuración · integración cross-módulo · buenas prácticas

---

## [0.1.5] — 2026-07-10 · MRG-06 CRM (parcial)

### Added
- **MRG-06-CRM** completo — alcance · pipeline · entidades · integración Sales/Inventory
- Indicadores comerciales · evolución prevista · buenas prácticas · estado actual vs objetivo

---

## [0.1.4] — 2026-07-10 · MRG-05 Sales / Ventas (parcial)

### Added
- **MRG-05-SALES** completo — POS · estados · crédito · clientes · indicadores
- Integración Inventory · Sales Pro · buenas prácticas · correspondencia `InvVenta`

---

## [0.1.3] — 2026-07-10 · MRG-04 Purchasing / Compras (parcial)

### Added
- **MRG-04-PUR** completo — flujo compras · proveedores · OC · recepción · indicadores
- Relación Inventory · Maintenance · buenas prácticas · estado actual vs roadmap

---

## [0.1.2] — 2026-07-10 · MRG-02 Maintenance (parcial)

### Added
- **MRG-02-MAINT** — roles · ciclo de vida activo · historial · estados OT ampliados
- Costos en OT · criticidad · dashboard conceptual · bloque Estado

---

## [0.1.1] — 2026-07-10 · MRG-01 refinamiento

### Changed
- Principios del producto · diagrama evolución plataforma · tabla madurez módulos
- Nomenclatura suite unificada (MPA · MAG · MSD · MRG · MCM · MUX · MRL)
- Bloque Evolución de MRG al cierre del capítulo

---

## [0.1.0] — 2026-07-10 · Sprint 10 iniciado · MRG-01

### Added
- **MRG-01-INTRO** completo — filosofía · SaaS · modularidad · tenant-first
- Estructura Sprint 10 · 10 capítulos · strategy · NOMENCLATURE
- Blueprint `mrg_routes.py` · catálogo `/mrg/`
- Suite docs **v1.7.0**

---
