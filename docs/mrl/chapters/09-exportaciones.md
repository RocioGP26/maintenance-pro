# MRL-09-EXP · Exportaciones

**Código:** MRL-09-EXP · Sprint 7.9

---

## PDF

| Aspecto | Estándar MRL |
|---------|--------------|
| Motor | **ReportLab** |
| Anatomía | MRL-03 completa |
| Nombre archivo | `{DOC}-{codigo}-{fecha}.pdf` |
| Metadata | Título, autor Roustix, empresa |

**Objetivo:** reconocible sin ver el logo.

---

## Excel

| Aspecto | Estándar |
|---------|----------|
| Uso | Datos tabulares, análisis externo |
| Header fila 1 | Mismos labels que MRL tabla |
| Estilo header | Fondo `#042C53`, texto blanco (openpyxl / xlsxwriter) |
| Zebra | Filas pares `#F4F7FB` |
| Hoja | Nombre = tipo DOC (ej. `Inventario`) |
| Primera fila | Metadatos: empresa, fecha, generado por Roustix |

Ya implementado parcialmente en Inventory — alinear a MRL.

---

## CSV

| Aspecto | Estándar |
|---------|----------|
| Encoding | UTF-8 con BOM (Excel LatAm) |
| Separador | `;` o `,` según locale tenant |
| Primera línea | Comentario `# Roustix · {empresa} · {fecha}` opcional |
| Headers | Igual que tabla MRL |

---

## Reglas transversales

1. Export siempre respeta **tenant** — solo datos `empresa_id`
2. MUX: feedback al usuario al terminar export
3. Archivos grandes → job async (MPA-08)
4. Mismo DOC code en nombre y metadata
5. Metadata completa según [MRL-11-META](11-metadata-documento.md) · plantilla según [MRL-12-TPL](12-versionado-plantillas.md)

---

→ [MRL-10-ROAD · Roadmap](10-roadmap.md) · [MRL-11-META](11-metadata-documento.md)
