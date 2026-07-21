# MRL-11-META · Metadata del documento

**Código:** MRL-11-META · Complemento Sprint 7

> Todo documento generado por Roustix lleva **metadatos consistentes** — en el header visible, en el footer y en las propiedades del archivo (PDF/Excel).

---

## 1 · Registro oficial de campos

| Campo | Descripción | Obligatorio | Ejemplo |
|-------|-------------|-------------|---------|
| **Documento** | Código DOC del tipo | Sí | `DOC-007` |
| **Versión** | Versión del documento instancia | Sí | `1.0` |
| **Empresa** | Tenant que genera | Sí | `Empresa XYZ S.A.S.` |
| **Usuario** | Quién generó (si aplica) | Sí* | `Ana García` |
| **Fecha** | Timestamp de generación | Sí | `2026-07-10T10:30:00` |
| **Zona horaria** | IANA del tenant | Sí | `America/Bogota` |
| **Idioma** | Locale del documento | Sí | `es-CO` |
| **Hash** | Integridad / verificación | Opcional | `sha256:abc…` |

\* Exportaciones automáticas programadas pueden usar `Sistema · Roustix`.

---

## 2 · Dónde vive cada metadato

| Capa | Campos |
|------|--------|
| **Header visible** (MRL-04) | Documento · Empresa · Fecha · Usuario · Módulo |
| **Footer** (MRL-FTR-001) | Página · «Generado por Roustix» · Versión MRL |
| **PDF properties** | Title, Author, Subject, Creator, CreationDate |
| **Excel** | Fila 1 metadatos o hoja `_meta` |
| **CSV** | Línea comentario `# Roustix · DOC-003 · …` |

---

## 3 · Formato fecha y zona

- Almacenar en **UTC** internamente
- Mostrar en PDF según `zona_horaria` del tenant (`Empresa.zona_horaria`)
- Formato visible LatAm: `DD/MM/YYYY HH:mm` + abreviatura zona si multi-país

---

## 4 · Hash (opcional)

Uso previsto:

- Verificación de documento no alterado (QR MRL-QR-001)
- Auditoría DOC-008
- API futura de validación

Si se incluye: `SHA-256` del contenido binario o de campos canónicos JSON.

---

## 5 · Ejemplo completo · DOC-007

```yaml
documento: DOC-007
version: "1.0"
empresa_id: 42
empresa: "Empresa XYZ S.A.S."
usuario: "Ana García"
fecha: "2026-07-10T15:30:00Z"
zona_horaria: America/Bogota
idioma: es-CO
mrl_version: "1.0"
plantilla: MRL-TPL-001
hash: null
```

---

## 6 · Reglas

1. Ningún PDF de producción sin al menos **Documento + Empresa + Fecha**
2. Metadatos deben coincidir entre header visible y propiedades del archivo
3. No incluir datos de otro tenant en metadatos
4. Idioma por defecto `es-CO`; extensible a `es-VE`, `es-MX` en roadmap

---

→ [MRL-12-TPL · Versionado de plantillas](12-versionado-plantillas.md)
