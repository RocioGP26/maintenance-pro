# Fase 6 · Auditoría MRG-07 · Administración e IAM

**Sprint 14.21–14.24** · **Estado:** ✅ **Fase 6 cerrada** (2026-07-10)  
**MRG:** [MRG-07-ADMIN](/mrg/chapters/07-administracion.md)  
**Última revisión:** 2026-07-10

---

## 1 · Resumen ejecutivo

| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué existe? | Usuarios/roles tenant · config empresa · campos custom · onboarding · Mantis `/platform/` |
| ¿Qué hace? | IAM tenant + aislamiento multi-tenant · plataforma SaaS separada |
| ¿Qué falta? | Invitación email E2E · multisede completa · API admin MAG |
| ¿Qué sobra? | — |
| ¿Qué difiere del MRG? | Config avanzada solo superadmin (MRG tabla dice Admin parcial) |

**Estado módulo:** ✅ **Producción** (núcleo) · **Sprint 14 Fase 6:** ✅ **Cerrado**

---

## 2 · MRG §1–§2 · Alcance y niveles

| Nivel | Ruta | Estado |
|-------|------|--------|
| Tenant | `/equipo` · `/configuracion/*` · onboarding | ✅ |
| Plataforma Mantis | `/platform/*` | ✅ |
| Aislamiento tenant | `empresa_id` · `query_tenant` | ✅ |

---

## 3 · MRG §3 · Usuarios y roles

| Rol | Clave | Estado |
|-----|-------|--------|
| Superadministrador | `superadmin` | ✅ |
| Administrador | `admin` | ✅ |
| Supervisor | `supervisor` | ✅ independiente |
| Técnico | `tecnico` | ✅ solo Mantenimiento |
| Vendedor | `vendedor` | ✅ solo Inventario + reportante |
| Usuario — solo consulta | `usuario` | ✅ |
| Solicitante / Reportante | `solicitante` | ✅ incidencias propias |

→ Matriz completa: [07-permissions-matrix.md](07-permissions-matrix.md) · Mantenimiento: [02-permissions-matrix.md](02-permissions-matrix.md)

---

## 4 · MRG §4 · Gestión de usuarios

| Operación | Estado | Notas |
|-----------|--------|-------|
| Crear usuario | ✅ | `/equipo/nuevo` |
| Asignar roles | ✅ | `roles_for_select` |
| Desactivar / reactivar | ✅ | |
| Editar perfil propio | ✅ | `/mi-perfil` |
| Restablecer contraseña | ✅ | en formulario equipo |
| Invitación por email | 🟡 | copy «Invitar» · sin email automático |
| Auditoría tenant | ✅ | `TenantActivityLog` |

---

## 5 · MRG §5–§7 · Tenant · sedes · configuración

| Área | Estado |
|------|--------|
| Datos empresa (razón social, NIT…) | ✅ |
| Logo · moneda · zona horaria | ✅ |
| Módulos activos | ✅ |
| Sedes | 🟡 sede en usuario · activos |
| Campos personalizados | ✅ superadmin |
| Plan / sector onboarding | ✅ |

---

## 6 · MRG §8–§9 · Onboarding y Mantis

| Flujo | Estado |
|-------|--------|
| Wizard onboarding | ✅ `/onboarding` |
| Datos ejemplo por sector | ✅ |
| Platform tenants | ✅ |
| Planes · suspensión · impersonación | ✅ |
| Facturación SaaS | 🟡 |

---

## 7 · MRG §10 · Seguridad

| Mecanismo | Estado |
|-----------|--------|
| Permisos por rol | ✅ `permissions.py` |
| Guards before_request | ✅ |
| JWT API | 🟡 login v1 |
| Auditoría | ✅ tenant + platform |

---

## 8 · Menús y copy

| Elemento | Objetivo MRG | Estado |
|----------|--------------|--------|
| Sección Administración | Submenú | ✅ |
| Equipo → Usuarios y roles | MRG §4 | ✅ |
| Configuración empresa | superadmin | ✅ |
| Campos personalizados | superadmin | ✅ |

---

## 9 · API MAG

| Endpoint | Estado |
|----------|--------|
| `/api/v1/admin/users` | 📋 |
| `/api/v1/admin/summary` | 🟡 parcial |
| `/api/v1/platform/*` | 📋 |

---

## 10 · Checklist Fase 6 · ✅ Cerrada

| # | Área | Estado |
|---|------|--------|
| 1 | Roles IAM | ✅ |
| 2 | Matriz permisos | ✅ |
| 3 | Nav administración | ✅ |
| 4 | Equipo / usuarios | ✅ |
| 5 | Config tenant | ✅ |
| 6 | Onboarding | ✅ |
| 7 | Mantis | ✅ |
| 8 | API | 🟡 |
| 9 | MRG badges | ✅ |

---

## 11 · Rutas verificadas

```
/equipo · /equipo/nuevo · /equipo/<id>/editar · /mi-perfil
/configuracion/empresa · /configuracion/campos
/onboarding
/platform/ (Mantis)
/api/v1/admin/summary
```

---

## 12 · Gaps abiertos (📋)

- Invitación email automatizada
- Multisede en todos los módulos
- Admin (no superadmin) config empresa parcial
- API MAG admin completa

---

## 13 · Próximos pasos

1. ~~**Cerrar MRG-07 Fase 6**~~ — ✅ 2026-07-10
2. **Fase 7** — MRG-08 Reportes ([checklist](../checklist.md#fase-7--mrg-08--reportes))

---

→ [Checklist maestro](../checklist.md) · [Matriz de estado](../status-matrix.md)
