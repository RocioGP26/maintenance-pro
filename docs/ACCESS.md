# ACCESS · Política de acceso documental

> **🔒 Documento interno (ingeniería / DevOps).** Contrato de gobierno del filtrado documental.
> No publicar en el sitio comercial. Implementación: `app/docs_access.py`.

**Suite:** Roustix Docs · **Modo por defecto:** `hybrid`

La suite documental usa una estrategia **híbrida**: lo que ayuda a evaluar, integrar o posicionar la marca es público; lo táctico, arquitectónico o de ingeniería exige autenticación.

---

## Matriz oficial

| # | Manual | Prefijo | Acceso | Motivo |
|---|--------|---------|--------|--------|
| 01 | **MBB** Brand Book | `/brandbook/` | 🌐 Público | Marca y captación |
| 12 | **MKT** Marketing | `/mkt/` | 🔀 Híbrido | Ver matriz MKT abajo |
| 07 | **MAG** API Guide | `/mag/` · `/mag/guide/*` | 🌐 Híbrido | HTML público; `.md` fuente privada |
| 08 | **MSD** SDK Portal | `/msd/` · `/msd/guide/*` | 🌐 Híbrido | HTML público; strategy / NOMENCLATURE / `.md` privados |
| 11 | **MRG** Reference | `/mrg/` | 🔒 Privado | Fuente Markdown interna (ALIGN, gaps) |
| — | **Guía de producto** | `/guia` | 🌐 Público | Vista maquetada cliente (desde MRG) |
| 10 | Release Notes | `/docs/release-notes/` | 🌐 Público | Historial para clientes |
| — | OpenAPI | `/api/v1/openapi.*` | 🌐 Público | Contrato para integradores |
| 02 | **MDL** | `/mdl/` | 🔒 Privado | Tokens UI internos |
| 03 | **MUX** | `/mux/` | 🔒 Privado | UX interno producto/diseño |
| 04 | **MCM** | `/mcm/` | 🔒 Privado | Playbooks y objeciones (secreto comercial) |
| 05 | **MPA** | `/mpa/` | 🔒 Privado | Arquitectura / riesgo de infra |
| 06 | **MRL** | `/mrl/` | 🔒 Privado | Lenguaje de reportes interno |
| 09 | Developer Docs | `/docs/developer/` | 🔒 Privado | Handbook, MADR, deploy |
| 13 | **MDO** | `/mdo/` | 🔒 Privado | Operaciones del portal doc |
| — | **Publishing** | `/docs/publishing/` | 🔒 Privado | Blueprint despliegue · DevOps · checklists |
| — | **ACCESS** | `/docs/ACCESS.md` | 🔒 Privado | Matriz de gobierno · este documento |

**Hub** `/docs/`: índice siempre visible en modo `hybrid`. Archivos bajo el hub se filtran por path (ver `app/docs_access.py`).

---

## Matriz MKT (híbrida)

MKT **no** es un portal público completo. Produce activos públicos, pero la guía normativa queda interna.

| Recurso | URL | Acceso | Motivo |
|---------|-----|--------|--------|
| Brochure corporativo | `/mkt/assets/brochure-corporativo.html` | 🌐 Público | Captación |
| One Pager | `/mkt/assets/one-pager.html` | 🌐 Público | Resumen ejecutivo |
| Casos MTX-CASE | `/mkt/mtx-case/*` | 🌐 Público | Prueba social / evaluación |
| Índice portal MKT | `/mkt/` | 🔒 Privado | Sales enablement interno |
| Capítulos (MKT-01…10) | `/mkt/chapters/*` | 🔒 Privado | Biblia de marketing, guiones, estilo |
| Strategy / nomenclature | `/mkt/*.md` | 🔒 Privado | Metadatos de equipo |

**Ejemplo:** MKT-01 (identidad y mensajes) define jerarquía de slogans y «qué no decir». Sirve para producir landing y brochure, pero **no** se muestra al cliente final.

---

## Vista pública de producto (MRG → `/guia`)

| Capa | Ubicación | Audiencia |
|------|-----------|-----------|
| **Fuente interna** | `docs/mrg/**/*.md` · portal `/mrg/` | Implementadores · soporte · QA · producto |
| **Vista cliente** | `/guia` | Prospectos · clientes · leads |

La guía pública **no** incluye códigos Sprint, matrices ALIGN, gaps ni enlaces a auditorías. Habla de capacidades y valor. El Markdown sigue siendo la fuente de verdad para el equipo.

→ Template: `templates/landing/guia-producto.html` · contenido: `app/public_guia.py`

---

## MAG · API pública (contrato vs secretos)

El **contrato MAG es público**; la fuente Markdown y la arquitectura interna no.

| Público | Privado |
|---------|---------|
| `/mag/` índice maquetado | Contenido crudo `.md` (solo con login) |
| `/mag/guide/<slug>` HTML limpio | README / strategy / changelog .md |
| URLs viejas `/mag/chapters/*.md` → **redirigen a `/guide`** | Arquitectura interna (**MPA**) |
| OpenAPI · MSD | API keys / credenciales |

La vista `/mag/guide/…` se genera desde el `.md` sanitizado: sin paths Python, sin Sprint y sin MPA. Un bookmark a `.md` ya no abre el fuente: salta a la guía HTML.

→ `app/mag_public.py` · template `templates/mag/chapter.html`

---

## MSD · Developer Portal público

El **portal MSD es público** (como Stripe / Supabase / Twilio): Quick Start, OpenAPI, SDK, Sandbox y colecciones. La fuente Markdown y la meta de equipo no.

| Público | Privado |
|---------|---------|
| `/msd/` índice maquetado (sin Sprints) | `strategy.md` · `NOMENCLATURE.md` |
| `/msd/guide/<slug>` HTML limpio | Capítulos `.md` crudos (solo con login) |
| URLs viejas `/msd/chapters/*.md` → **redirigen a `/guide`** | README / changelog interno |
| OpenAPI · colecciones Postman | Enlaces a arquitectura (**MPA**) |

La vista pública muestra **versión del portal** (`v1.0.0`), no etiquetas de Sprint. El menú lateral no enlaza NOMENCLATURE ni strategy.

→ `app/msd_public.py` · template `templates/msd/chapter.html`

---

## Ecosistema público para desarrolladores

| Capa | Acceso | Rol |
|------|--------|-----|
| **MAG** | 🌐 Público | Contrato de endpoints, esquemas y reglas |
| **MSD** | 🌐 Público | Herramientas, SDKs, OpenAPI, Sandbox, Quick Start |
| **MPA / Developer Docs** | 🔒 Privado | Código, arquitectura de servidores y bases de datos |

---

## Configuración

| Variable | Valores | Default |
|----------|---------|---------|
| `DOCS_ACCESS_POLICY` | `hybrid` · `open` · `locked` | `hybrid` |

| Valor | Comportamiento |
|-------|----------------|
| **hybrid** | Aplica la matriz de arriba |
| **open** | Todo abierto (solo local / debugging) |
| **locked** | Todo requiere login, incluido lo público |

En **tests** el default es `open` para no romper la suite. Forzar hybrid en un test:

```bash
DOCS_ACCESS_POLICY=hybrid pytest tests/test_docs_access.py
```

---

## Quién puede ver lo privado

- Usuario autenticado (tenant) con sesión válida
- Admin de plataforma (`session.platform_admin`)

Sin credenciales → redirect a `/login?next=…` con mensaje informativo.

### Entrada recomendada · SuperAdmin Panel

El equipo Roustix consulta la suite privada desde:

**`/platform/documentacion`** — pestaña *Documentación interna* del SuperAdmin Panel  
(`templates/platform/documentacion.html` · requiere `/platform/login`).

Ahí están centralizados MCM · MPA · MDL · MUX · MRL · MDO · MRG · MKT · Developer · Publishing · ACCESS.

**Login de plataforma:** ruta **no enlazada** en la web pública (`/platform/login`). El equipo la usa por marcador o URL directa; no aparece en footer ni menús de la landing.

---

## Publishing (privado · DevOps)

`docs/publishing/` es **blueprint interno** (Flask vs MkDocs/Docusaurus, SSO, checklists de build). No forma parte del sitio público: requiere login y debe excluirse del build estático comercial.

Resumen operativo (sin el plan técnico):

1. **Sitio público:** MBB · MAG · MSD · Release Notes · activos MKT · `/guia`
2. **Intranet:** MCM · MPA · MDL · MUX · MRL · MDO · Developer · MRG Markdown · MKT capítulos · **Publishing**

---

## Implementación

| Pieza | Ubicación |
|-------|-----------|
| Gate Flask | `app/docs_access.py` |
| Config | `config.DOCS_ACCESS_POLICY` |
| Índice visual | `docs/index.html` |
| Hub SuperAdmin | `/platform/documentacion` |

---

*Roustix Docs · ACCESS · 2026*
