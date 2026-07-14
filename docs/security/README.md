# Seguridad e Identidad

Esta guía define la política operativa de sesiones de Maintix. Desde Sprint 18,
la autenticación web combina la cookie firmada de Flask-Login con un registro
revocable en servidor (`active_sessions`). Una cookie válida no es suficiente si
la sesión fue revocada, superó su inactividad o alcanzó su tiempo máximo.

## Política por tenant

| Parámetro | Predeterminado | Rango seguro |
|---|---:|---:|
| Inactividad | 30 min | 10–60 min |
| Duración absoluta | 8 h | 1–12 h |
| Advertencia | 2 min | Menor que inactividad |
| Recordarme | Desactivado | 14 días si se permite |
| Múltiples sesiones | Permitidas | Sí / No |
| Revocar al cambiar contraseña | Sí | Sí / No |

La configuración está disponible para superadministradores y administradores en
`Administración → Seguridad y sesiones`.

## Controles

- Cada petición y cada interacción web relevante renuevan la última actividad.
- El tiempo absoluto nunca se renueva durante la misma sesión.
- La advertencia permite continuar o cerrar sesión; no genera actividad sin una
  acción del usuario.
- Cambiar correo, desactivar/bloquear usuario o suspender empresa revoca accesos.
- El cambio de contraseña incrementa `auth_version`, invalidando cookies firmadas.
- Las sesiones pueden finalizarse remotamente y cada evento queda auditado.

## Operación

Aplicar la migración `t7j0l48r51u9` antes de desplegar. En producción deben
mantenerse cookies `Secure`, `HttpOnly` y `SameSite=Lax`, ya configuradas en
`ProductionConfig`.

Ver también [reporte de Sprint 18](SPRINT18-REPORT.md).
