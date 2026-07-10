# MRG-07 · Matriz de permisos · IAM tenant

**Sprint 14.22** · Fuente: [MRG-07 §3](/mrg/chapters/07-administracion.md) · Código: `app/permissions.py`

---

## Roles de plataforma

| Rol | Clave | Mantenimiento | Inventario comercial |
|-----|-------|---------------|----------------------|
| Superadministrador | `superadmin` | Completo | Completo |
| Administrador | `admin` | Operativo + equipo | Operativo + equipo |
| Técnico | `tecnico` | OT · incidencias | — |
| Vendedor | `tecnico` *(label)* | — | Ventas · clientes |
| Vendedor / Técnico | `tecnico` *(ambos módulos)* | OT | Ventas |
| Usuario | `usuario` | Lectura · incidencias | Lectura |

---

## Matriz transversal · Acciones IAM

| Acción | Superadmin | Admin | Técnico/Vendedor | Usuario | Helper |
|--------|:----------:|:-----:|:----------------:|:-------:|--------|
| Crear catálogos | ✅ | ✅ | ❌ | ❌ | `can_create` |
| Editar operación | ✅ | ✅ | ✅ | ❌ | `can_edit` |
| Eliminar registros | ✅ | ✅ | ❌ | ❌ | `can_delete` |
| Configuración empresa | ✅ | ❌ | ❌ | ❌ | `can_manage_config` |
| Campos personalizados | ✅ | ❌ | ❌ | ❌ | `can_manage_config` |
| Gestionar usuarios | ✅ | ✅ | ❌ | ❌ | `can_manage_equipo` |
| Asignar superadmin | ✅ | ❌ | ❌ | ❌ | `can_assign_role` |
| Solo lectura | ✅ | ✅ | ✅ | ✅ | `is_read_only` |

---

## Flags plantilla (`permission_flags`)

| Flag | Uso nav / UI |
|------|--------------|
| `perm.crear` | Botones alta |
| `perm.editar` | Edición |
| `perm.eliminar` | Borrado |
| `perm.config` | Administración → config |
| `perm.equipo` | Administración → usuarios |
| `perm.solo_lectura` | Restricción POST |
| `perm.reportar_incidencia` | Incidencias |
| `perm.gestionar_incidencias` | Resolver incidencias |
| `perm.crear_ot` | OT desde incidencia |

---

## Desviaciones documentadas

| # | MRG | Producto | Estado |
|---|-----|----------|--------|
| D1 | Admin config avanzada | Solo superadmin | 🟡 Más restrictivo |
| D2 | Supervisor rol | → `admin` legacy | 🟡 Aceptado |
| D3 | Invitación email | Manual / formulario | 🟡 |

---

→ [Auditoría Fase 6](07-admin-audit.md) · [MRG-02 permisos mant.](02-permissions-matrix.md)
