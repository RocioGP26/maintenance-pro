# MDO-08 · Portal Documental

**Código:** MDO-08 · Sprint 13.8 · **Entregado**

> El portal documental es el **producto de lectura** de Roustix Docs: la capa que convierte manuales dispersos en una experiencia unificada, navegable y profesional.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MDO-02 · Arquitectura](02-arquitectura-documentacion.md) · [MDO-06 · Catálogo](06-catalogo-documental.md) · [MDO-07 · Roadmap](07-roadmap-evolucion.md)

---

## Objetivo del capítulo

Describir el **portal como producto**: arquitectura, componentes de interfaz, integraciones y criterios de experiencia para `/docs/` y dominios asociados.

Este capítulo es el **manual del portal** — referencia para diseño, desarrollo y evolución del sitio documental.

---

## 1 · Filosofía

El portal no es un listado de enlaces. Es la **puerta de entrada** al ecosistema de conocimiento Roustix.

| Principio | Aplicación |
|-----------|------------|
| **Un solo hub** | `/docs/` concentra el acceso |
| **Consistencia** | Misma estructura en todos los manuales |
| **Estado visible** | Versión y madurez siempre visibles |
| **Preparado para escalar** | Nuevos manuales sin rehacer el shell |

---

## 2 · Arquitectura del portal `/docs`

```
Usuario
    ↓
/docs/  (índice maestro · docs/index.html)
    ↓
Blueprint Flask (docs_routes.py · {manual}_routes.py)
    ↓
docs/{manual}/  (Markdown + index.html + assets)
```

| Capa | Implementación actual |
|------|------------------------|
| **Hub** | `docs/index.html` · `docs_hub` blueprint |
| **Manuales** | `/brandbook/` · `/mdl/` · `/mux/` · `/mpa/` · `/mag/` · `/msd/` · `/mrg/` · `/mcm/` · `/mkt/` · `/mdo/` |
| **Registro** | [VERSIONS.md](/docs/VERSIONS.md) · [changelog.md](/docs/changelog.md) |
| **Estáticos** | `docs/css/docs-hub.css` · CSS por manual |

→ Arquitectura lógica: [MDO-02](02-arquitectura-documentacion.md)

---

## 3 · Homepage

La homepage del portal (`/docs/`) debe comunicar:

1. **Qué es Roustix Docs** — suite documental oficial
2. **Versión de la suite** — banner de release
3. **Acceso rápido** — cards por manual
4. **Tagline** — *Toda la operación. Una sola plataforma.*

### Componentes actuales

| Componente | Función |
|------------|---------|
| `docs-release` | Banner de versión y sprint |
| `docs-hero` | Título · árbol de suite |
| `docs-grid` | Cards de manuales |
| `docs-nav` | Sidebar sticky |

### Componentes objetivo (v2.x)

- Buscador global en header
- Selector de versión de suite
- Acceso por audiencia (cliente · dev · comercial)

---

## 4 · Índices automáticos

Los índices se generan desde **metadatos estructurados**, no manualmente.

| Fuente | Genera |
|--------|--------|
| [VERSIONS.md](/docs/VERSIONS.md) | Tabla de manuales · versiones · URLs |
| `{manual}/NOMENCLATURE.md` | Capítulos por código |
| `{manual}/index.html` | Vista visual por sprint |
| `{manual}/README.md` | Resumen markdown |

**Roadmap v3.x:** script CI que sincronice VERSIONS → índice HTML → catálogo MDO-06.

---

## 5 · Navegación lateral

Patrón estándar (implementado en MDO, MKT, MCM, MRG…):

```
┌─────────────────┐
│ Wordmark + meta │
├─────────────────┤
│ Grupo Sprint    │
│ · Capítulo 01   │
│ · Capítulo 02   │
├─────────────────┤
│ Meta            │
│ · NOMENCLATURE  │
│ · Changelog     │
└─────────────────┘
```

| Regla |
|-------|
| Sidebar **sticky** · altura 100vh · scroll interno |
| Enlaces a capítulos **ancla** (`#mdo-01`) + markdown |
| Estado visual: `is-done` · `is-planned` |
| Link a `/docs/` en meta de cada manual |

---

## 6 · Breadcrumbs

Patrón objetivo:

```
Roustix Docs  ›  MDO  ›  MDO-08 · Portal Documental
```

| Nivel | Ejemplo |
|-------|---------|
| 1 | Roustix Docs → `/docs/` |
| 2 | Manual → `/mdo/` |
| 3 | Capítulo → `chapters/08-portal-docs.md` |

**Estado:** 📋 Planificado en shell unificado (v2.x). Hoy: navegación por sidebar + enlaces entre capítulos.

---

## 7 · Version selector

Permite consultar documentación de **releases anteriores** cuando aplique.

| Alcance | Comportamiento |
|---------|----------------|
| **Suite** | Selector `v1.13` · `v1.12` … en header |
| **Manual** | Badge en card y portada (`v1.0.0`) |
| **Capítulo** | Metadatos en encabezado markdown |

→ Registro: [VERSIONS.md](/docs/VERSIONS.md) · Política: [MDO-05](05-versionado-releases.md)

---

## 8 · Dark mode

Alineado con [MDL](/mdl/) y [MUX](/mdl/dark-mode.md):

| Estado | Notas |
|--------|-------|
| **Fundación** | Manuales MBB/MDL definen tokens dark |
| **Portal v2.x** | Toggle en header · `prefers-color-scheme` |
| **Persistencia** | `localStorage` · misma convención que app |

No implementar dark mode aislado por manual — debe ser **global del portal**.

---

## 9 · Responsive

El portal debe ser usable en:

| Viewport | Comportamiento |
|----------|----------------|
| **Desktop** | Sidebar fijo + contenido scroll |
| **Tablet** | Sidebar colapsable |
| **Mobile** | Nav hamburger · cards apiladas |

CSS base: `docs-hub.css` · grid `docs-shell` → columna única en breakpoints futuros.

---

## 10 · Cards de manuales

Cada manual en `/docs/` se presenta como **card**:

| Elemento | Contenido |
|----------|-----------|
| Número suite | `01` · `12` · `13` |
| Nombre | MRG · MCM · MDO |
| Código | `Roustix Reference Guide` |
| Descripción | Una línea de propósito |
| Badge | Versión · estado · sprint |
| Link | URL del manual |

Ejemplo actual: sección `#suite` en [docs/index.html](/docs/).

---

## 11 · Estado de cada manual

Cada card muestra **estado documental**:

| Badge | Significado |
|-------|-------------|
| ✔ Congelado | Fundación 1.0 |
| ✅ Sprint N | Manual v1 entregado |
| 🟡 En curso | Desarrollo activo |
| 📋 Planificado | Sin contenido |

Sincronizado con [MDO-06 · Catálogo](06-catalogo-documental.md).

---

## 12 · Integración con Git

| Práctica | Descripción |
|----------|-------------|
| **Docs en repo** | `docs/` versionado con el código |
| **Tags** | `docs-v1.13` · `docs-foundation-1.0` |
| **Changelog** | Entrada por release en `docs/changelog.md` |
| **PR review** | Cambios doc siguen MDO-04 · MDO-05 |

Flujo: merge → bump VERSIONS → tag opcional → deploy portal.

---

## 13 · Integración con Mintlify (roadmap)

[Mintlify](https://mintlify.com) (u homólogo: Docusaurus · MkDocs) como motor de publicación **v2.x**:

| Ventaja |
|---------|
| Búsqueda nativa |
| Sidebar auto desde `mint.json` |
| API reference integrada (MAG) |
| Versionado y preview por branch |

| Requisito |
|-----------|
| Mantener **misma estructura** `docs/{manual}/chapters/` |
| Export o sync desde repo Git |
| No duplicar contenido — una fuente en repo |

→ Plan: [publishing/README.md](/docs/publishing/README.md) *(cuando exista)* · [MDO-07 §3](07-roadmap-evolucion.md#3--roadmap-documental)

---

## Relación con otros documentos

| Documento | Relación |
|-----------|----------|
| [MDO-03](03-guia-usuarios.md) | Uso del portal |
| [MDO-09](09-busqueda.md) | Búsqueda e indexación |
| [MDO-06](06-catalogo-documental.md) | Catálogo de manuales |
| [/docs/](/docs/) | Portal en producción (dev) |

---

## Exit Criteria

- [x] Arquitectura del portal documentada
- [x] Componentes UI definidos (home · sidebar · cards · breadcrumbs)
- [x] Version selector y responsive especificados
- [x] Integración Git y Mintlify descritas

---

## Filosofía del capítulo

El portal es la **cara pública** del conocimiento Roustix. Debe sentirse tan cuidado como el producto que documenta.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| Especificación portal | ✅ Definida |
| Implementación shell v2 | 🟡 Roadmap |
| MDO-08 | ✅ Entregado |

---

← [MDO-07](07-roadmap-evolucion.md) · [Índice MDO](/mdo/) · [MDO-09](09-busqueda.md) →
