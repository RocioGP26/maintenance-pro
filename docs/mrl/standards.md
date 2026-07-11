# MRL · Estándares de implementación

**Código:** MRL-STD · Sprint 15  
**Versión:** v1.1.0  
**Estado:** 🚧 Sprint 15.0 · obligatorio para todo código en `app/mrl/`

> Reglas que **todo export y documento** generado por Maintix debe cumplir.  
> Especificación funcional detallada: [capítulos MRL](chapters/).

---

## 1 · Regla de oro

**Ningún módulo define estilos propios de export.**  
Usa `app/mrl/`. Si falta un bloque, extiende MRL — no copies estilos en el módulo.

**Ningún módulo funcional importa `openpyxl` directamente.**  
Toda generación Excel pasa por `app.mrl.excel` (adaptador + `BaseExcelExporter`).

---

## 2 · Códigos de documento (DOC)

| Código | Documento | Formato | Plantilla |
|--------|-----------|---------|-----------|
| DOC-001 | Orden de Trabajo | PDF | MRL-TPL-002 |
| DOC-002 | Activo / ficha técnica | PDF | — |
| DOC-003 | Inventario | PDF · Excel | MRL-TPL-003 |
| DOC-004 | Factura | PDF | 📋 |
| DOC-005 | Cotización | PDF | 📋 |
| DOC-006 | Orden de compra | PDF | ✅ Sprint 16.2 |
| DOC-007 | Dashboard exportado | PDF | MRL-TPL-001 |
| DOC-008 | Auditoría | PDF | 📋 |
| DOC-009 | Reporte ejecutivo | PDF | MRL-TPL-001 |
| DOC-010 | Exportación genérica | Excel · CSV | — |

Registro completo: [MRL-02-DOC](chapters/02-tipos-documentos.md).

**Antes de implementar un export nuevo:** registrar DOC si no existe.

---

## 3 · Bloques MRL

| ID | Uso | Referencia |
|----|-----|------------|
| MRL-HDR-001 | Header | [cap. 04](chapters/04-header-estandar.md) |
| MRL-FTR-001 | Footer | architecture.md §6 |
| MRL-TBL-001 | Tablas | [cap. 05](chapters/05-tablas.md) |
| MRL-KPI-001 | KPI cards | [cap. 06](chapters/06-kpi-cards.md) |
| MRL-CHT-001 | Gráficos | [cap. 08](chapters/08-graficos.md) |
| MRL-QR-001 | QR verificación | 📋 v1.1 |
| MRL-SIG-001 | Firma digital visual | 📋 v1.2 |

---

## 4 · Colores (obligatorios)

Fuente: [MRL-07-COL](chapters/07-colores.md) · implementación: `app/mrl/colors.py`

| Token | Hex | Uso |
|-------|-----|-----|
| `PRIMARY` | `#042C53` | Títulos, header tabla Excel/PDF |
| `BODY` | `#444441` | Texto cuerpo |
| `MUTED` | `#888780` | Metadata, footer, wordmark |
| `ACCENT` | `#185FA5` | Enlaces, acentos |
| `BORDER` | `#E2E8F0` | Líneas, bordes |
| `SURFACE` | `#F4F7FB` | Zebra, fondo KPI |
| `OK` | `#38A169` | Estado operativo |
| `CRITICAL` | `#E53E3E` | Crítico |
| `WARNING` | `#D69E2E` | Advertencia |

**Prohibido:** inventar colores fuera de MDL/MRL en exports.

---

## 5 · Tipografía

Fuente: [MRL-04-HDR](chapters/04-header-estandar.md) · implementación: `app/mrl/typography.py`

| Elemento | PDF | Excel |
|----------|-----|-------|
| Título documento | 16pt bold | 14pt bold fila meta |
| Cuerpo | 11pt | 11pt default |
| Metadata | 9pt | 9–10pt |
| Wordmark Maintix | 10pt muted | Texto meta |
| Versión MRL | 8pt | Footer / última fila meta |

PDF: Helvetica o equivalente ReportLab embebido.  
Excel: fuente sistema (Calibri/Arial) — bold solo en headers MRL.

---

## 6 · Metadata · MRL-11

Todo export **de producción** incluye:

| Campo | Obligatorio |
|-------|-------------|
| `doc_code` | Sí |
| `instance_code` | Sí (o `BATCH-{fecha}` en listados) |
| `empresa_nombre` | Sí |
| `generated_at` + `timezone` | Sí |
| `usuario` | Sí (o `Sistema · Maintix`) |
| `mrl_version` | Sí |
| `module` | Sí |

Detalle: [MRL-11-META](chapters/11-metadata-documento.md).

---

## 7 · Excel

Fuente: [MRL-09-EXP](chapters/09-exportaciones.md)

| Regla | Valor |
|-------|-------|
| Librería | `openpyxl` |
| Header columnas | Fondo `#042C53`, texto blanco |
| Zebra | Pares `#F4F7FB` |
| Meta | Filas 1–6 (empresa, NIT, título, fecha, generador) |
| Fila header columnas | Fila 7 (convención Sprint 15) |
| Nombre archivo | `{DOC}-{codigo}-{YYYYMMDD}.xlsx` |
| Tenant | Solo datos `empresa_id` del contexto |
| UTF-8 | Sí · sin caracteres corruptos en nombres |

**Import Excel** (productos): fuera de MRL — solo exports usan `BaseExcelExporter`.

---

## 8 · PDF

| Regla | Valor |
|-------|-------|
| Motor | `reportlab` |
| Anatomía | [MRL-03-ANAT](chapters/03-anatomia-documento.md) |
| Nombre archivo | `{DOC}-{codigo}-{YYYYMMDD}.pdf` |
| PDF properties | Title, Author=`Maintix`, Creator, Subject=DOC code |
| Logo tenant | Max 40 mm ancho; fallback iniciales en círculo |
| Páginas 2+ | Header reducido (título + código + página) |
| Impresión B/N | Contraste mínimo 4.5:1 — [MRL-13-A11Y](chapters/13-accesibilidad.md) |

---

## 9 · CSV (futuro)

| Regla | Valor |
|-------|-------|
| Encoding | UTF-8 con BOM |
| Separador | `;` default LatAm |
| Primera línea | `# Maintix · {empresa} · {DOC} · {fecha}` |

Implementación: 📋 post-Sprint 15 o bajo DOC-010.

---

## 10 · Naming de archivos en código

```
app/mrl/colors.py          # constantes, sin lógica
app/mrl/metadata.py        # MRLDocumentMeta
app/mrl/excel/exporter.py  # BaseExcelExporter
app/mrl/pdf/exporter.py    # BasePdfExporter
app/{modulo}/mrl_exports.py  # adaptadores por módulo (fuera de app/mrl)
tests/test_mrl_smoke.py    # smoke test Sprint 15.1
tests/test_mrl_excel.py    # opcional 15.2
tests/test_mrl_pdf.py      # opcional 15.3
```

**Prohibido:** `mrl_styles.py` monolítico duplicado (patrón obsoleto de strategy.md Sprint 7).

---

## 11 · Checklist PR · export MRL

Todo PR que toque exports debe verificar:

- [ ] Usa `MRLDocumentMeta` con DOC válido
- [ ] No define colores/fuentes fuera de `app/mrl/`
- [ ] Nombre archivo sigue convención `{DOC}-{codigo}-{fecha}`
- [ ] Metadata visible coincide con propiedades archivo (PDF)
- [ ] Respeta tenant — sin datos cruzados
- [ ] Smoke test / tests MRL pasan
- [ ] Captura visual adjunta en PR (primera vez por DOC)
- [ ] Changelog MRL actualizado si nuevo DOC o bloque

---

## 12 · UX · MUX

Al completar export en UI:

- Feedback claro (toast o redirect con mensaje)
- Nombre archivo legible para el usuario
- Errores: mensaje MUX, no stack trace

---

## Referencias

| Doc | Enlace |
|-----|--------|
| Arquitectura | [architecture.md](architecture.md) |
| Plantillas | [templates/README.md](templates/README.md) |
| Sprint 15 | [SPRINT15-REPORT.md](SPRINT15-REPORT.md) |

---

*MRL-STD · Sprint 15 · Maintix · 2026-07-10*
