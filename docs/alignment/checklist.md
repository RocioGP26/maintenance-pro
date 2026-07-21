# Sprint 14 · Checklist de Alineación

**Actualizado:** 2026-07-10 · Fases 1–8 ✅ · **Sprint 14 ALIGN cerrado**

Leyenda: ☐ pendiente · 🟡 en progreso · ✅ alineado · ➖ N/A

---

## Fase 1 · MRG-02 · Mantenimiento · ✅ Cerrada

**MRG:** [02-maintenance.md](/mrg/chapters/02-maintenance.md) v1.0.2 · **Auditorías:** [02-maintenance-audit.md](modules/02-maintenance-audit.md)

| Área | ☐ | Notas |
|------|---|-------|
| Menús | ✅ | Nav alineado MRG-02 |
| Formularios | ✅ | Activos · OT · incidencias |
| Botones | ✅ | CTAs MUX |
| Permisos | ✅ | [02-permissions-matrix.md](modules/02-permissions-matrix.md) |
| Rutas | ✅ | URLs estables |
| Reportes | 🟡 | Gráficos OK · export 📋 |
| Dashboard | ✅ | Resumen MRG-02 §10 |
| API | 🟡 | GET v1 · CRUD 📋 |
| Exportaciones | 📋 | Excel OT/activos |
| MRG estado | ✅ | Badges §1–§11 · v1.0.2 |

---

## Fase 2 · MRG-03 · Inventario · ✅ Cerrada

**MRG:** [03-inventario.md](/mrg/chapters/03-inventario.md) v1.0.1 · **Auditoría:** [03-inventario-audit.md](modules/03-inventario-audit.md)

| Área | ☐ | Notas |
|------|---|-------|
| Menús | ✅ | Repuestos técnicos · Dashboard inventario |
| Formularios | ✅ | Productos · ubicación · mínimos |
| Botones | ✅ | Import/export · Nuevo producto |
| Permisos | ✅ | `@require_module(inventario)` |
| Rutas | ✅ | `/comercial/*` |
| Dashboard | ✅ | KPIs · bajo stock · valorización |
| Import/export | ✅ | Excel catálogo · plantilla · bajo stock |
| API | 📋 | MAG `/inventory/*` pendiente |
| Distinción MRG-02 | ✅ | Nav repuestos vs productos |
| MRG estado | ✅ | Badges §1–§6 · v1.0.1 |

**Rutas clave:** `/inventario` · `inv_comercial` productos · bodegas

---

## Fase 3 · MRG-04 · Compras · ✅ Cerrada

**MRG:** [04-compras.md](/mrg/chapters/04-compras.md) v1.0.1 · **Auditoría:** [04-compras-audit.md](modules/04-compras-audit.md)

| Área | ☐ | Notas |
|------|---|-------|
| Menús | ✅ | Submenú Compras · CxP |
| Formularios | ✅ | Entrada mercancía · IVA · multimoneda |
| Proveedores | ✅ | Distinto de servicio MRG-02 |
| CxP y pagos | ✅ | Parcial · pagada · alertas |
| Rutas | ✅ | `/comercial/compras` · `/cuentas-por-pagar` |
| Stock al confirmar | ✅ | `registrar_entrada_mercancia` |
| Listado | ✅ | Estado pago · filtros CxP |
| API | 📋 | MAG `/purchasing/*` |
| MRG estado | ✅ | Badges §1–§9 · v1.0.1 |

---

## Fase 4 · MRG-05 · Ventas · ✅ Cerrada

**MRG:** [05-ventas.md](/mrg/chapters/05-ventas.md) v1.0.1 · **Auditoría:** [05-ventas-audit.md](modules/05-ventas-audit.md)

| Área | ☐ | Notas |
|------|---|-------|
| Menús | ✅ | Submenú Ventas · Por cobrar |
| POS | ✅ | `/ventas/nueva` |
| Crédito / abonos | ✅ | `InvVentaCobro` |
| Clientes | ✅ | `/comercial/clientes` |
| Stock al vender | ✅ | validación stock |
| Cartera por cobrar | ✅ | filtro `?cobro=pendiente` |
| Dashboard | ✅ | ventas hoy · top productos |
| API | 📋 | MAG `/sales/*` |
| MRG estado | ✅ | Badges §1–§10 · v1.0.1 |

---

## Fase 5 · MRG-06 · CRM · ✅ Cerrada

**MRG:** [06-crm.md](/mrg/chapters/06-crm.md) v1.0.1 · **Auditoría:** [06-crm-audit.md](modules/06-crm-audit.md)

| Área | ☐ | Notas |
|------|---|-------|
| Maestro clientes | ✅ | `InvCliente` CRUD |
| Nav | ✅ | Ventas → Clientes |
| Copy pre-CRM | ✅ | listado clientes |
| Integración ventas | ✅ | POS · crédito |
| Pipeline / oportunidades | 📋 | roadmap |
| MRG estado | ✅ | Badges §1–§10 · v1.0.1 |

---

## Fase 6 · MRG-07 · Administración e IAM · ✅ Cerrada

**MRG:** [07-administracion.md](/mrg/chapters/07-administracion.md) v1.0.1 · **Auditorías:** [07-admin-audit.md](modules/07-admin-audit.md) · [07-permissions-matrix.md](modules/07-permissions-matrix.md)

| Área | ☐ | Notas |
|------|---|-------|
| Roles IAM | ✅ | `permissions.py` |
| Matriz permisos | ✅ | transversal + MRG-02 |
| Nav administración | ✅ | Submenú · Usuarios y roles |
| Equipo / usuarios | ✅ | `/equipo` |
| Config tenant | ✅ | superadmin |
| Onboarding | ✅ | `/onboarding` |
| Roustix Platform | ✅ | `/platform/` |
| API | 🟡 | `/admin/summary` |
| MRG estado | ✅ | Badges §1–§10 · v1.0.1 |

---

## Fase 7 · MRG-08 · Reportes · ✅ Cerrada

**MRG:** [08-reportes.md](/mrg/chapters/08-reportes.md) v1.0.1 · **Auditorías:** [08-reportes-audit.md](modules/08-reportes-audit.md) · [02-reports-audit.md](modules/02-reports-audit.md)

| Área | ☐ | Notas |
|------|---|-------|
| Menús | ✅ | Submenú Indicadores (mant + inv) |
| Formularios | ➖ | N/A reportes |
| Botones | ✅ | KPIs comerciales · enlaces cruzados |
| Permisos | ✅ | Por módulo tenant |
| Rutas | ✅ | `/dashboard` · `/reportes` · `/comercial/dashboard` |
| Reportes | 🟡 | Gráficos mant · tendencias 📋 |
| Dashboard | ✅ | Mantenimiento + comercial |
| API | 📋 | API reportes MAG |
| Exportaciones | 🟡 | Excel inv ✅ · OT/activos 📋 |
| MRG estado | ✅ | Badges §1–§9 · v1.0.1 |

**Rutas clave:** `/dashboard` · `/reportes` · `/comercial/dashboard`

---

## Fase 8 · MRG-09 · Flujos (transversal) · ✅ Cerrada

**MRG:** [09-workflows.md](/mrg/chapters/09-workflows.md) v1.0.1 · **Auditoría:** [09-workflows-audit.md](modules/09-workflows-audit.md)

| Flujo | ☐ | Notas |
|-------|---|-------|
| Incidencia → OT | ✅ | `crear-ot` · resolver sin OT |
| OT preventiva | ✅ | calendario anual · planeación mensual |
| Consumo repuestos | 🟡 | solo OT correctiva |
| Compra → inventario | ✅ | `registrar_entrada_mercancia` |
| Venta → inventario | ✅ | `registrar_venta` · stock |
| Onboarding | ✅ | `/onboarding` |
| IAM / permisos | ✅ | `/equipo` · `permissions.py` |
| MRG estado | ✅ | Badges §1–§12 · v1.0.1 |

---

## Cierre Sprint 14

- [x] Fase 1 MRG-02 auditada y cerrada
- [x] Fase 2 MRG-03 auditada y cerrada
- [x] Fase 3 MRG-04 auditada y cerrada
- [x] Fase 4 MRG-05 auditada y cerrada
- [x] Fase 5 MRG-06 auditada y cerrada
- [x] Fase 6 MRG-07 auditada y cerrada
- [x] Fase 7 MRG-08 auditada y cerrada
- [x] Fase 8 MRG-09 auditada y cerrada
- [x] `status-matrix.md` fases 1–8
- [x] MRG changelog actualizado por capítulo (MRG-02–09)
- [ ] MAG revisado donde hubo cambios API (sin cambios API Fase 8)
- [x] Demo comercial (MCM) validada — [mcm-demo-validation.md](mcm-demo-validation.md)

---

→ [README Sprint 14](README.md) · [Matriz de estado](status-matrix.md) · **[Reporte final](SPRINT14-REPORT.md)** · [Fase 2 Public](public/README.md)
