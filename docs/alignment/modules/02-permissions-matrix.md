# MRG-02 · Matriz de permisos · Mantenimiento

**Sprint 14.2** · Fuente: [MRG-02 §2](/mrg/chapters/02-maintenance.md) · Código: `app/permissions.py`

---

## Correspondencia de roles

| Rol MRG | Rol plataforma | Enum |
|---------|----------------|------|
| Administrador | Superadmin · Admin | `superadmin` · `admin` |
| Supervisor | Admin *(legacy `supervisor` → admin)* | `admin` |
| Técnico | Técnico | `tecnico` |
| Solicitante | Usuario | `usuario` |
| Proveedor externo | — | Sin login |

---

## Matriz funcional · Mantenimiento

| Acción | Superadmin | Admin | Técnico | Usuario | Implementación |
|--------|:----------:|:-----:|:-------:|:-------:|----------------|
| Ver dashboard / listados | ✅ | ✅ | ✅ | ✅ | Lectura global |
| Crear activos / tipos | ✅ | ✅ | ❌ | ❌ | `can_create` |
| Editar activos / OT | ✅ | ✅ | ✅ | ❌ | `can_edit` |
| Eliminar registros | ✅ | ✅ | ❌ | ❌ | `can_delete` |
| Configuración empresa | ✅ | ❌ | ❌ | ❌ | `can_manage_config` |
| Gestionar equipo (IAM) | ✅ | ✅ | ❌ | ❌ | `can_manage_equipo` |
| **Reportar incidencia** | ✅ | ✅ | ✅ | ✅ | `USUARIO_POST` + `can_report_incident` |
| **Ver incidencias** | Todas | Todas | Todas | Solo propias | `_incidents_scope_query` |
| **Resolver incidencia** | ✅ | ✅ | ✅ | ❌ | `can_manage_incidents` |
| **Crear OT desde incidencia** | ✅ | ✅ | ❌ | ❌ | `can_create_work_order` |
| Crear OT directa | ✅ | ✅ | ❌ | ❌ | `can_create` + `CREATE_GET` |
| Ejecutar OT (jornadas) | ✅ | ✅ | ✅ | ❌ | `can_edit` en OT |

---

## Helpers Sprint 14

| Función | Uso |
|---------|-----|
| `can_report_incident(user)` | Formulario `/incidencia` |
| `can_manage_incidents(user)` | Resolver incidencias |
| `can_create_work_order(user)` | Crear OT desde incidencia |
| `permission_flags` → `gestionar_incidencias` | Plantillas |
| `permission_flags` → `crear_ot` | Plantillas |
| `permission_flags` → `reportar_incidencia` | Plantillas |

---

## Desviaciones documentadas

| # | MRG | Producto | Estado |
|---|-----|----------|--------|
| D1 | Supervisor = rol distinto | Mapeado a Admin | 🟡 Aceptado |
| D2 | Técnico no crea OT | `can_create` = false | ✅ |
| D3 | Técnico puede resolver incidencia | `can_manage_incidents` incluye técnico | 🟡 Operativo |
| D4 | Asignación explícita incidencia → supervisor | Sin UI de asignación | 📋 Roadmap |
| D5 | Proveedor externo sin login | Referenciado en OT externa | ✅ doc |

---

## Endpoints protegidos · Incidencias

| Endpoint | Método | Permiso |
|----------|--------|---------|
| `main.incidencia` | GET/POST | Autenticado; POST también Usuario |
| `main.incidencias_list` | GET | Autenticado; scope Usuario = propias |
| `main.incidencias_detail` | GET | Scope por rol |
| `main.incidencias_resolver` | POST | `can_manage_incidents` |
| `main.incidencias_crear_ot` | POST | `can_create_work_order` |

---

→ [Auditoría Fase 1](02-maintenance-audit.md) · [Checklist](../checklist.md)
