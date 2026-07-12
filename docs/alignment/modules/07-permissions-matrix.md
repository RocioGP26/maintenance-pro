# MRG-07 · Matriz de permisos · IAM tenant

**Actualización 2026-07-11** · Fuente: [MRG-07 §3](/mrg/chapters/07-administracion.md) · Código: `app/permissions.py`

---

## Roles de plataforma

| Rol | Clave | Mantenimiento | Inventario comercial |
|-----|-------|---------------|----------------------|
| Superadministrador | `superadmin` | Completo | Completo |
| Administrador | `admin` | Operativo + equipo | Operativo + equipo |
| Supervisor | `supervisor` | Coordinar · asignar · estados | Coordinación operativa |
| Técnico | `tecnico` | OT · incidencias | Sin acceso |
| Vendedor | `vendedor` | Incidencias propias | Inventario · ventas · clientes |
| Usuario — solo consulta | `usuario` | Lectura general | Lectura general |
| Solicitante / Reportante | `solicitante` | Reportar · incidencias propias | Sin acceso operativo |

`tecnico` y `vendedor` son roles independientes. Tener ambos módulos contratados no amplía automáticamente el acceso del rol.

Regla adicional por área: `admin` + área **Mantenimiento** no accede a Inventario. `superadmin` permanece sin esta restricción.

---

## Matriz transversal · Acciones IAM

| Acción | Superadmin | Admin | Supervisor | Técnico | Vendedor | Usuario | Solicitante | Helper |
|--------|:----------:|:-----:|:----------:|:-------:|:--------:|:-------:|:-----------:|--------|
| Crear catálogos | ✅ | ✅ | ✅ | ❌ | Operación comercial | ❌ | ❌ | `can_create` |
| Editar operación | ✅ | ✅ | ✅ | Mantenimiento | Inventario | ❌ | Reportar | `can_edit` |
| Eliminar registros | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | `can_delete` |
| Configuración empresa | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | `can_manage_config` |
| Gestionar usuarios | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | `can_manage_equipo` |
| Resolver incidencias | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ | `can_manage_incidents` |
| Reportar incidencias | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ | `can_report_incident` |
| Acceder a Mantenimiento | ✅ | ✅ | ✅ | ✅ | Solo incidencias | ✅ | Solo incidencias | `can_access_maintenance` |
| Acceder a Inventario | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ | `can_access_inventory` |

---

## Flags de plantilla (`permission_flags`)

| Flag | Uso en navegación / UI |
|------|-------------------------|
| `perm.crear` | Botones de alta |
| `perm.editar` | Edición operativa |
| `perm.eliminar` | Borrado |
| `perm.config` | Administración → configuración |
| `perm.equipo` | Administración → usuarios |
| `perm.solo_lectura` | Restricción global de escritura |
| `perm.solicitante` | Navegación exclusiva del reportante |
| `perm.vendedor` | Navegación comercial + incidencias propias |
| `perm.acceso_mantenimiento` | Visibilidad de Mantenimiento |
| `perm.acceso_inventario` | Visibilidad de Inventario |
| `perm.reportar_incidencia` | Reportar incidencias |
| `perm.gestionar_incidencias` | Resolver incidencias |
| `perm.crear_ot` | OT desde incidencia |

---

## Desviaciones documentadas

| # | MRG | Producto | Estado |
|---|-----|----------|--------|
| D1 | Admin configura avanzado | Solo superadmin | 🟡 Más restrictivo |
| D2 | Supervisor independiente | `supervisor` | ✅ Resuelto |
| D3 | Técnico y Vendedor separados | `tecnico` · `vendedor` | ✅ Resuelto |
| D4 | Invitación por email | Manual / formulario | 🟡 Pendiente automatización |

---

→ [Auditoría Fase 6](07-admin-audit.md) · [MRG-02 permisos mantenimiento](02-permissions-matrix.md)
