# MRL-02-DOC · Tipos de documentos

**Código:** MRL-02-DOC · Sprint 7.2

Catálogo oficial de documentos que Maintix genera o exportará. Todos comparten anatomía MRL (cap. 03).

---

## Registro DOC

| Código | Documento | Módulo | Formato principal |
|--------|-----------|--------|-------------------|
| **DOC-001** | Orden de Trabajo | Maintenance | PDF |
| **DOC-002** | Activo / ficha técnica | Maintenance | PDF |
| **DOC-003** | Inventario | Inventory · Maintenance | PDF · Excel |
| **DOC-004** | Factura | Sales (futuro) · Inventory | PDF |
| **DOC-005** | Cotización | Sales (futuro) | PDF |
| **DOC-006** | Compra / entrada | Inventory | PDF |
| **DOC-007** | Dashboard exportado | Ambos | PDF |
| **DOC-008** | Auditoría | Plataforma | PDF |
| **DOC-009** | Reporte ejecutivo | Ambos | PDF |
| **DOC-010** | Exportación genérica | Ambos | PDF · Excel · CSV |

---

## Metadatos por documento

Cada DOC incluye en header:

| Campo | Ejemplo |
|-------|---------|
| Código DOC | `DOC-001` |
| Código instancia | `OT-2026-0042` |
| Módulo origen | Maintenance |
| Empresa | Razón social tenant |
| Fecha generación | ISO + zona tenant |
| Usuario | Quién generó (si aplica) |
| Versión MRL | `MRL v1.0` |

---

## Estado de implementación (hoy)

| DOC | Estado |
|-----|--------|
| DOC-001 · OT | 🟡 ReportLab · estandarizar MRL |
| DOC-003 · Inventario | 🟡 Excel activo · PDF MRL |
| DOC-006 · Compra | 🟡 En producto |
| DOC-007–010 | 📋 Roadmap MRL-10 |

---

## Regla

Nuevo tipo de documento → nuevo código **DOC-0NN** en este registro antes de implementar.

---

→ [MRL-03-ANAT · Anatomía](03-anatomia-documento.md)
