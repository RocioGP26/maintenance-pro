# MPA-07-SEC · Seguridad

**Código:** MPA-07-SEC · Sprint 6.7

> La confianza de una EMP se gana en **login, permisos y auditoría** — especialmente en multi-tenant.

---

## 1 · Modelo de amenazas (resumen)

| Amenaza | Mitigación |
|---------|------------|
| Acceso cross-tenant | `empresa_id` obligatorio + middleware |
| Escalación de privilegios | Roles + checks en `permissions.py` |
| CSRF en web | Flask-WTF / tokens |
| API abuse | JWT expiración, rate limits (evolución) |
| Pérdida de datos | Backups automáticos |
| Cuenta comprometida | MFA plataforma (evolución por tenant) |

---

## 2 · Login y sesión

| Canal | Mecanismo |
|-------|-----------|
| Web app | Flask-Login, sesión segura |
| API | JWT Bearer (`app/tenancy/jwt_auth.py`) |
| Platform | Superadmin separado |

**Buenas prácticas:**

- Contraseñas hasheadas (werkzeug)
- Logout en todas las rutas sensibles
- Página de cuenta suspendida

---

## 3 · Permisos

- Matriz rol × acción en `permissions.py`
- Decoradores y checks en rutas críticas
- Módulo inactivo = 403 aunque el rol sea admin

**Regla:** «Si está en el menú» no es seguridad. «Si pasa el check en el servidor» sí.

---

## 4 · Auditoría

- `app/platform_audit.py` — registro de acciones de plataforma
- Impersonación registrada
- Visibilidad de auditoría para admin de empresa (según política)

Eventos auditables (evolución):

- Cambios de plan y módulos
- Altas/bajas de usuarios
- Export masivo de datos
- Cambios de configuración crítica

---

## 5 · Backups

| Aspecto | Detalle |
|---------|---------|
| Frecuencia | Job programado + CLI manual |
| Formatos | `.db` (SQLite) · `.sql.gz` (PostgreSQL) |
| Retención | 7 días por defecto (`prune_old_backups`) |
| Ubicación | `BACKUP_DIR` env |

**RPO/RTO:** objetivos por definir en operaciones — documentar en Developer Docs (09) al formalizar SRE.

---

## 6 · Logs

- Logging estructurado en servicios críticos (backup, tenancy)
- Evolución: correlación por `request_id` y `empresa_id`
- Sin datos sensibles en logs (contraseñas, tokens)

---

## 7 · 2FA / MFA

| Estado | Alcance |
|--------|---------|
| 🟡 En evolución | MFA en rutas `/platform/` |
| 📋 Planificado | MFA opcional por empresa (IAM) |

---

## 8 · Roles · resumen

| Rol | Riesgo si mal asignado |
|-----|------------------------|
| `admin` | Configuración total del tenant |
| `tecnico` | Datos operativos sensibles |
| `usuario` | Lectura de información interna |
| Platform superadmin | **Todos** los tenants |

Principio de mínimo privilegio en invitaciones de equipo.

---

## Documentación relacionada

- Detalle operativo futuro: [security/README.md](../../security/README.md)
- MADR de decisiones de auth: [madr/README.md](../../madr/README.md)

---

## Siguiente

→ [MPA-08-SCALE · Escalabilidad](08-escalabilidad.md)
