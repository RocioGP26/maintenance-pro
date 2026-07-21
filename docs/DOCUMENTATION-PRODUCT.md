# Roustix Documentation · Producto independiente

**Roustix Documentation Suite** no es un apéndice del repositorio. Es un **producto documental** con su propia versión, changelog, índice maestro y estándares de calidad.

> El software y la documentación evolucionan juntos, pero **no al mismo ritmo**. La documentación tiene releases propios.

---

## Por qué tratarla como producto

| Audiencia | Qué necesita de la documentación |
|-----------|----------------------------------|
| **Clientes y prospectos** | Confianza, narrativa coherente, profesionalismo |
| **Desarrolladores** | Onboarding rápido, arquitectura clara, reglas explícitas |
| **Socios** | Misma historia en marca, producto y comercial |
| **Inversionistas** | Señal de madurez: no solo código, sino **sistema de conocimiento** |

Un producto documental bien versionado comunica: *«esto se mantiene, se revisa y se respeta»*.

---

## Los cinco pilares del producto documental

### 1 · Versiones oficiales

Cada manual tiene versión semver propia (`v1.0`, `v1.1`, `v2.0`).  
La **suite completa** también tiene versión agregada.

→ Registro único: [VERSIONS.md](VERSIONS.md)  
→ Política: [VERSIONING.md](VERSIONING.md)

### 2 · Control de cambios

Todo cambio significativo deja rastro:

| Nivel | Archivo |
|-------|---------|
| Suite | [changelog.md](changelog.md) |
| Por manual | `{manual}/changelog.md` |
| Releases | [release-notes/](release-notes/) · tags Git `docs-v*` |

### 3 · Índice maestro

Un solo punto de entrada:

- **Visual:** [/docs/](http://127.0.0.1:5000/docs/) · `index.html`
- **Markdown:** [README.md](README.md)
- **Nomenclatura:** [NOMENCLATURE.md](NOMENCLATURE.md)

### 4 · Referencias cruzadas

Los manuales no viven aislados. Se enlazan con convenciones fijas:

**MBB ↔ MDL ↔ MUX ↔ MCM ↔ MPA**

→ Matriz y reglas: [CROSS-REFERENCES.md](CROSS-REFERENCES.md)

### 5 · Sitio público (futuro)

Hoy la documentación se sirve desde Flask (`/docs/`, `/brandbook/`, `/mpa/`…).  
Cuando llegue el momento de hacerla **pública** para clientes y partners:

→ Plan: [publishing/README.md](publishing/README.md) (MkDocs · Docusaurus)

---

## Relación software ↔ documentación

```
Roustix App (semver app)          Roustix Docs (semver docs)
        │                                  │
        ├─ features                        ├─ MPA describe plataforma
        ├─ migraciones BD                  ├─ MCM describe venta
        └─ releases                        └─ releases docs-v1.0, docs-v1.1…
```

**No es 1:1.** Un release de app puede no requerir bump de MBB. Un nuevo capítulo MPA puede subir la suite sin release de app.

---

## Definición de «hecho» para un release documental

- [ ] Versiones actualizadas en [VERSIONS.md](VERSIONS.md)
- [ ] Entrada en [changelog.md](changelog.md)
- [ ] Changelogs de manuales afectados
- [ ] Índice `/docs/` sincronizado
- [ ] Cross-refs verificadas ([CROSS-REFERENCES.md](CROSS-REFERENCES.md))
- [ ] Tag Git `docs-vX.Y` (releases internos oficiales)
- [ ] [RELEASE-vX.Y.md](RELEASE-v1.0.md) si es hito mayor

---

## Estado actual

**Suite:** v1.2 · **Último tag:** `docs-v1.0` (próximo: `docs-v1.2` al cerrar hito)

→ [VERSIONS.md](VERSIONS.md) · [Índice maestro](README.md)

---

*Roustix Documentation · Producto independiente · 2026*
