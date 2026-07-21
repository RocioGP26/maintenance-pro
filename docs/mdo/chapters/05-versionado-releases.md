# MDO-05 · Versionado, Publicación y Ciclo de Vida de la Documentación

**Código:** MDO-05 · Sprint 13.5 · **Entregado**

> La documentación de Roustix es un **producto vivo**. Cada cambio debe ser trazable, versionado y publicado de forma controlada para garantizar que usuarios, implementadores, desarrolladores y partners consulten siempre una **fuente oficial**.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MDO-01 · Filosofía](01-introduccion-portal.md) · [MDO-02 · Arquitectura](02-arquitectura-documentacion.md) · [MDO-03 · Uso del Portal](03-guia-usuarios.md) · [MDO-04 · Colaboradores](04-guia-colaboradores.md)

---

## Objetivo del capítulo

Definir las reglas oficiales de **versionado**, **publicación** y **ciclo de vida** de toda la documentación Roustix.

Este capítulo establece cómo evoluciona la suite, cómo se registran los cambios y cómo se garantiza que lo publicado sea **oficial, trazable y consistente** con el producto.

---

## 1 · Filosofía

La documentación **no es estática**.

Evoluciona con el producto, pero mantiene **releases propios** — el software y la documentación avanzan juntos, **no al mismo ritmo**.

| Principio | Significado |
|-----------|-------------|
| **Trazabilidad** | Todo cambio importante deja rastro |
| **Oficialidad** | Solo lo versionado y publicado es referencia válida |
| **Independencia** | Cada manual puede evolucionar sin bloquear a los demás |
| **Coherencia** | La suite agregada refleja el estado global |
| **Honestidad** | Producción, diseño y roadmap se distinguen siempre |

→ Manifiesto: [DOCUMENTATION-PRODUCT.md](/docs/DOCUMENTATION-PRODUCT.md)

---

## 2 · Niveles de versionado

Roustix documenta en **tres niveles**.

```
Suite documental (v1.13.0)
    │
    ├── Manual (MRG v1.0.0 · MCM v1.0.0 · MDO v0.5.1…)
    │       │
    │       └── Capítulo (MRG-03 · MDO-05…)
    │
    └── Release Git (docs-v1.13)
```

| Nivel | Ejemplo | Registro |
|-------|---------|----------|
| **Suite** | `v1.13.0` | [VERSIONS.md](/docs/VERSIONS.md) · [changelog.md](/docs/changelog.md) |
| **Manual** | `MRG v1.0.0` | `{manual}/changelog.md` |
| **Capítulo** | `MDO-05` | Metadatos en el propio capítulo · [NOMENCLATURE.md](/docs/NOMENCLATURE.md) |

---

## 3 · Semver documental

Toda documentación utiliza **versionado semántico**.

**Formato:** `MAJOR.MINOR.PATCH`

| Bump | Cuándo | Ejemplo |
|------|--------|---------|
| **MAJOR** | Reescritura, reestructura, cambio de posicionamiento | MBB `v2.0` |
| **MINOR** | Capítulo nuevo, sección amplia, nuevo código PLAY/OBJ | MPA `v1.0` → `v1.1` |
| **PATCH** | Typo, enlace, aclaración sin cambiar significado | MRG `v1.0.0` → `v1.0.1` |

> **Regla:** un cambio importante **no modifica la edición vigente en silencio**. Abre una nueva versión y se registra en el changelog.

→ Política completa: [VERSIONING.md](/docs/VERSIONING.md)

---

## 4 · Changelog

Todo cambio significativo se registra en **tres capas** cuando aplica.

| Capa | Archivo | Cuándo actualizar |
|------|---------|-------------------|
| **Suite** | [docs/changelog.md](/docs/changelog.md) | Hitos transversales · nuevo manual · bump de suite |
| **Manual** | `{manual}/changelog.md` | Cualquier cambio del dominio |
| **Release** | [release-notes/](/docs/release-notes/) | Releases oficiales con tag Git |

### Formato de entrada

```markdown
## [1.13.0] — 2026-07-10 · MDO v0.5.0

### Added
- MDO-05 · Versionado y ciclo de vida

### Changed
- MDO v0.4.0 → v0.5.0
```

---

## 5 · Ciclo de vida de un documento

Cada documento atraviesa **estados definidos** desde su concepción hasta su retiro.

En proyectos grandes existen **dos revisiones distintas** antes de publicar:

- **Revisión técnica** — exactitud funcional (producto)
- **Revisión editorial** — calidad documental (MDO)

```
📋 Planificado
    ↓
🟡 En desarrollo
    ↓
🔄 Revisión técnica
    ↓
📝 Revisión editorial
    ↓
✅ Publicado  ← referencia oficial
    ↓
📦 Archivado / ❌ Obsoleto
```

| Estado | Responsable | Uso permitido | Publicación |
|--------|-------------|---------------|-------------|
| 📋 **Planificado** | Producto / autor | Diseño · roadmap | No |
| 🟡 **En desarrollo** | Autor | Borrador interno | No |
| 🔄 **Revisión técnica** | Producto · QA | Validación de exactitud | Preview interno |
| 📝 **Revisión editorial** | Documentación (MDO) | Formato · tono · cross-refs | Preview interno |
| ✅ **Publicado** | MDO · Dirección | Referencia oficial | Sí |
| 📦 **Archivado** | Documentación | Histórico | Solo lectura |
| ❌ **Obsoleto** | Documentación | No utilizar | Retirado del índice activo |

> Antes de citar un documento como fuente oficial, **verificar estado y versión**.  
> En metadatos de sprint, «Entregado» indica que el capítulo completó su entrega; el estado en portal debe ser **✅ Publicado**.

→ Estados editoriales: [MDO-04 §5](04-guia-colaboradores.md#5--estados-permitidos)

---

## 6 · Ciclo de vida de un manual

Un manual completo sigue el mismo espíritu a mayor escala.

| Fase | Descripción |
|------|-------------|
| **Inicio** | Primer capítulo · `v0.1.0` · Sprint activo |
| **Desarrollo** | Capítulos incrementales · bumps MINOR |
| **Completo** | Exit Criteria del manual cumplido · `v1.0.0` |
| **Congelado** | Cambios solo PATCH o MINOR acordados |
| **Evolución** | Nuevos capítulos · MAJOR si hay reestructura |

### Manuales congelados (Fundación 1.0)

| Manual | Versión | Estado |
|--------|---------|--------|
| MBB | v2.0 | ✔ Congelado |
| MDL | v1.0 | ✔ Congelado |
| MUX | v1.2 | ✔ Congelado |
| MPA | v1.0 | ✔ Congelado |

---

## 7 · Flujo de publicación

Ningún documento llega al portal sin pasar por el **flujo oficial**.

```
Borrador
    ↓
Revisión técnica (exactitud)
    ↓
Revisión editorial (MDO-04)
    ↓
Bump de versión
    ↓
Changelog actualizado
    ↓
Índice / portada sincronizados
    ↓
Publicación en /docs/
```

### Checklist de publicación

- [ ] Versión actualizada en [VERSIONS.md](/docs/VERSIONS.md)
- [ ] Entrada en `{manual}/changelog.md`
- [ ] Si afecta suite → [changelog.md](/docs/changelog.md)
- [ ] Cross-refs verificadas → [CROSS-REFERENCES.md](/docs/CROSS-REFERENCES.md)
- [ ] Estado del capítulo = ✅ Publicado
- [ ] Índice del manual (`index.html` / README) sincronizado
- [ ] Enlaces HTTP verificados (200)

→ Flujo de contribución: [MDO-04 §10](04-guia-colaboradores.md#10--flujo-de-contribución)

---

## 8 · Compatibilidad documentación ↔ producto

La documentación y el **software de aplicación** no comparten semver.

```
Roustix App (semver app)          Roustix Docs (semver docs)
        │                                  │
        ├─ features                        ├─ MRG describe operación
        ├─ migraciones BD                  ├─ MAG describe API
        └─ releases app                    └─ releases docs-v1.x
```

| Situación | Acción documental |
|-----------|-------------------|
| Nueva funcionalidad en producción | Actualizar MRG · bump MINOR o PATCH |
| Feature en roadmap | Documentar como 📋 o 🟡 · nunca como ✅ Publicado |
| Breaking change en API | MAG MAJOR · MSD actualizado · changelog |
| Cambio solo comercial | MCM/MKT · sin bump de MRG |
| Reestructura documental | Suite MAJOR · tag `docs-vX.0` |

> **No es 1:1.** Un release de app puede no requerir bump de MBB. Un nuevo capítulo MPA puede subir la suite sin release de app.

---

## 9 · Releases oficiales

Los **releases documentales** se marcan con tags Git.

| Tag | Significado |
|-----|-------------|
| `docs-v1.0` | Primera edición oficial congelada |
| `docs-foundation-1.0` | Fundación MBB · MDL · MUX · MPA |
| `docs-v1.13` | Suite con MDO Sprint 13 *(futuro)* |

### Definición de «hecho» para un release

- [ ] [VERSIONS.md](/docs/VERSIONS.md) actualizado
- [ ] [changelog.md](/docs/changelog.md) con entrada
- [ ] Changelogs de manuales afectados
- [ ] Índice [/docs/](/docs/) sincronizado
- [ ] Cross-refs verificadas
- [ ] Tag Git `docs-vX.Y`
- [ ] [RELEASE-vX.Y.md](/docs/RELEASE-v1.0.md) si es hito mayor

---

## 10 · Publicación por entorno

La misma estructura de archivos se publica en distintos **entornos**.

| Entorno | URL / motor | Audiencia |
|---------|-------------|-----------|
| **Desarrollo** | Flask local `127.0.0.1:5000` | Equipo interno |
| **Portal interno** | `/docs/` · `/mdo/` · manuales | Roustix · partners |
| **Estático** | GitHub Pages · MkDocs · Docusaurus | Público futuro |
| **Export** | PDF por manual | Comercial · partners |

> La **estructura de carpetas no cambia** según el motor de publicación.

→ Plan público: [publishing/README.md](/docs/publishing/README.md) *(cuando exista)*

---

## 11 · Retiro y archivo

Cuando un documento deja de ser válido:

1. Cambiar estado a **❌ Obsoleto** o **📦 Archivado**
2. Registrar en `changelog.md` del manual
3. Retirar del índice activo (mantener archivo con aviso)
4. Actualizar cross-refs que apunten al documento
5. Indicar documento sustituto si existe

**Nunca eliminar silenciosamente** contenido que fue referencia oficial.

---

## 12 · Responsabilidades

| Rol | Responsabilidad en versionado |
|-----|------------------------------|
| **Autor** | Borrador · bump propuesto · changelog del capítulo |
| **Producto** | Exactitud funcional · alineación MRG ↔ app |
| **Documentación (MDO)** | Calidad editorial · VERSIONS.md · suite changelog |
| **Dirección** | Aprobación de releases mayores · freeze |
| **Desarrollo** | MAG/MSD alineados con API real |

---

## 13 · Política de compatibilidad entre manuales

Un cambio en un manual **puede obligar** a actualizar otros dominios. Esta política evita documentación desalineada.

| Cambio | Debe actualizar |
|--------|-----------------|
| **Nuevo módulo de producto** | MPA · MRG · MCM · MKT |
| **Nuevo endpoint API** | MAG · MSD |
| **Nuevo rol** | MRG · MUX |
| **Cambio visual importante** | MDL · MUX |
| **Cambio de marca** | MBB · MCM · MKT |

### Reglas

1. **El manual origen** registra el cambio en su `changelog.md`.
2. **Manuales dependientes** se actualizan en el mismo sprint o se documenta la deuda en [MDO-06](06-catalogo-documental.md).
3. **Cross-refs** se verifican en [CROSS-REFERENCES.md](/docs/CROSS-REFERENCES.md).
4. Si el cambio es **roadmap**, solo el manual origen lo marca como 📋 o 🟡 — los demás no anticipan producción.

→ Compatibilidad docs ↔ app: [§8](#8--compatibilidad-documentación--producto)

---

## 14 · Matriz de madurez documental

Cuando la suite crezca a **300–400 capítulos**, cada documento debe poder clasificarse por **nivel de madurez**.

| Nivel | Estado | Significado |
|-------|--------|-------------|
| **Nivel 1** | Existe borrador | Contenido inicial · 🟡 En desarrollo |
| **Nivel 2** | Revisado técnicamente | Producto validó exactitud · 🔄 Revisión técnica superada |
| **Nivel 3** | Publicado | ✅ Publicado en portal · referencia usable |
| **Nivel 4** | Referenciado | Otros manuales enlazan este documento como fuente |
| **Nivel 5** | Congelado | Versión estable · cambios solo PATCH o acordados |

### Uso

- **MDO-06 Catálogo** reportará madurez por manual y capítulo.
- **Nivel 4** confirma que el documento es parte activa del ecosistema, no un silo.
- **Nivel 5** aplica a Fundación 1.0 (MBB · MDL · MUX · MPA) y manuales completos congelados.

```
Nivel 1 → 2 → 3 → 4 → 5
borrador   técnico   publicado   referenciado   congelado
```

---

## Relación con otros documentos

| Documento | Relación |
|-----------|----------|
| [MDO-02](02-arquitectura-documentacion.md) | Estructura y convenciones |
| [MDO-04](04-guia-colaboradores.md) | Estándares editoriales y flujo |
| [MDO-06](06-catalogo-documental.md) | Catálogo y estado de manuales |
| [MDO-09](09-gobierno-documental.md) | Gobierno y auditoría *(incorporado en MDO-10)* |
| [VERSIONING.md](/docs/VERSIONING.md) | Política semver |
| [VERSIONS.md](/docs/VERSIONS.md) | Registro oficial |
| [DOCUMENTATION-PRODUCT.md](/docs/DOCUMENTATION-PRODUCT.md) | Producto documental |

---

## Exit Criteria

- [x] Versionado por suite, manual y capítulo definido
- [x] Semver y reglas de bump documentadas
- [x] Ciclo de vida de documentos y manuales establecido
- [x] Flujo de publicación y checklist definidos
- [x] Compatibilidad docs ↔ producto explicada
- [x] Releases oficiales y retiro documentados
- [x] Política de compatibilidad entre manuales definida
- [x] Matriz de madurez documental establecida

---

## Filosofía del capítulo

Una documentación confiable **no es la que nunca cambia**.

Es la que **cambia con trazabilidad**: cada versión tiene autor, fecha, motivo y registro.

Roustix trata la documentación como producto porque **la confianza del cliente depende de saber qué es oficial, qué está en roadmap y qué quedó atrás**.

---

## Estado

| Aspecto | Estado |
|---------|--------|
| Versionado documental | ✅ Definido |
| Ciclo de vida | ✅ Documentado |
| Flujo de publicación | ✅ Establecido |
| Compatibilidad entre manuales | ✅ Definida |
| Matriz de madurez | ✅ Establecida |
| MDO-05 | ✅ Entregado |
| Sprint 13 | 🚧 En progreso |

---

← [MDO-04](04-guia-colaboradores.md) · [Índice MDO](/mdo/) · [MDO-06](06-catalogo-documental.md) →
