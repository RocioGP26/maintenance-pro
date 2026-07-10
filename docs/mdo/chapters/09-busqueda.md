# MDO-09 · Búsqueda, Navegación e Indexación

**Código:** MDO-09 · Sprint 13.9 · **Entregado**

> En un ecosistema de cientos de capítulos, **encontrar** información es tan crítico como escribirla bien.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MDO-03 · Uso del portal](03-guia-usuarios.md) · [MDO-06 · Catálogo](06-catalogo-documental.md) · [MDO-08 · Portal](08-portal-docs.md)

---

## Objetivo del capítulo

Definir cómo los usuarios **encuentran información** en Maintix Docs: búsqueda global, índices, tags, cross-references, URLs permanentes y estrategias anti-duplicación.

---

## 1 · Filosofía

| Principio | Significado |
|-----------|-------------|
| **Buscar antes de navegar** | Si conoces el tema, usa search |
| **Código primero** | `MRG-03` es más rápido que scroll |
| **Un tema, un lugar** | Search debe llevar al documento canónico |
| **URLs estables** | Enlaces que no envejecen |

---

## 2 · Search global

Buscador unificado en el portal — **objetivo v2.x**.

### Qué indexar

| Campo | Peso |
|-------|------|
| Código (`MDO-09`, `MRG-03`) | Alto |
| Título del capítulo | Alto |
| Encabezados H2–H3 | Medio |
| Cuerpo markdown | Medio |
| Tags / categoría | Medio |

### MVP (implementación incremental)

1. **Índice JSON** generado desde `NOMENCLATURE.md` de cada manual
2. **Client-side search** (MiniSearch · Lunr) en `/docs/`
3. **Mintlify search** en migración v2.x

### Ejemplos de consulta

| Query | Resultado esperado |
|-------|-------------------|
| `OT` | MRG · mantenimiento |
| `JWT` | MAG · MSD |
| `MCM-04` | Planes SaaS |
| `ICP` | MCM appendix |
| `Tenant` | MRG-01 · glosario |

→ Guía usuario: [MDO-03 §6–7](03-guia-usuarios.md#6--uso-del-buscador)

---

## 3 · Índices

| Índice | Ubicación | Contenido |
|--------|-----------|-----------|
| **Maestro** | [/docs/](/docs/) | Todos los manuales |
| **Por manual** | `/mdo/` · `/mrg/` … | Capítulos del dominio |
| **Nomenclatura** | `NOMENCLATURE.md` | Códigos oficiales |
| **VERSIONS** | [VERSIONS.md](/docs/VERSIONS.md) | Versiones y URLs |
| **Catálogo** | [MDO-06](06-catalogo-documental.md) | Estado y cobertura |

Regla: **no mantener índices duplicados** — enlazar al canónico.

---

## 4 · Tags

Tags agrupan contenido **transversal** a manuales.

| Tag | Ejemplos |
|-----|----------|
| `producto` | MRG |
| `api` | MAG · MSD |
| `comercial` | MCM |
| `marketing` | MKT |
| `gobierno` | MDO |
| `sector-manufactura` | MCM-05 · MTX-CASE |

Formato futuro en frontmatter:

```yaml
tags: [producto, inventario, mrg]
audience: [implementador, admin]
```

---

## 5 · Cross references

Referencias cruzadas explícitas en cada capítulo.

| ✅ Correcto | ❌ Incorrecto |
|-------------|---------------|
| → [MRG-03 Inventario](/mrg/) | «Ver manual de producto» |
| → [MAG-02 Auth](/mag/) | Copiar sección completa |

→ Matriz: [CROSS-REFERENCES.md](/docs/CROSS-REFERENCES.md) · [MDO-02 §8](02-arquitectura-documentacion.md#8--referencias-cruzadas)

---

## 6 · Categorías

Organización por **dominio de conocimiento** (no por equipo):

| Categoría | Manuales |
|-----------|----------|
| Producto | MRG |
| Plataforma | MPA · MAG · MSD |
| Comercial | MCM · MKT |
| Experiencia | MUX · MDL · MRL |
| Marca | MBB |
| Documentación | MDO |

---

## 7 · SEO documental

Para portal público futuro:

| Práctica |
|----------|
| Título único por página: `{Código} · {Título} · Maintix Docs` |
| Meta description desde objetivo del capítulo |
| URLs legibles: `/mrg/chapters/03-inventario` |
| `lang="es"` en HTML |
| Sitemap generado desde catálogo MDO-06 |
| `robots.txt` en producción |

---

## 8 · URLs permanentes

| Regla |
|-------|
| El **código** del capítulo no cambia (`MDO-09`) |
| El slug del archivo puede evolucionar con redirect |
| Rutas Flask: `/{manual}/chapters/{file}.md` |
| No usar IDs opacos en URLs públicas |

Ejemplo estable:

```
https://docs.maintix.com/mdo/chapters/09-busqueda
```

---

## 9 · Redirecciones

Cuando un capítulo se renombra o mueve:

1. Mantener redirect 301 en servidor
2. Actualizar [CROSS-REFERENCES.md](/docs/CROSS-REFERENCES.md)
3. Entrada en `changelog.md` del manual
4. No dejar enlaces rotos > 1 sprint

Legacy conocido: `docs/architecture/` → MPA · ver [NOMENCLATURE.md](/docs/NOMENCLATURE.md).

---

## 10 · Convenciones de nombres

| Patrón | Uso |
|--------|-----|
| `{NN}-{slug}.md` | Capítulos |
| `MTX-CASE-{NNN}` | Casos marketing |
| `PLAY-{NNN}` | Demos comerciales |
| `OBJ-{NNN}` | Objeciones |

Evitar: `final.md` · `v2.md` · `copia.md`

→ [MDO-02 §6](02-arquitectura-documentacion.md#6--convención-de-archivos) · [MDO-04 §6](04-guia-colaboradores.md#6--terminología-oficial)

---

## 11 · Organización del contenido

Jerarquía de lectura recomendada:

```
Código conocido → Search / NOMENCLATURE
    ↓
Manual correcto → Índice del manual
    ↓
Capítulo → Cross-refs relacionados
    ↓
Apéndice / material si profundiza
```

---

## 12 · Evitar contenido duplicado

| Estrategia | Acción |
|------------|--------|
| **Un tema, un lugar** | MRG explica OT; MCM vende OT; no duplicar procedimiento |
| **Materials/** | Taglines · CTAs una sola vez |
| **Glosario central** | MDO-02 §9 · no redefinir términos |
| **Search canonical** | Un resultado principal por concepto |
| **Compatibilidad** | [MDO-05 §13](05-versionado-releases.md#13--política-de-compatibilidad-entre-manuales) |

Antes de escribir: **¿Existe ya?** → Enlazar.

---

## Relación con otros documentos

| Documento | Relación |
|-----------|----------|
| [MDO-03](03-guia-usuarios.md) | Guía de uso · FAQ |
| [MDO-08](08-portal-docs.md) | Shell del buscador |
| [MDO-06](06-catalogo-documental.md) | Índice maestro |
| [MDO-10](10-cierre-mdo.md) | Cierre del manual |

---

## Exit Criteria

- [x] Search global especificado (MVP + v2)
- [x] Índices · tags · categorías documentados
- [x] SEO · URLs · redirects definidos
- [x] Estrategia anti-duplicación establecida

---

## Filosofía del capítulo

La mejor navegación es invisible: el usuario encuentra la respuesta **antes** de preguntarse dónde buscar.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| Especificación búsqueda | ✅ Definida |
| Implementación MVP | 🟡 Roadmap v2 |
| MDO-09 | ✅ Entregado |

---

← [MDO-08](08-portal-docs.md) · [Índice MDO](/mdo/) · [MDO-10](10-cierre-mdo.md) →
