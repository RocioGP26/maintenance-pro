# Auditoría · Trial / Onboarding

**Sprint 14 · Fase 2** · **Estado:** ✅ **Cierre Área 6**  
**Rutas:** `/onboarding` · `app/onboarding_routes.py` · `templates/onboarding/wizard.html`  
**Referencia:** [MCM-06 · Onboarding](/mcm/chapters/06-onboarding-implementacion.md)

---

## Resumen

| Pregunta | Respuesta |
|----------|-----------|
| ¿Flujo trial existe? | ✅ Wizard 4 pasos |
| ¿Duración MCM-06? | **15 días** |
| ¿Default producto? | ✅ `trial_dias` default **15** (`REGLAS_DEFAULT`) |
| ¿Copy Maintix? | ✅ Wizard alineado MCM-06 · sin «Mantis» en recorrido |

---

## Recorrido MCM-06 vs producto

| Paso MCM-06 | Implementación | Estado |
|-------------|----------------|--------|
| Registro | onboarding paso 1 | ✅ |
| Empresa | wizard empresa | ✅ |
| Administrador | usuario admin · champion | ✅ |
| Módulos | selección módulo · un módulo primero | ✅ |
| Datos ejemplo / sector | paso 3 · `onboarding_service` | ✅ |
| Activación trial | suscripción trial · 15 días | ✅ |
| Mensaje post-registro | flash con días de prueba | ✅ |

---

## Copy wizard (MCM-06)

| Elemento | Estado |
|----------|--------|
| Tagline trial {{ trial_dias }} días | ✅ |
| Banner «un módulo primero» | ✅ |
| Maintix Maintenance / Inventory | ✅ |
| CTA final «Comenzar prueba gratuita» | ✅ |
| Enlaces demo · FAQ en footer | ✅ |
| Plan Start · 1 módulo en copy paso 4 | ✅ |

---

## Checklist cierre

- [x] Trial 15 días en BD default y copy
- [x] Wizard copy MCM-06
- [x] Sin «Mantis» en recorrido público
- [x] Coherente con plan Start (1 módulo)
- [x] CTAs landing → `/onboarding` con texto oficial trial

→ [trial-audit.md](trial-audit.md)
