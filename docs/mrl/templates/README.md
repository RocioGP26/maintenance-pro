# MRL · Plantillas de documento

**Código:** MRL-TPL · Sprint 15  
**Registro oficial:** [MRL-12-TPL](../chapters/12-versionado-plantillas.md)

> Catálogo de plantillas (`MRL-TPL-*`) que componen documentos DOC usando bloques MRL.

---

## Registro activo

| Código | Nombre | DOC | Formato | Estado |
|--------|--------|-----|---------|--------|
| **MRL-TPL-001** | Reporte Ejecutivo | DOC-009 | PDF | 📋 |
| **MRL-TPL-002** | Orden de Trabajo | DOC-001 | PDF | 🚧 Sprint 15.4 |
| **MRL-TPL-003** | Inventario valorizado | DOC-003 | PDF · Excel | 📋 |

Nuevas plantillas requieren entrada aquí y en [NOMENCLATURE.md](../NOMENCLATURE.md) **antes** de implementación.

---

## Anatomía de una plantilla

Toda plantilla MRL se compone de bloques estándar:

```
MRL-TPL-00N
├── MRL-HDR-001    Header (logo, título, meta DOC)
├── [cuerpo]       Secciones específicas del DOC
│   ├── MRL-KPI-001   (opcional)
│   ├── MRL-TBL-001   (tablas)
│   └── MRL-CHT-001   (opcional)
└── MRL-FTR-001    Footer (página, Roustix, versión MRL)
```

Referencia: [MRL-03-ANAT](../chapters/03-anatomia-documento.md).

---

## MRL-TPL-002 · Orden de Trabajo (DOC-001)

**Sprint:** 15.4 · documento de referencia del motor PDF.

### Secciones

| # | Sección | Bloque |
|---|---------|--------|
| 1 | Header | MRL-HDR-001 |
| 2 | Resumen OT | KPI: estado, prioridad, tipo |
| 3 | Activo / ubicación | Texto + metadata |
| 4 | Descripción / trabajo | Párrafo |
| 5 | Repuestos utilizados | MRL-TBL-001 |
| 6 | Tiempos / técnico | MRL-TBL-001 |
| 7 | Footer | MRL-FTR-001 |

### Metadata mínima

```yaml
documento: DOC-001
plantilla: MRL-TPL-002
instance_code: OT-2026-0042
module: Maintenance
title: "Orden de Trabajo Correctiva"
```

---

## MRL-TPL-003 · Inventario valorizado (DOC-003)

**Sprint:** 15.5 (Excel) · PDF 📋 v1.1

### Excel

- Meta filas 1–6
- Tabla: referencia, nombre, stock, mínimo, valor
- Export vía `BaseExcelExporter`

---

## Cómo añadir una plantilla

1. Asignar código `MRL-TPL-0NN` en [NOMENCLATURE.md](../NOMENCLATURE.md)
2. Registrar DOC en [MRL-02-DOC](../chapters/02-tipos-documentos.md) si no existe
3. Documentar secciones en este archivo
4. Implementar adaptador en módulo (`app/{modulo}/mrl_exports.py`)
5. Usar solo bloques de `app/mrl/` — no estilos locales
6. PR con checklist [standards.md](../standards.md) §11
7. Entrada en [changelog.md](../changelog.md)

---

## Plantillas futuras (roadmap)

| Código | DOC | Módulo | Sprint |
|--------|-----|--------|--------|
| MRL-TPL-004 | DOC-006 | Purchasing | 16 |
| MRL-TPL-005 | DOC-005 | CRM / Sales | 18 |
| MRL-TPL-006 | DOC-007 | Analytics | 19 |

---

→ [standards.md](../standards.md) · [architecture.md](../architecture.md)

---

*MRL-TPL · Sprint 15 · Roustix · 2026-07-10*
