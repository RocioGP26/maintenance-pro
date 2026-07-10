# Auditoría · Planes

**Sprint 14 · Fase 2** · **Estado:** 🟡 **Auditoría inicial**  
**Rutas:** `/#precios` · catálogo BD · `app/platform_config_service.py` · `app/models.py`  
**Referencia:** [MCM-04 · Planes SaaS](/mcm/chapters/04-planes-saas.md)

---

## Resumen

| Pregunta | Respuesta |
|----------|-----------|
| ¿Planes oficiales MCM-04? | Start · Grow · Scale · Enterprise |
| ¿Planes visibles al público? | Starter · Pro · Enterprise (**3 tiers**) |
| ¿Página `/planes`? | 📋 No existe |

---

## Nomenclatura

| Plan MCM-04 | Código BD / seed | Visible landing | Estado |
|-------------|------------------|-----------------|--------|
| **Start** | `basico` / **Starter** | Starter | ❌ |
| **Grow** | — | **Ausente** | ❌ |
| **Scale** | `profesional` / **Pro** | Pro | ❌ |
| **Enterprise** | `enterprise` | Enterprise | 🟡 nombre OK |

---

## Trial y copy comercial

| Tema | MCM-04 / MCM-08 | Producto | Estado |
|------|-----------------|----------|--------|
| Trial | **15 días** | `trial_dias` default **14** | ❌ |
| Start = 1 módulo | ✅ doc | ✅ lógica planes | ✅ |
| Precios | Catálogo plataforma | `PLAN_CATALOG` vs `PLANES_SEED` duplicados | 🟡 |

---

## Acciones Fase 2

1. Renombrar labels públicos → Start · Grow · Scale · Enterprise  
2. Añadir tier **Grow** (o mapear Pro → Grow + Scale intermedio según MCM-04)  
3. Unificar seed catálogo con MCM-04  
4. Crear ruta `/planes` o canonical desde MKT-05  
5. Copy trial **15 días** en toda superficie pública  

---

## Checklist cierre

- [ ] 4 planes visibles con nombres MCM-04
- [ ] Sin «Starter» / «Pro» en UI pública
- [ ] Trial 15 días
- [ ] Precios coherentes (una fuente de verdad)
- [ ] Página o sección `/planes` alineada

→ [plans-audit](plans-audit.md) · [MCM-04](/mcm/chapters/04-planes-saas.md)
