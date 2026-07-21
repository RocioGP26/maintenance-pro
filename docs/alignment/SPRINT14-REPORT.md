# Sprint 14 · Reporte Final

**Código:** ALIGN · **Documentation Alignment**  
**Período:** Sprint 14 · **Cierre:** 2026-07-10  
**Commit principal:** `8512056` — *Sprint 14 ALIGN: alinear producto y MRG (fases 1-8)*  
**Frase:** Toda la operación. Una sola plataforma.

---

## Objetivo

**Alinear producto y documentación** — sin scope creep ni features nuevas.

Que Roustix refleje el MRG como fuente funcional: menús, copy (MUX), permisos (IAM), rutas, dashboards, flujos transversales y estado real por funcionalidad (✅ · 🟡 · 📋 · ❌).

→ Metodología: [README.md](README.md) · Checklist: [checklist.md](checklist.md)

---

## Resultado

| Métrica | Valor |
|---------|-------|
| Archivos modificados | **60** |
| Commit Sprint 14 ALIGN | **1** (`8512056`) |
| Commits en rama `develop` (vs `origin`) | **5** *(incluye Sprints 11–13)* |
| Pantallas / plantillas auditadas | **32** |
| Módulos MRG revisados | **8** (MRG-02 → MRG-09) |
| Fases ALIGN cerradas | **8 / 8** |
| Auditorías creadas | **14** archivos en `modules/` |
| Entradas MRG changelog | **8** ([1.0.2] → [1.0.9]) |
| Nuevas funcionalidades | **0** |
| Gaps documentados | **~35** *(19 en matriz · resto transversal en auditorías)* |
| Gaps cerrados (alineación) | **~18** *(nav · copy · permisos · doc · validación demo)* |
| Validación MCM-07 demo | ✅ [mcm-demo-validation.md](mcm-demo-validation.md) |

### Desglose · pantallas auditadas (32)

**Mantenimiento (12):** dashboard · reportes · activos (list/form/tipos) · OT (list/form/planeación) · calendario · repuestos técnicos · incidencias (list/detalle/alta) · proveedores servicio  

**Inventario comercial (12):** dashboard comercial · productos · compras · CxP · ventas (list/POS/detalle) · clientes · proveedores comerciales  

**Admin / transversal (8):** equipo · configuración empresa · campos personalizados · onboarding · permisos · flujos incidencia→OT · integración módulos · API v1 (parcial)

---

## Estado por módulo

Leyenda en este reporte:

| Símbolo | Significado Sprint 14 |
|---------|------------------------|
| 🟢 | Alineación documental **cerrada** · núcleo operativo sólido |
| 🟡 | Alineación **cerrada** · implementación **parcial** (gaps 📋 activos) |

| Módulo | MRG | Doc | Código | Estado |
|--------|-----|-----|--------|--------|
| **Maintenance** | MRG-02 | v1.0.2 | 🟡 | 🟡 |
| **Inventory** | MRG-03 | v1.0.1 | ✅ | 🟡 |
| **Purchasing** | MRG-04 | v1.0.2 | 🟡 | 🟡 |
| **Sales** | MRG-05 | v1.0.1 | 🟡 | 🟡 |
| **CRM** | MRG-06 | v1.0.1 | 🟡 pre-CRM | 🟡 |
| **Admin / IAM** | MRG-07 | v1.0.1 | ✅ | 🟢 |
| **Reports** | MRG-08 | v1.0.1 | 🟡 | 🟡 |
| **Workflows** | MRG-09 | v1.0.1 | 🟡 | 🟢 |

→ Detalle fila a fila: [status-matrix.md](status-matrix.md)

---

## Entregables

| Entregable | Estado |
|------------|--------|
| Producto alineado con MRG (nav · copy · permisos) | ✅ |
| Navegación unificada (submenús Compras · Ventas · Admin · Indicadores) | ✅ |
| Copy MUX aplicado («Activos» · «Repuestos técnicos» · pre-CRM) | ✅ |
| Permisos revisados (`permissions.py` · matrices 02/07) | ✅ |
| Dashboard resumen operativo (MRG-02 §10) | ✅ |
| Demo MCM-07 validada | ✅ |
| Auditorías por módulo (`docs/alignment/modules/`) | ✅ |
| MRG capítulos 02–09 con badges y matriz § | ✅ |
| Gaps priorizados y documentados | ✅ |
| MAG revisión formal | ☐ pendiente Sprint 15+ |

---

## Cambios de producto (resumen)

Sin features nuevas — solo **alineación** de lo existente:

1. **Nav:** submenús Activos · Órdenes · Compras (Listado + CxP) · Ventas (Listado + Por cobrar + Clientes) · Indicadores · Administración  
2. **Copy:** equipos → activos · inventario técnico → repuestos técnicos  
3. **Dashboard / reportes:** resumen OT · enlaces cruzados mant ↔ comercial  
4. **Compras / ventas:** estado pago · filtro cartera `?cobro=pendiente`  
5. **Permisos:** incidencias · crear OT desde incidencia  
6. **API:** ampliación GET v1 tenancy (parcial · sin CRUD completo)

---

## Gaps documentados (priorizados)

### Transversales (P1–P2)

| Gap | Módulos | Prioridad |
|-----|---------|-----------|
| Export Excel OT / activos | MRG-02 · MRG-08 | P2 |
| API MAG CRUD (maintenance · inventory · sales · purchasing · crm) | Todos | P2 |
| Repuestos en OT preventiva / emergencia | MRG-02 · MRG-09 | P2 |
| Jerarquía activo · OT «En espera» | MRG-02 | P2 |

### Comercial / inventario

| Gap | MRG | Prioridad |
|-----|-----|-----------|
| Purchasing formal (solicitud · OC · recepción parcial) | MRG-04 · MRG-09 | P2 |
| Kardex UI · ajuste manual stock | MRG-03 | P2 |
| CRM pipeline · oportunidades · actividades | MRG-06 | P3 |
| PDF MRL · tendencias · BI | MRG-08 | P3 |
| Webhooks MAG | MRG-09 · MAG | P3 |

### Gaps cerrados en Sprint 14 (alineación, no roadmap)

Nav unificada · copy MUX · permisos incidencias/OT · dashboard resumen · CxP en nav y listado · Por cobrar · Clientes bajo Ventas · Indicadores · Administración submenú · MRG badges · auditorías · validación demo MCM.

---

## Resultado

**Sprint 14 cumplió su objetivo.**

- Producto y MRG **sincronizados** en lo que ya existía.  
- Documentation drift **reducido** a gaps explícitos 📋.  
- Base **lista para evolución** — no para más «alineación ad hoc».

---

## Después del Sprint 14

A partir de aquí **ya no se habla de «alineación»**, sino de **evolución del producto**.

Toda funcionalidad nueva o gap 📋 que pase a desarrollo debe cumplir:

1. **Contrato en MRG** — definición funcional y criterios de aceptación  
2. **Impacto comercial en MCM** — si afecta venta, demo u onboarding  
3. **Soporte en MAG** — si expone API pública  
4. **Transición de estado** — de 📋 Roadmap → 🚧 En desarrollo → 🧪 QA → ✅ Producción  

---

## Recomendación · ciclo de vida (Sprint 15+)

Incorporar un **ciclo de vida estándar** además de los íconos de cobertura (✅/🟡/📋/❌):

| Estado | Significado |
|--------|-------------|
| 📋 **Roadmap** | Aprobado funcionalmente en MRG · pendiente de desarrollo |
| 🚧 **En desarrollo** | Trabajo activo en código |
| 🧪 **QA / Validación** | Implementada · pruebas funcionales · alineación MRG |
| ✅ **Producción** | Disponible · documentación y producto sincronizados |
| 🔒 **Deprecado** | Reemplazada o retirada · ventana de migración documentada |

Esto mantiene **MRG · código · MDO (versiones) · planificación** en el mismo lenguaje durante toda la evolución de Roustix.

**Propuesta Sprint 15:** adoptar esta leyenda en `docs/alignment/README.md` (o MDO-05), actualizar `status-matrix.md` al primer ítem 🚧, y priorizar 1–2 gaps P2 con contrato MRG + entrada changelog.

---

## Roadmap

**El Sprint 15 comienza sobre una base alineada** — producto autenticado sincronizado con MRG.

### Sprint 14 · Fase 2 · Public Experience Alignment 🚀

**Código:** ALIGN-PUB · **Objetivo:** alinear sitio público con MCM · MKT · MDL · MUX.

| Fase | Alcance | Estado |
|------|---------|--------|
| Fase 1 | MRG ↔ app autenticada | ✅ Cerrada |
| **Fase 2** | MCM/MKT ↔ landing · trial · FAQ · footer | 🚀 [Iniciada](../alignment/public/README.md) |

→ [README Fase 2](../alignment/public/README.md) · [Matriz pública](../alignment/public/status-matrix.md)

Tras Fase 2: **evolución del producto** con ciclo de vida 📋 → 🚧 → 🧪 → ✅ (ver recomendación Sprint 15+ arriba).

| Área | Siguiente paso sugerido |
|------|-------------------------|
| **Fase 2 P0** | Marca Roustix · planes Start–Enterprise · trial 15 días |
| Producto | Cerrar gap P2 acordado post-Fase 2 |
| MRG | Estados 🚧/🧪 en gaps seleccionados |
| MAG | Revisión formal post-ALIGN |
| MCM/MKT | Copy sitio = manuales oficiales |

---

## Referencias

| Documento | Enlace |
|-----------|--------|
| Checklist maestro | [checklist.md](checklist.md) |
| Matriz MRG ↔ código | [status-matrix.md](status-matrix.md) |
| MRG changelog | [/mrg/changelog.md](/mrg/changelog.md) |
| Validación demo | [mcm-demo-validation.md](mcm-demo-validation.md) |
| **Fase 2 · Sitio público** | [SPRINT14-PHASE2-REPORT.md](SPRINT14-PHASE2-REPORT.md) |
| Índice suite | [/docs/index.html](/docs/index.html) |

---

*Sprint 14 · Documentation Alignment · Roustix · 2026-07-10 · ✅ Cerrado oficialmente*
