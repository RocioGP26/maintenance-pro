# MRL-04-HDR · Header estándar

**Código:** MRL-04-HDR · Sprint 7.4 · Bloque **MRL-HDR-001**

---

## Layout oficial

```
┌──────────────────────────────────────────────────────────┐
│ [LOGO EMPRESA]              ROUSTIX                      │
│                             {Título del documento}       │
│                             {Empresa · NIT}              │
│                                                          │
│ DOC-001 · OT-2026-0042          Generado: 10/07/2026   │
│ Módulo: Maintenance             Usuario: Ana García      │
│ MRL v1.0                                                 │
└──────────────────────────────────────────────────────────┘
```

---

## Campos

| Campo | Posición | Tipografía |
|-------|----------|------------|
| **Logo empresa** | Izquierda superior | Max 40 mm ancho |
| **Wordmark Roustix** | Derecha | 10pt · `#888780` |
| **Título** | Derecha bajo wordmark | 16pt bold · `#042C53` |
| **Empresa** | Derecha | 11pt · `#444441` |
| **Código documento** | Izquierda inferior bloque meta | 9pt mono |
| **Fecha** | Derecha inferior | 9pt · `#888780` |
| **Usuario** | Derecha | 9pt |
| **Módulo** | Izquierda | 9pt |
| **Versión MRL** | Izquierda | 8pt · secondary |

---

## Reglas

1. Logo tenant si existe; si no, iniciales empresa en círculo MDL
2. Título = nombre humano del DOC (ej. «Orden de Trabajo Correctiva»)
3. Línea separadora 1pt `#042C53` al 15% opacidad bajo header
4. En páginas 2+, header reducido: título + código + página (opcional repetición)

---

## ReportLab (patrón)

- `Table` de dos columnas para logo / meta
- Estilos en módulo compartido `mrl_styles.py` (futuro)
- No duplicar `ParagraphStyle` por reporte

---

Metadatos completos del documento → [MRL-11-META · Metadata](11-metadata-documento.md)

→ [MRL-05-TBL · Tablas](05-tablas.md)
