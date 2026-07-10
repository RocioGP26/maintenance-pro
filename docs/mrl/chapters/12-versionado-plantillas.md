# MRL-12-TPL · Versionado de plantillas

**Código:** MRL-12-TPL · Complemento Sprint 7

> Si en dos años cambias el diseño de un reporte, debes saber **con qué plantilla** fue generado cada PDF archivado.

---

## 1 · Concepto

| Término | Significado |
|---------|-------------|
| **DOC-0NN** | Tipo de documento (qué es) |
| **MRL-TPL-0NN** | Plantilla visual (cómo se ve) |
| **vX.Y** | Versión semver de la plantilla |

Un mismo DOC puede evolucionar de plantilla sin perder trazabilidad:

```
DOC-009 Reporte Ejecutivo
  └── MRL-TPL-001 v1.0  (2026)
  └── MRL-TPL-001 v1.1  (2027 · nuevos KPIs)
  └── MRL-TPL-001 v2.0  (2028 · rediseño header)
```

---

## 2 · Registro de plantillas

| Código | Nombre | DOC asociado | Versión actual |
|--------|--------|--------------|----------------|
| **MRL-TPL-001** | Reporte Ejecutivo | DOC-009 | v1.0 |
| **MRL-TPL-002** | Orden de Trabajo | DOC-001 | v1.0 |
| **MRL-TPL-003** | Inventario valorizado | DOC-003 | v1.0 |
| **MRL-TPL-004** | Factura comercial | DOC-004 | 📋 Planificado |
| **MRL-TPL-005** | Dashboard PDF | DOC-007 | 📋 Planificado |

Nuevas plantillas → nuevo código **MRL-TPL-0NN**, nunca reutilizar código con diseño incompatible.

---

## 3 · Metadatos de plantilla

Cada PDF generado incluye en metadata (MRL-11):

| Campo | Ejemplo |
|-------|---------|
| `plantilla` | `MRL-TPL-001` |
| `plantilla_version` | `1.0` |
| `mrl_version` | `1.0` |

Visible en footer reducido: `MRL-TPL-001 v1.0`

---

## 4 · Política de versionado

| Bump | Cuándo |
|------|--------|
| **v1.0 → v1.1** | Columna nueva, KPI adicional, ajuste menor |
| **v1.x → v2.0** | Rediseño header, cambio de tipografía, nueva anatomía |
| **Congelar** | Plantilla en producción → no editar; crear v siguiente |

Alineado con [VERSIONING.md](../../VERSIONING.md) de la suite documental.

---

## 5 · Implementación (código)

```python
# Patrón futuro · app/mrl_templates.py
TEMPLATES = {
    "MRL-TPL-001": {"doc": "DOC-009", "version": "1.0", "builder": build_reporte_ejecutivo_v1},
    "MRL-TPL-002": {"doc": "DOC-001", "version": "1.0", "builder": build_ot_v1},
}
```

Al generar PDF: registrar `plantilla` + `plantilla_version` en metadata y auditoría.

---

## 6 · Ejemplo · MRL-TPL-001

| Atributo | Valor |
|----------|-------|
| **Código** | MRL-TPL-001 |
| **Nombre** | Reporte Ejecutivo |
| **Versión** | v1.0 |
| **DOC** | DOC-009 |
| **Bloques** | HDR-001 · KPI-001 · TBL-001 · CHT-001 · FTR-001 |
| **Estado** | Documentado · implementación pendiente |

---

→ [MRL-13-A11Y · Accesibilidad](13-accesibilidad.md)
