# Publicación · Sitio de documentación

> **🔒 Documento interno (DevOps / equipo).** No publicar en el sitio comercial.
> Acceso: login · excluido del build público (junto a MCM · MPA · Developer · MDL · MUX).

**Suite docs · Estrategia híbrida (público / privado)**

Hoy Roustix sirve la documentación desde Flask con control de acceso:

| Zona | Contenido | Acceso |
|------|-----------|--------|
| **Público** | MBB · MAG · MSD · Release Notes · OpenAPI · MKT assets · **`/guia`** | Sin login |
| **Privado** | MCM · MPA · MDL · MUX · MRL · MDO · Developer · MKT capítulos · **`/mrg/`** (fuente) | Login |
| **Hub** | `/docs/` índice | Visible; paths filtrados |

**Arquitectura de contenido de producto:**

```
docs/mrg/*.md     →  fuente interna (equipo)
        ↓
   /guia (HTML)   →  vista limpia para cliente · PDF
```

No publiques el portal `/mrg/` crudo al cliente: contiene Sprint, ALIGN y gaps.

→ Matriz completa: [ACCESS.md](../ACCESS.md) · código: `app/docs_access.py`

Esto cubre **equipo interno**, **prospectos** e **integradores** en la misma app. Cuando convenga un sitio estático dedicado, la misma matriz se replica en MkDocs/Docusaurus.

---

## Resumen práctico

| Destino | Qué publicar |
|---------|--------------|
| **Sitio público** | MBB · MAG · MSD · `/guia` · brochure / one-pager / MTX-CASE · Release Notes |
| **Portal interno / intranet** | MCM · MPA · MDL · MUX · MRL · MDO · Developer · MKT capítulos · **MRG Markdown** |

No mezclar playbooks comerciales ni arquitectura interna en el sitio público.

---

## Opciones evaluadas

| Herramienta | Fortalezas | Para Roustix |
|-------------|------------|--------------|
| **MkDocs** | Simple · Markdown nativo · Material theme · rápido de montar | ✅ Buen fit inicial — ya tenemos `.md` |
| **Docusaurus** | React · versioning · blog · i18n | ✅ Si crece comunidad o docs multidioma |
| **Flask actual** | Cero infra extra · gate híbrido · catálogos HTML | ✅ Mantener para hub + preview internos |

**Recomendación por fases:**

1. **Ahora:** Flask + `DOCS_ACCESS_POLICY=hybrid` + índice maestro
2. **Público v1:** MkDocs Material **solo** con nav pública (MBB · MKT · MAG · MSD · MRG)
3. **Intranet:** mismo repo, build filtrado o SSO delante de los manuales privados
4. **Escala:** Docusaurus si versioning público, búsqueda avanzada o portal partners

---

## Requisitos previos al sitio público estático

- [x] Política de acceso documentada ([ACCESS.md](../ACCESS.md))
- [ ] [VERSIONS.md](../VERSIONS.md) estable por 2+ releases
- [ ] Todos los manuales core con changelog
- [ ] [CROSS-REFERENCES.md](../CROSS-REFERENCES.md) aplicado
- [ ] Dominio definido (ej. `docs.roustix.com`)
- [ ] Build que **excluya** MCM · MPA · Developer · MDL · MUX del artefacto público

---

## Estructura MkDocs (borrador · solo público)

```yaml
# mkdocs.yml (futuro — sitio público)
site_name: Roustix Documentation
nav:
  - Inicio: README.md
  - Brand Book: brandbook/README.md
  - Marketing assets: mkt/assets/
  - Casos: mkt/mtx-case/
  - Producto (MRG): mrg/README.md
  - API (MAG): mag/README.md
  - SDK (MSD): msd/README.md
  - Release Notes: release-notes/README.md
```

**No incluir en el build público:** `mcm/`, `mpa/`, `mdl/`, `mux/`, `mrl/`, `mdo/`, `developer/`, `mkt/chapters/`, `mkt/index.html`.

---

## Variable de entorno (Flask)

```bash
# Producción / desarrollo (recomendado)
DOCS_ACCESS_POLICY=hybrid

# Solo debugging local
DOCS_ACCESS_POLICY=open

# Paranoia: todo detrás de login
DOCS_ACCESS_POLICY=locked
```

---

## No hacer

- No publicar MCM (playbooks / objeciones) en el sitio público
- No exponer MPA ni Developer Docs sin autenticación
- No duplicar contenido en wiki externa sin filtro de acceso
- No mezclar docs internas con el portal público «por comodidad»

---

→ [ACCESS.md](../ACCESS.md) · [DOCUMENTATION-PRODUCT.md](../DOCUMENTATION-PRODUCT.md) · [Índice maestro](../index.html)
