# Sprint 23.2 · Auditoría inicial

## Controles existentes reutilizados

| Control | Estado inicial |
| --- | --- |
| Idle y absolute timeout tenant | Implementado en Sprint 18 |
| Sesiones activas y revocación remota | Implementado |
| `auth_version` para Flask-Login | Implementado |
| Rate limit de login y recuperación | Implementado en memoria |
| Recuperación y verificación por correo | Implementado |
| Cookies Secure/HttpOnly/SameSite | Implementado en producción |
| CSRF | Implementado |
| MFA del panel de plataforma | Disponible, pero opcional |

## Brechas confirmadas

| Riesgo | Severidad | Evidencia | Tratamiento 23.2 |
| --- | --- | --- | --- |
| Producción puede iniciar con SQLite | Crítica | `ProductionConfig` solo registra warning | Fail-fast |
| Producción puede usar archivos locales | Crítica | `STORAGE_BACKEND` solo registra warning | Fail-fast S3 |
| Plataforma funciona sin TOTP | Crítica | TOTP depende de secreto opcional | MFA requerido si el panel está habilitado |
| Sesión de plataforma hereda 14 días | Alta | `session.permanent = True` | Idle y absolute timeout propios |
| Clave privilegiada usa igualdad normal | Media | Comparación directa en login | `compare_digest` |
| JWT no se revoca con contraseña | Crítica | No contiene ni valida `auth_version` | Vinculación y consulta viva |
| JWT confía en tenant y rol firmados | Alta | Middleware copia claims a `g` | Revalidación contra BD |
| Proxy/Host no están explícitos | Alta | Sin `ProxyFix` ni allowlist | Proxy confiable y host guard |
| CSP conserva `unsafe-inline` | Media | Plantillas inline existentes | Roadmap con nonce/hash |

## Decisión

Sprint 23.2 endurece los límites de confianza existentes. No crea un segundo
sistema de sesiones tenant ni mezcla el enrolamiento MFA por usuario con el
acceso excepcional de superadministración.
