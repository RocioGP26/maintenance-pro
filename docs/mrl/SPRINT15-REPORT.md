# Sprint 15 · MRL Foundation — Report & Document Engine

**Código:** MRL-S15 · **Report & Document Engine**  
**Período:** Sprint 15 · **Inicio:** 2026-07-10  
**Predecesor:** Sprint 14 ALIGN (cerrado 2026-07-10)  
**Frase:** Toda la operación. Una sola plataforma.

---

## Objetivo

Crear la **infraestructura común del sistema de reportes (MRL)** para que todos los documentos — Excel, PDF y futuros reportes — compartan la misma identidad visual, metadatos y arquitectura de código.

> **No se implementan funcionalidades de negocio nuevas** en Sprint 15.0.  
> Se formaliza el estándar y se prepara la base sobre la que los módulos existentes y futuros generarán documentos.

---

## Contexto

Tras la secuencia MCM → MKT → MDO → Sprint 14 ALIGN, el producto y MRG están sincronizados. Los módulos en producción **ya generan información**:

| Módulo | Salidas actuales |
|--------|------------------|
| Maintenance | Dashboards, `/reportes`, OT (sin PDF MRL) |
| Inventory | Excel catálogo, bajo stock, plantilla import |
| Purchasing (simplificado) | Compras, CxP |
| Sales | Ventas POS, listados |
| Reports | Gráficos web, badge «Próximamente» en export Excel |

Lo que **no comparten** es una forma única de presentarla. MRL v1.0.1 (Sprint 7) definió el estándar en documentación; Sprint 15 lo convierte en **infraestructura reutilizable**.

---

## Alcance del Sprint

| Fuera de alcance | Dentro de alcance |
|------------------|-------------------|
| Purchasing formal (Sprint 16) | Paquete `app/mrl/` |
| CRM, Analytics | Motores Excel y PDF base |
| MAG CRUD completo | DOC-001 como documento de referencia |
| Features de negocio nuevas | Migración de exports existentes |
| BI / Power BI | Documentación oficial MRL Sprint 15 |

---

## Sub-sprints

| Fase | Código | Objetivo | Estado |
|------|--------|----------|--------|
| **15.0** | MRL-S15.0 | Documentación completa (README, arquitectura, estándares, roadmap, charter) | ✅ |
| **15.1** | MRL-S15.1 | Foundation — `colors`, `typography`, `metadata`, `styles`, smoke test | ✅ |
| **15.2** | MRL-S15.2 | Excel Engine — `BaseExcelExporter`, tablas, header, footer, logo | ✅ |
| **15.3** | MRL-S15.3 | PDF Engine — ReportLab: header, footer, tabla, KPI, numeración, watermark | ✅ |
| **15.4** | MRL-S15.4 | Primer documento oficial — **DOC-001** Orden de Trabajo | ✅ |
| **15.5** | MRL-S15.5 | Integración — reemplazar exports ad hoc (OT, activos, inventario, compras, ventas) | ✅ |

→ Detalle técnico: [architecture.md](architecture.md)  
→ Estándares: [standards.md](standards.md)  
→ Roadmap implementación: [roadmap.md](roadmap.md)

---

## Estructura documental

```
docs/mrl/
├── README.md                 ← índice suite MRL (actualizado Sprint 15)
├── changelog.md
├── roadmap.md                ← roadmap de implementación Sprint 15+
├── architecture.md           ← diseño app/mrl/
├── standards.md              ← reglas obligatorias de código y export
├── strategy.md               ← contexto Sprint 7 (histórico)
├── SPRINT15-REPORT.md        ← este documento
├── templates/
│   └── README.md             ← registro MRL-TPL y guía de plantillas
└── chapters/                 ← especificación funcional MRL v1.0.1 (Sprint 7)
```

---

## Estructura de código (objetivo)

```
app/mrl/
├── __init__.py
├── colors.py
├── typography.py
├── metadata.py
├── styles.py
├── utils.py
├── excel/
│   ├── base.py
│   └── exporter.py
└── pdf/
    ├── base.py
    └── exporter.py
```

→ Especificación completa: [architecture.md](architecture.md)

---

## Definition of Done · Sprint 15 completo

El Sprint queda **terminado** cuando se cumplen **todos** estos criterios:

| # | Criterio | Fase |
|---|----------|------|
| 1 | Existe `app/mrl/` con paquete importable | 15.1 |
| 2 | Documentación oficial MRL Sprint 15 publicada | 15.0 |
| 3 | Changelog MRL actualizado | 15.0+ |
| 4 | Roadmap de implementación vigente | 15.0 |
| 5 | Existe `BaseExcelExporter` operativo | 15.2 |
| 6 | Existe `BasePdfExporter` operativo (bloques, no DOC completos) | 15.3 |
| 7 | Existe `MRLDocumentMeta` / metadata corporativa | 15.1 |
| 8 | Sistema de estilos reutilizable (colors + typography + styles) | 15.1 |
| 9 | Smoke test automatizado pasa en CI/local | 15.1 |
| 10 | DOC-001 OT PDF generado desde producto | 15.4 |
| 11 | Exports inventario migrados a MRL Excel | 15.5 |
| 12 | Exports maintenance (OT, activos) activos en `/reportes` | 15.5 |
| 13 | Badge «Próximamente» retirado de exportaciones implementadas | 15.5 |

---

## Estado actual vs objetivo

| Componente | Hoy (post-ALIGN) | Objetivo Sprint 15 |
|------------|------------------|---------------------|
| MRL docs Sprint 7 | ✅ v1.0.1 completo | ✅ + Sprint 15 docs |
| `app/mrl/` | ❌ No existe | ✅ Paquete foundation (15.1) |
| Excel inventario | 🟡 openpyxl ad hoc | 🟡 BaseExcelExporter (activos ✅; inventario pendiente 15.5) |
| Excel maintenance | 📋 «Próximamente» | 🟡 Activos ✅ · OT pendiente 15.5 |
| PDF operativos | ❌ Sin ReportLab | ✅ DOC-001 + motor base |
| Metadata MRL-11 | 📋 Solo en docs | ✅ En código (15.1) |
| ReportLab | ❌ No en requirements | ✅ Dependencia declarada (15.3) |

---

## Gaps MRG-08 que cierra este Sprint

| Gap | Prioridad pre-Sprint 15 | Resolución |
|-----|-------------------------|------------|
| Export Excel OT / activos | P2 | 15.2 + 15.5 |
| Excel inventario sin estándar MRL | P2 | 15.2 + 15.5 |
| PDF MRL operativos | P3 | 15.3 + 15.4 |
| Tendencias temporales `/reportes` | P2 | 📋 Post-Sprint 15 (Sprint 20) |
| BI / API reportes | P3 | 📋 Sprint 19+ |

---

## Dependencias desbloqueadas

Una vez terminado Sprint 15, estos sprints pueden avanzar **sin rediseñar reportes**:

| Sprint | Enfoque | Reutiliza MRL |
|--------|---------|---------------|
| **16** | Purchasing formal | DOC-006 Compra / OC / recepción |
| **17** | MAG v1 completo | Exports vía API con metadata MRL |
| **18** | CRM | Cotizaciones, pipeline, actividades |
| **19** | Analytics / BI | KPI cards, dashboards exportados |
| **20** | Reportes avanzados | Tendencias, ejecutivos, programados |

Cadena objetivo:

```
DOC-006 Orden de Compra → MRL → MAG → Producto
```

---

## Ciclo de vida (heredado Sprint 14)

| Estado | Significado |
|--------|-------------|
| 📋 **Roadmap** | Aprobado en MRG/MRL · pendiente de desarrollo |
| 🚧 **En desarrollo** | Trabajo activo en código |
| 🧪 **QA / Validación** | Implementado · pruebas · alineación MRG |
| ✅ **Producción** | Disponible · docs y producto sincronizados |

Sprint 15.0 = documentación 🚧 → ✅ al merge.  
Sprint 15.1+ = transición 📋 → 🚧 por sub-sprint.

---

## Entregables · Sprint 15.0 (este documento)

| Entregable | Archivo | Estado |
|------------|---------|--------|
| Charter Sprint 15 | `SPRINT15-REPORT.md` | ✅ |
| Arquitectura código | `architecture.md` | ✅ |
| Estándares implementación | `standards.md` | ✅ |
| Roadmap implementación | `roadmap.md` | ✅ |
| Guía plantillas | `templates/README.md` | ✅ |
| README actualizado | `README.md` | ✅ |
| Changelog MRL | `changelog.md` | ✅ |

**Sin código en 15.0** — solo formalización documental.

---

## Referencias

| Documento | Enlace |
|-----------|--------|
| MRL capítulos Sprint 7 | [chapters/](chapters/) |
| Sprint 14 ALIGN | [../alignment/SPRINT14-REPORT.md](../alignment/SPRINT14-REPORT.md) |
| Matriz MRG ↔ código | [../alignment/status-matrix.md](../alignment/status-matrix.md) |
| MRG-08 Reportes | [../mrg/chapters/08-reportes.md](../mrg/chapters/08-reportes.md) |
| MRL-11 Metadata | [chapters/11-metadata-documento.md](chapters/11-metadata-documento.md) |
| Exports actuales inventario | `app/inventario_comercial/exports.py` |
| Página reportes | `templates/reportes.html` |

---

## Próximo paso

**Sprint 16 · Purchasing** — comenzar el módulo formal de compras reutilizando los
motores Excel/PDF y la metadata corporativa consolidados por MRL.

---

*Sprint 15 · MRL Foundation — Report & Document Engine · Roustix · 2026-07-11 · Sprint 15.0–15.5 ✅ · Sprint finalizado*
