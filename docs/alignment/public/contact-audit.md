# Auditoría · Contacto

**Sprint 14 · Fase 2** · **Estado:** ✅ **Cierre Área 8**  
**Rutas:** `/contacto` · nav · footer  
**Referencia:** MKT-05 · MKT-06 (emails)

---

## Resumen

| Elemento | Actual | MKT / MCM | Estado |
|----------|--------|-----------|--------|
| Página contacto | `/contacto` + formulario | Formulario + CTA | ✅ |
| Email | `contacto@maintix.com` | Dominio Maintix | ✅ |
| Mensaje éxito | Confirmación 24 h | Copy MKT | ✅ |
| Demo vs contacto | Rutas separadas | Flujos separados | ✅ |

---

## Implementación

| Elemento | Archivo |
|----------|---------|
| Contenido y asuntos | `app/public_contact.py` |
| Ruta GET/POST | `app/routes.py` → `main.contacto` |
| Template | `templates/landing/contacto.html` |
| Público sin login | `middleware.py` · `before_request` |

---

## Checklist cierre

- [x] Formulario o canal oficial documentado
- [x] CTAs alineados MKT
- [x] Sin mailto `@mantis.app` en público
- [x] Separado de demo (`/demo`) y trial (`/onboarding`)

→ [contact-audit.md](contact-audit.md)
