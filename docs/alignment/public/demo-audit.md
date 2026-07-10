# Auditoría · Demo

**Sprint 14 · Fase 2** · **Estado:** ✅ **Cierre Área 5**  
**Rutas:** `/demo` · nav · landing CTAs  
**Referencia:** [MCM-07 · Demo comercial](/mcm/chapters/07-demo-comercial.md)

---

## Resumen

| Pregunta | Respuesta |
|----------|-----------|
| ¿CTA oficial? | **Solicitar demostración** (MKT-05) |
| ¿Actual? | ✅ Unificado en landing, nav y `/demo` |
| ¿Página `/demo`? | ✅ `templates/landing/demo.html` · `app/public_demo.py` |
| ¿Producto interno validado? | ✅ [mcm-demo-validation.md](../mcm-demo-validation.md) Fase 1 |

---

## Implementación

| Elemento | Archivo |
|----------|---------|
| Contenido PLAY-001–005 | `app/public_demo.py` |
| Ruta GET/POST | `app/routes.py` → `main.demo` |
| Formulario solicitud | `templates/landing/demo.html` |
| Público sin login | `middleware.py` · `before_request` |
| Separación demo / trial / contacto | Sección «Demo, prueba o contacto» en `/demo` |

---

## Flujo MCM-07 (copy público)

| PLAY | Mensaje público | Estado |
|------|-----------------|--------|
| PLAY-001 | Preparación · sector · módulo entrada | ✅ |
| PLAY-002 | Descubrimiento · historia sector | ✅ |
| PLAY-003 | Demo 20 min · un flujo | ✅ |
| PLAY-004 | KPIs dashboard | ✅ |
| PLAY-005 | Plan · trial 15 días · siguiente paso | ✅ |

---

## Checklist cierre

- [x] CTA «Solicitar demostración» unificado
- [x] Flujo MCM-07 descrito en sitio
- [x] Sin prometer features 📋 en guion demo público
- [x] Enlace coherente con trial (`/onboarding`)

→ [demo-audit.md](demo-audit.md)
