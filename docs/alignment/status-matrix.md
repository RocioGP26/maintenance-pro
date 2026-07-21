# Matriz de alineación · MRG ↔ Implementación

**Sprint 14** · Fuente funcional: [MRG](/mrg/) · Actualizado: 2026-07-10

| MRG | Módulo | Implementación | Doc MRG | Código | Prioridad |
|-----|--------|----------------|---------|--------|-----------|
| MRG-02-MAINT | Mantenimiento | `app/routes.py` · API v1 | ✅ v1.0.2 | 🟡 Fase 1 ✅ | — |
| MRG-03-INV | Inventario | `/comercial` · `inv_comercial` | ✅ v1.0.1 | ✅ Fase 2 ✅ | — |
| MRG-04-PUR | Purchasing | solicitudes · OC · recepción · CxP | ✅ Sprint 16 | ✅ Operativo | API MAG |
| MRG-05-SALES | Ventas | `inv_comercial` ventas · POS | ✅ v1.0.1 | 🟡 Fase 4 ✅ | — |
| MRG-06-CRM | CRM | `InvCliente` · pre-CRM | ✅ v1.0.1 | 🟡 Fase 5 ✅ | — |
| MRG-07-ADMIN | Admin · IAM | `/equipo` · config · platform | ✅ v1.0.1 | ✅ Fase 6 ✅ | — |
| MRG-08-REPORTS | Reportes | `/dashboard` · `/reportes` · `/comercial/dashboard` | ✅ v1.0.1 | 🟡 Fase 7 ✅ | — |
| MRG-09-WORKFLOWS | Flujos | transversal · incidencia→OT | ✅ v1.0.1 | 🟡 Fase 8 ✅ | — |

**Leyenda código:** ✅ Producción · 🟡 Parcial/desalineado · 📋 Roadmap · ❌ No implementado

---

## Detalle por capítulo (se actualiza en cada fase)

### MRG-02 · Mantenimiento · Fase 1 ✅ cerrada 2026-07-10

| Entidad / flujo MRG | Ruta / código | Estado |
|---------------------|---------------|--------|
| Activos | `/activos` | ✅ |
| Tipos de activo | `/activos/tipos` | ✅ |
| Órdenes de trabajo | `/ordenes` | 🟡 |
| Planeación preventiva | `/ordenes/planeacion` | ✅ |
| Calendario OT | `/calendario` | ✅ |
| Incidencias | `/incidencias` | 🟡 |
| Repuestos (inv. técnico) | `/inventario` | ✅ |
| Técnicos | `/equipo` | ✅ |
| Proveedores servicio | `/proveedores` | ✅ |
| Campos personalizados | `/configuracion/campos` | ✅ |
| KPIs dashboard | `/dashboard` | ✅ |
| Reportes web | `/reportes` | 🟡 |
| Historial activo (ficha) | `activos/form` §5 | 🟡 |
| API MAG v1 | `/api/v1/maintenance/*` | 🟡 |

→ Auditorías: [02-maintenance-audit.md](modules/02-maintenance-audit.md) · [02-api-audit.md](modules/02-api-audit.md)

### MRG-03 · Inventario comercial · Fase 2 ✅ cerrada 2026-07-10

| Entidad / flujo MRG | Ruta / código | Estado |
|---------------------|---------------|--------|
| Catálogo productos | `/comercial/productos` | ✅ |
| Alta / edición / baja lógica | productos CRUD | ✅ |
| Import / export Excel | productos import/export | ✅ |
| Alertas bajo stock | dashboard · filtro · campana | ✅ |
| Valorización | dashboard KPI | ✅ |
| Ubicación bodega | campo producto | ✅ |
| Kardex / movimientos | implícito compras/ventas | 🟡 |
| Ajuste manual stock | — | 📋 |
| Repuestos técnicos (MRG-02) | `/inventario` | ✅ |
| API MAG inventory | — | 📋 |

→ Auditoría: [03-inventario-audit.md](modules/03-inventario-audit.md)

### MRG-04 · Compras · Fase 3 ✅ cerrada 2026-07-10

| Entidad / flujo MRG | Ruta / código | Estado |
|---------------------|---------------|--------|
| Proveedores comerciales | `/comercial/proveedores` | ✅ |
| Registro compra / entrada | `/comercial/compras` | ✅ |
| Detalle e edición | compras detalle/editar | ✅ |
| CxP (cuentas por pagar) | `/comercial/cuentas-por-pagar` | ✅ |
| Pagos parciales | `InvCompraPago` | ✅ |
| Alertas vencimiento | dashboard · filtros | ✅ |
| Stock al recibir | automático | ✅ |
| Solicitudes / OC formal | `/purchasing/solicitudes` · `/purchasing/ordenes` | ✅ |
| Recepción parcial | `PurRecepcion` · actualización stock idempotente | ✅ |
| API MAG purchasing | — | 📋 |

→ Auditoría: [04-compras-audit.md](modules/04-compras-audit.md)

### MRG-05 · Ventas · Fase 4 ✅ cerrada 2026-07-10

| Entidad / flujo MRG | Ruta / código | Estado |
|---------------------|---------------|--------|
| POS / nueva venta | `/comercial/ventas/nueva` | ✅ |
| Listado ventas | `/comercial/ventas` | ✅ |
| Contado / crédito | `forma_pago` | ✅ |
| Abonos | detalle · `InvVentaCobro` | ✅ |
| Cartera por cobrar | `?cobro=pendiente` | ✅ |
| Clientes | `/comercial/clientes` | ✅ |
| Descuento stock | automático | ✅ |
| Sales Pro | — | 📋 |
| API MAG sales | — | 📋 |

→ Auditoría: [05-ventas-audit.md](modules/05-ventas-audit.md)

### MRG-06 · CRM · Fase 5 ✅ cerrada 2026-07-10

| Entidad / flujo MRG | Ruta / código | Estado |
|---------------------|---------------|--------|
| Maestro clientes | `/comercial/clientes` | ✅ |
| Alta / edición / baja lógica | clientes CRUD | ✅ |
| Vínculo ventas | `InvVenta.cliente_id` | ✅ |
| Nav comercial | Ventas → Clientes | ✅ |
| Contactos múltiples | — | 📋 |
| Pipeline / oportunidades | — | 📋 |
| Actividades | — | 📋 |
| Ficha historial cliente | — | 📋 |
| API MAG crm | — | 📋 |

→ Auditoría: [06-crm-audit.md](modules/06-crm-audit.md)

### MRG-07 · Administración e IAM · Fase 6 ✅ cerrada 2026-07-10

| Entidad / flujo MRG | Ruta / código | Estado |
|---------------------|---------------|--------|
| Usuarios y roles | `/equipo` | ✅ |
| Configuración empresa | `/configuracion/empresa` | ✅ |
| Campos personalizados | `/configuracion/campos` | ✅ |
| Onboarding | `/onboarding` | ✅ |
| Roustix Platform plataforma | `/platform/` | ✅ |
| Permisos por rol | `permissions.py` | ✅ |
| Sedes | usuario · activos | 🟡 |
| Invitación email | — | 🟡 |
| API admin | `/api/v1/admin/summary` | 🟡 |

→ Auditorías: [07-admin-audit.md](modules/07-admin-audit.md) · [07-permissions-matrix.md](modules/07-permissions-matrix.md)

### MRG-08 · Indicadores y reportes · Fase 7 ✅ cerrada 2026-07-10

| Entidad / flujo MRG | Ruta / código | Estado |
|---------------------|---------------|--------|
| Dashboard mantenimiento | `/dashboard` | ✅ |
| Resumen operativo OT | `_dashboard_resumen_operativo` | ✅ |
| Reportes web gráficos | `/reportes` | 🟡 |
| Dashboard comercial | `/comercial/dashboard` | ✅ |
| Export Excel inventario | productos export | ✅ |
| Nav Indicadores | submenú mant + inv | ✅ |
| Export OT/activos Excel | — | 📋 |
| PDF MRL operativos | — | 📋 |
| Tendencias temporales | — | 📋 |
| BI / API reportes | — | 📋 |

→ Auditorías: [08-reportes-audit.md](modules/08-reportes-audit.md) · [02-reports-audit.md](modules/02-reports-audit.md)

### MRG-09 · Flujos transversales · Fase 8 ✅ cerrada 2026-07-10

| Entidad / flujo MRG | Ruta / código | Estado |
|---------------------|---------------|--------|
| Incidencia → OT | `incidencias_crear_ot` | ✅ |
| Resolver sin OT | `incidencias_resolver` | ✅ |
| OT preventiva anual | `crear_programacion_preventiva_anio` | ✅ |
| Planeación mensual | `/ordenes/planeacion` | ✅ |
| Consumo repuestos OT | `_guardar_repuestos_orden` | 🟡 correctiva |
| Compra → stock | `registrar_entrada_mercancia` | ✅ |
| Venta → stock | `registrar_venta` | ✅ |
| Cobros / abonos | `InvVentaCobro` | ✅ |
| Onboarding | `/onboarding` | ✅ |
| IAM por rol | `permissions.py` · `/equipo` | ✅ |
| Sync estados OT | `sincronizar_estados_ordenes` | ✅ |
| CRM → venta | — | 📋 |
| Purchasing formal | — | 📋 |

→ Auditoría: [09-workflows-audit.md](modules/09-workflows-audit.md)

---

*Actualizar esta matriz al cerrar cada fase de Sprint 14.*
