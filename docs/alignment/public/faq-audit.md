# Auditoría · FAQ

**Sprint 14 · Fase 2** · **Estado:** 🟡 **Auditoría inicial**  
**Fuente única:** [MCM-08 · FAQ](/mcm/chapters/08-faq.md)  
**Sitio:** 📋 **No hay página pública** — solo manual en `/mcm/chapters/08-faq.md`

---

## Regla Fase 2

> **No mantener otra versión distinta.** El FAQ público debe ser **exactamente** MCM-08 (renderizado o copia literal aprobada).

---

## Contenido MCM-08 (temas clave)

| Tema | Debe reflejarse en sitio |
|------|--------------------------|
| Qué es Roustix | ✅ |
| Módulos hoy vs roadmap | ✅ |
| Planes Start–Enterprise | ✅ |
| Trial 15 días | ✅ |
| Tiempos onboarding Start/Grow | ✅ |
| Integraciones / ERP | ✅ honesto |

---

## Opciones implementación

| Opción | Pros | Esfuerzo |
|--------|------|----------|
| A · `/faq` render MD MCM-08 | Una fuente | Medio |
| B · Sección `#faq` en landing | SPA simple | Bajo |
| C · Include desde docs | DRY | Medio |

**Recomendación:** opción A o C — evitar FAQ hardcodeado divergente.

---

## Checklist cierre

- [ ] FAQ público existe
- [ ] Contenido = MCM-08 (versionado)
- [ ] Enlace en footer / nav Recursos
- [ ] Sin FAQ duplicado en otros templates

→ [faq-audit.md](faq-audit.md)
