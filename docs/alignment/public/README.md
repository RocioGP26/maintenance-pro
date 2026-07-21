# Sprint 14 · Fase 2 · Public Experience Alignment

**Código:** ALIGN-PUB · **Cierre:** 2026-07-10  
**Estado:** ✅ **Completada**  
**Frase:** Toda la operación. Una sola plataforma.

> **Fase 1:** producto autenticado alineado con MRG → [SPRINT14-REPORT.md](../SPRINT14-REPORT.md)  
> **Fase 2:** sitio público alineado con MCM · MKT · MDL · MUX

**Sin features nuevas de producto** — copy, nav, páginas públicas y trial.

---

## Objetivo

Que cualquier visitante vea **el mismo Roustix** que describen MCM y MKT: marca unificada, planes oficiales, módulos en producción vs roadmap, CTAs coherentes y recorrido trial/demo/contacto separados.

---

## Resultado

| Métrica | Valor |
|---------|-------|
| Áreas Fase 2 | **10 / 10** cerradas |
| Páginas públicas nuevas | `/faq` · `/demo` · `/contacto` · `/recursos` |
| Módulos Python contenido | `public_faq.py` · `public_demo.py` · `public_contact.py` · `public_recursos.py` |
| Trial default | **15 días** (MCM-04 · MCM-06 · MCM-08) |
| Marca pública | **Roustix** |
| Planes públicos | Start · Grow · Scale · Enterprise |

---

## Entregables por área

| # | Área | Entregable clave |
|---|------|------------------|
| 1 | Landing | Hero MKT-05 · sección Problema · reorden narrativo |
| 2 | Planes | Catálogo MCM-04 · `#precios` |
| 3 | Módulos | Producción vs roadmap en `#modulos` |
| 4 | Sectores | 5 tarjetas MCM-03 |
| 5 | Demo | `/demo` · PLAY-001–005 · formulario |
| 6 | Trial | Wizard MCM-06 · copy · 15 días |
| 7 | FAQ | `/faq` · MCM-08 · 22 preguntas |
| 8 | Contacto | `/contacto` · formulario general |
| 9 | Recursos | `/recursos` · MTX-CASE · stub blog |
| 10 | Nav/Footer | MKT-05 §6 · suite Docs/MCM/MKT/MRG/MAG |

---

## Archivos principales

```
app/branding.py              APP_NAME · contacto@roustix.com
app/landing_service.py       Hero · sectores · problema · CTAs
app/platform_config_service  Planes Start/Grow/Scale · trial 15d
app/public_*.py              FAQ · demo · contacto · recursos
app/routes.py                /faq /demo /contacto /recursos
templates/landing/           index · partials nav/footer · páginas
templates/onboarding/        wizard MCM-06
static/css/landing.css       Estilos públicos
docs/alignment/public/       Auditorías · matriz · checklist
```

---

## Rutas públicas (sin login)

| Ruta | Fuente |
|------|--------|
| `/` | MKT-05 landing |
| `/onboarding` | MCM-06 |
| `/faq` | MCM-08 |
| `/demo` | MCM-07 |
| `/contacto` | MKT-05 |
| `/recursos` | MKT-09 stub |

Registradas en `middleware.py` y `before_request` de `routes.py`.

---

## Pendiente post-Fase 2 (roadmap, no bloquea)

| Ítem | Prioridad |
|------|-----------|
| Página `/planes` dedicada | P3 |
| Landings por sector | P3 |
| Blog público en `/recursos` | P3 |
| Privacidad / términos legales | P3 |
| Redes sociales footer | P3 |
| Revisión visual MDL tokens | P2 |
| SMTP real formularios demo/contacto | P2 |

---

## Relación Fase 1 + Fase 2

| Capa | Alcance | Estado |
|------|---------|--------|
| **Interno** | App autenticada ↔ MRG | ✅ Fase 1 |
| **Externo** | Sitio público ↔ MCM/MKT | ✅ Fase 2 |

El ecosistema documental y la experiencia visitor-facing hablan el mismo lenguaje Roustix.

---

## Próximo paso recomendado

**Evolución del producto** — no más sprints de alineación masiva. Nuevas features siguen el ciclo MRG → MCM → MAG documentado en [SPRINT14-REPORT.md](../SPRINT14-REPORT.md).

---

→ [Checklist Fase 2](public/checklist.md) · [Matriz pública](public/status-matrix.md) · [Fase 1](../SPRINT14-REPORT.md)
