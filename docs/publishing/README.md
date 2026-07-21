# Publicación · Sitio de documentación

**Suite docs · Publicación futura**

Hoy Roustix sirve documentación desde la app Flask:

| Ruta | Contenido |
|------|-----------|
| `/docs/` | Índice maestro |
| `/brandbook/` | MBB |
| `/mdl/` | MDL |
| `/mux/` | MUX |
| `/mcm/` | MCM |
| `/mpa/` | MPA |

Esto es suficiente para **equipo interno** y desarrollo. Cuando la documentación deba ser **pública** (clientes, partners, inversionistas), conviene un sitio estático dedicado.

---

## Opciones evaluadas

| Herramienta | Fortalezas | Para Roustix |
|-------------|------------|--------------|
| **MkDocs** | Simple · Markdown nativo · Material theme · rápido de montar | ✅ Buen fit inicial — ya tenemos `.md` |
| **Docusaurus** | React · versioning · blog · i18n | ✅ Si crece comunidad o docs multidioma |
| **Flask actual** | Cero infra extra · catálogos HTML ricos | ✅ Mantener para previews internos |

**Recomendación por fases:**

1. **Ahora:** Flask + índice maestro + VERSIONS + cross-refs
2. **Público v1:** MkDocs Material desde `docs/` + export de catálogos HTML como referencia
3. **Escala:** Docusaurus si versioning público, búsqueda avanzada o portal partners

---

## Requisitos previos al sitio público

- [ ] [VERSIONS.md](../VERSIONS.md) estable por 2+ releases
- [ ] Todos los manuales core con changelog
- [ ] [CROSS-REFERENCES.md](../CROSS-REFERENCES.md) aplicado
- [ ] MPA v1.0 congelado
- [ ] Política de versionado comunicada ([VERSIONING.md](../VERSIONING.md))
- [ ] Dominio definido (ej. `docs.roustix.com`)

---

## Estructura MkDocs (borrador)

```yaml
# mkdocs.yml (futuro)
site_name: Roustix Documentation
nav:
  - Inicio: README.md
  - Brand Book: brandbook/README.md
  - MDL: mdl/README.md
  - MUX: mux/README.md
  - MCM: mcm/README.md
  - MPA: mpa/README.md
  - Versiones: VERSIONS.md
  - Changelog: changelog.md
```

Los catálogos HTML interactivos pueden enlazarse como «Vista visual» desde cada sección.

---

## No hacer aún

- No duplicar contenido en wiki externa
- No publicar docs sin versión congelada
- No mezclar docs internas (Developer) con portal público sin filtro

---

→ [DOCUMENTATION-PRODUCT.md](../DOCUMENTATION-PRODUCT.md) · [Índice maestro](../README.md)
