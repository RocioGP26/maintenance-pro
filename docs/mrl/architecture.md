# MRL · Arquitectura de implementación

**Código:** MRL-ARCH · Sprint 15  
**Versión:** v1.1.0-draft  
**Estado:** 📋 Especificación · Sprint 15.0

> Diseño del paquete `app/mrl/` — infraestructura común de reportes y documentos.  
> La especificación funcional permanece en los [capítulos MRL](chapters/) (Sprint 7).

---

## 1 · Principios

| Principio | Descripción |
|-----------|-------------|
| **Un solo motor** | Excel y PDF comparten colors, typography, metadata y reglas de naming |
| **Módulos aportan datos** | Maintenance, Inventory, etc. no definen estilos; solo columnas, filas y contexto DOC |
| **Bloques composables** | Header, tabla, KPI y footer son unidades reutilizables (MRL-HDR-001, MRL-TBL-001, …) |
| **Tenant-first** | Toda export respeta `empresa_id`; metadata incluye empresa, usuario, zona |
| **Sin lógica de negocio** | `app/mrl/` no importa modelos de OT, productos ni compras |

---

## 2 · Capas

```
┌─────────────────────────────────────────────────────────┐
│  Módulos de producto                                     │
│  maintenance · inventario_comercial · routes/reportes      │
│  (adaptadores: datos → MRLDocumentMeta + tablas)         │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│  app/mrl/ · Motores de exportación                       │
│  excel/exporter.py · pdf/exporter.py                     │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│  app/mrl/ · Bloques y estilos                            │
│  colors · typography · metadata · styles · utils         │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│  Librerías externas                                      │
│  openpyxl (Excel) · reportlab (PDF)                      │
└─────────────────────────────────────────────────────────┘
```

---

## 3 · Estructura de paquete

```
app/mrl/
├── __init__.py           # exporta versión MRL, fábricas públicas
├── colors.py             # tokens MDL → valores hex/RGB
├── typography.py         # tamaños, pesos, familias (PDF + convenciones Excel)
├── metadata.py           # MRLDocumentMeta, validación MRL-11
├── styles.py             # registro unificado; acceso a colors + typography
├── utils.py              # filenames, BytesIO, fechas tenant, logo helper
├── excel/
│   ├── base.py           # estilos openpyxl: header row, zebra, bordes
│   └── exporter.py       # BaseExcelExporter
└── pdf/
    ├── base.py           # ParagraphStyle, TableStyle ReportLab
    └── exporter.py       # BasePdfExporter
```

### Responsabilidades por módulo

| Archivo | Responsabilidad |
|---------|-----------------|
| `colors.py` | Constantes `#042C53`, `#F4F7FB`, semánticos verde/rojo/ámbar — ver [MRL-07-COL](chapters/07-colores.md) |
| `typography.py` | 16pt título, 11pt cuerpo, 9pt meta — ver [MRL-04-HDR](chapters/04-header-estandar.md) |
| `metadata.py` | Dataclass `MRLDocumentMeta`: DOC, instancia, módulo, empresa, usuario, fecha, zona, idioma, `mrl_version` |
| `styles.py` | API única: `mrl_colors`, `mrl_fonts`, versión `MRL_VERSION = "1.1"` |
| `utils.py` | `{DOC}-{codigo}-{YYYYMMDD}.{ext}`, resolución logo tenant, formateo fecha LatAm |
| `excel/base.py` | Funciones puras openpyxl: `apply_header_row`, `apply_zebra`, `write_meta_rows` |
| `excel/exporter.py` | Clase `BaseExcelExporter` — ver §5 |
| `pdf/base.py` | Builders ReportLab: header table, footer canvas, KPI row, watermark |
| `pdf/exporter.py` | Clase `BasePdfExporter` — ver §6 |

---

## 4 · Metadata · `MRLDocumentMeta`

Implementación de [MRL-11-META](chapters/11-metadata-documento.md).

```python
@dataclass(frozen=True)
class MRLDocumentMeta:
    doc_code: str           # "DOC-001"
    instance_code: str      # "OT-2026-0042"
    module: str             # "Maintenance"
    empresa_id: int
    empresa_nombre: str
    empresa_nit: str | None
    usuario: str
    generated_at: datetime  # UTC
    timezone: str           # "America/Bogota"
    locale: str             # "es-CO"
    mrl_version: str        # "1.1"
    title: str              # "Orden de Trabajo Correctiva"
    template: str | None    # "MRL-TPL-002"
```

**Reglas:**

- Validar `doc_code` contra registro DOC-001…010 antes de export
- Propiedades PDF (`Title`, `Author`, `Creator`) derivadas de metadata
- Excel: filas 1–N reservadas para meta; fila de columnas en posición fija documentada en `standards.md`

---

## 5 · Excel Engine · `BaseExcelExporter`

**Sprint:** 15.2  
**Dependencia:** `openpyxl` (ya en `requirements.txt`)

### API propuesta

```python
class BaseExcelExporter:
    def __init__(self, meta: MRLDocumentMeta, sheet_name: str): ...

    def write_metadata_block(self, ws) -> int:
        """Escribe filas meta MRL. Retorna índice de fila del header de columnas."""

    def write_table(
        self, ws, headers: list[str], rows: list[list], *, start_row: int
    ) -> None: ...

    def auto_width(self, ws, num_cols: int) -> None: ...

    def build(self) -> tuple[bytes, str]:
        """Retorna (contenido_xlsx, nombre_archivo)."""
```

### Comportamiento obligatorio

| Aspecto | Estándar |
|---------|----------|
| Header de columnas | Fondo `#042C53`, texto blanco, bold |
| Zebra | Filas pares `#F4F7FB` |
| Meta superior | Empresa, NIT, título DOC, fecha, «Generado por Roustix» |
| Nombre hoja | Tipo DOC corto (ej. `Inventario`, `OT`) |
| Nombre archivo | Ver `utils.filename_for(meta, "xlsx")` |

### Adaptadores de módulo (Sprint 15.5)

| Módulo | Función adaptadora | DOC |
|--------|-------------------|-----|
| Maintenance | `maintenance_excel.export_work_orders(meta, queryset)` | DOC-001 / DOC-010 |
| Maintenance | `maintenance_excel.export_assets(meta, queryset)` | DOC-002 |
| Inventory | Refactor `exports.py`, `productos_excel.py` | DOC-003 |
| Purchasing | `purchasing_excel.export_compras(...)` | DOC-006 |
| Sales | `sales_excel.export_ventas(...)` | DOC-010 |

Los adaptadores viven **fuera** de `app/mrl/` (ej. `app/maintenance/mrl_exports.py`).

---

## 6 · PDF Engine · `BasePdfExporter`

**Sprint:** 15.3  
**Dependencia:** `reportlab` (añadir en 15.3)

### Alcance 15.3 — motor, no documentos completos

| Bloque | ID MRL | Incluido en 15.3 |
|--------|--------|------------------|
| Header | MRL-HDR-001 | ✅ |
| Footer | MRL-FTR-001 | ✅ |
| Tabla | MRL-TBL-001 | ✅ |
| KPI row | MRL-KPI-001 | ✅ |
| Numeración | — | ✅ |
| Watermark | — | ✅ (borrador / copia) |
| QR | MRL-QR-001 | 📋 v1.1 |
| Firma | MRL-SIG-001 | 📋 v1.2 |

### API propuesta

```python
class BasePdfExporter:
    def __init__(self, meta: MRLDocumentMeta): ...

    def render_header(self, logo_bytes: bytes | None) -> list[Flowable]: ...
    def render_footer(self, page_num: int, total_pages: int) -> callable: ...
    def render_table(self, headers, rows, col_widths=None) -> Table: ...
    def render_kpi_row(self, kpis: list[tuple[str, str]]) -> Table: ...

    def build(self, story: list[Flowable]) -> tuple[bytes, str]: ...
```

DOC-001 (15.4) compone `story` con bloques del motor + contenido específico OT.

---

## 7 · Smoke test · Sprint 15.1

Ubicación propuesta: `tests/test_mrl_smoke.py`

**Debe verificar (sin datos de negocio):**

1. Import de `app.mrl` y versión definida
2. `MRLDocumentMeta` valida campos obligatorios
3. Generación Excel mínima: 1 hoja, meta + 1 fila tabla, bytes no vacíos
4. (Tras 15.3) Generación PDF mínima: 1 página, header + footer presentes

El smoke test **no** requiere Flask app context ni base de datos.

---

## 8 · Integración Flask

| Patrón | Descripción |
|--------|-------------|
| Rutas | `@bp.route(".../export")` en módulo dueño; delega a adaptador MRL |
| Respuesta | `send_file(BytesIO(data), download_name=nombre, mimetype=...)` |
| Permisos | Sin cambio — permisos existentes del módulo |
| Logo | `utils.load_empresa_logo(empresa)` — lee logo tenant si configurado |

No crear blueprint `mrl_bp` para exports; MRL es librería interna.

---

## 9 · Migración desde código actual

| Archivo actual | Problema | Acción Sprint 15.5 |
|----------------|----------|-------------------|
| `app/inventario_comercial/exports.py` | `_escribir_encabezado_empresa` ad hoc | Usar `BaseExcelExporter` |
| `app/inventario_comercial/productos_excel.py` | Headers sin `#042C53` | Export vía MRL; **import** sin cambios |
| `templates/reportes.html` | Badge «Próximamente» | Enlaces reales post-15.5 |
| — | Sin PDF | DOC-001 en 15.4 |

**Regla:** eliminar funciones duplicadas de encabezado solo cuando el adaptador MRL esté en producción.

---

## 10 · Versionado

| Artefacto | Versión Sprint 15 |
|-----------|-------------------|
| Docs MRL | v1.1.0 |
| `MRL_VERSION` en código | `"1.1"` |
| Compatibilidad | Docs Sprint 7 (v1.0.1) siguen vigentes; este doc extiende implementación |

---

## Referencias

| Doc | Enlace |
|-----|--------|
| Estándares obligatorios | [standards.md](standards.md) |
| Sprint 15 charter | [SPRINT15-REPORT.md](SPRINT15-REPORT.md) |
| Roadmap | [roadmap.md](roadmap.md) |
| Estrategia Sprint 7 | [strategy.md](strategy.md) |

---

*MRL-ARCH · Sprint 15 · Roustix · 2026-07-10*
