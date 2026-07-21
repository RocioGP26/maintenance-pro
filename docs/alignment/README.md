# Sprint 14 · Alineación Documental del Producto

**Código:** ALIGN · **Sprint 14** · Documentation Alignment
**Estado:** ✅ Fase 1 cerrada · 🚀 **Fase 2 Public Experience** → [public/README.md](public/README.md)
**Frase:** Toda la operación. Una sola plataforma.

> La suite documental (MPA · MRG · MCM · MKT · MDO) define **cómo debe ser Roustix**.
> Sprint 14 asegura que **el producto implementado refleje esa documentación**.

**No es un sprint de features nuevas.** Es el puente entre el Roustix actual y la plataforma definida en la suite.

---

## Objetivo

Que cada pantalla, flujo, permiso, reporte y API del sistema **coincida con la documentación oficial** (MRG como fuente funcional, MAG como contrato API).

### Resultado esperado

1. Documentación y producto **sincronizados** (sin documentation drift)
2. MRG con **estado de implementación** por funcionalidad (✅ · 🟡 · 📋 · ❌)
3. Base consistente para Sprints 15+ (MQA · MSP · MTR · desarrollo)

---

## Metodología (por módulo)

Ciclo fijo en cada fase:

```
1. Auditoría     → ¿Qué existe? ¿Qué falta? ¿Qué sobra? ¿Qué difiere del MRG?
2. Alineación    → Menús · botones · mensajes · permisos · rutas · dashboards
3. Completar     → Solo lo que el manual exige (sin scope creep)
4. Marcar estado → Actualizar MRG + matriz de alineación
```

→ Gobernanza: [MDO-05 · Versionado](/mdo/chapters/05-versionado-releases.md) · [MDO-05 §13 · Compatibilidad](/mdo/chapters/05-versionado-releases.md#13--política-de-compatibilidad-entre-manuales)

---

## Estados de implementación (en MRG)

| Estado | Significado |
|--------|-------------|
| ✅ **Producción** | Implementado y alineado con MRG |
| 🟡 **Parcial** | Existe pero incompleto o desalineado |
| 📋 **Roadmap** | Documentado · no implementado |
| ❌ **No implementado** | Ausente en código |

---

## Orden de fases

| Fase | MRG | Módulo | Implementación principal |
|------|-----|--------|--------------------------|
| **1** | MRG-02-MAINT | Mantenimiento | ✅ Cerrada · `/activos` · `/ordenes` |
| **2** | MRG-03-INV | Inventario | ✅ Cerrada · `/comercial` |
| **3** | MRG-04-PUR | Compras | ✅ Cerrada · compras · CxP |
| **4** | MRG-05-SALES | Ventas | ✅ Cerrada · POS · cartera |
| **5** | MRG-06-CRM | CRM | ✅ Cerrada · maestro clientes |
| **6** | MRG-07-ADMIN | Admin · IAM | ✅ Cerrada · usuarios · Roustix Platform |
| **7** | MRG-08-REPORTS | Reportes | ✅ Cerrada · dashboards · `/reportes` |
| **8** | MRG-09-WORKFLOWS | Flujos transversales | ✅ Cerrada · incidencia→OT · stock |

> **Nota:** IAM no es capítulo MRG separado — vive en **MRG-07-ADMIN** (`/equipo`, roles, permisos).

---

## Artefactos Sprint 14

| Archivo | Rol |
|---------|-----|
| [SPRINT14-REPORT.md](SPRINT14-REPORT.md) | **Cierre Fase 1** · métricas · roadmap |
| [public/README.md](public/README.md) | **Fase 2** · Public Experience Alignment 🚀 |
| [checklist.md](checklist.md) | Lista de control maestra |
| [status-matrix.md](status-matrix.md) | Matriz MRG ↔ código ↔ estado |
| [modules/](modules/) | Auditorías · [API MAG](modules/02-api-audit.md) |

---

## Checklist transversal (cada módulo)

- [ ] Menús y navegación
- [ ] Formularios y validaciones
- [ ] Botones y CTAs (MUX copy)
- [ ] Permisos y roles
- [ ] Rutas URL
- [ ] Dashboard / KPIs
- [ ] Reportes y exportaciones
- [ ] API (MAG) · contratos
- [ ] Mensajes y estados (español oficial)
- [ ] MRG actualizado con estado real

---

## Reglas Sprint 14

1. **MRG manda** en lenguaje funcional; el código se alinea al manual
2. **No features nuevas** salvo gaps explícitos marcados 📋 en auditoría
3. Cambio en MRG por alineación → PATCH en MRG + entrada changelog
4. Cambio en código → revisar MAG si hay API pública
5. Cada fase cierra con **status-matrix** actualizada

---

## Relación con la suite

| Manual | Rol en Sprint 14 |
|--------|------------------|
| **MRG** | Fuente funcional · estados actualizados |
| **MUX** | Microcopy · labels · mensajes |
| **MAG** | Validación API vs implementación |
| **MDO** | Versionado · changelog · catálogo |
| **MCM/MKT** | Sin cambios salvo demo alineada |

---

## Próximo paso

Sprint 14 **cerrado** (fases MRG-02–09). Pendiente opcional: revisión MAG en Sprints 15+.

→ [Validación MCM demo](mcm-demo-validation.md) · [Checklist cierre](checklist.md#cierre-sprint-14) · [MRG-10](/mrg/chapters/10-buenas-practicas.md)

---

*Sprint 14 · Documentation Alignment · Roustix · 2026*
