# Sprint 23.2 · Reporte de cierre

## Resultado

El hardening de identidad y plataforma quedó implementado y validado localmente
sin cambios de esquema ni migraciones nuevas.

## Controles entregados

- Arranque productivo fail-fast: exige secreto robusto, PostgreSQL, S3/R2,
  endpoint HTTPS y correo transaccional configurado.
- `ProxyFix` limitado a un salto y allowlist opcional de hosts mediante
  `TRUSTED_HOSTS` y `RENDER_EXTERNAL_HOSTNAME`.
- Cookies seguras, protección fuerte de Flask-Login, HSTS, cabeceras defensivas
  y `Cache-Control: no-store` en pantallas de identidad y plataforma.
- Panel privilegiado con clave comparada en tiempo constante, MFA TOTP
  obligatorio en producción, desafío de cinco minutos y sesión no permanente
  con 15 minutos de inactividad y 120 minutos absolutos.
- Auditoría de acceso exitoso/fallido, MFA fallido/expirado, expiración de sesión
  y logout de plataforma.
- JWT de ocho horas con `auth_version`, `jti` y `nbf`; cada petición revalida
  usuario, estado, empresa, slug y rol contra la base de datos.
- Contraseñas nuevas entre 12 y 128 caracteres y rechazo temprano de entradas
  excesivas antes de ejecutar el hash.
- Dirección IP obtenida desde `remote_addr` después del proxy confiable, sin
  confiar directamente en un `X-Forwarded-For` enviado por el cliente.

## Validación

- 12 pruebas focalizadas de hardening.
- Pruebas existentes de identidad y sesiones conservadas.
- Suite completa: 237 pruebas aprobadas en 122.326 segundos.
- Migraciones: no aplica; el sprint no modifica el esquema.

## Gate de despliegue en Render

Antes de fusionar a `main`, verificar estas variables en producción:

- `SECRET_KEY`: valor aleatorio de al menos 32 caracteres.
- `DATABASE_URL`: conexión PostgreSQL/Neon.
- `STORAGE_BACKEND=s3` y credenciales operativas de Cloudflare R2.
- `MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD` y `MAIL_DEFAULT_SENDER`.
- `PLATFORM_ADMIN_KEY`: valor aleatorio de al menos 32 caracteres, si se usa el panel.
- `PLATFORM_ADMIN_TOTP_SECRET`: secreto Base32 válido cuando el panel está habilitado.
- `PLATFORM_MFA_REQUIRED=true`.
- `TRUSTED_HOSTS`: dominio público de Roustix y hostname de Render separados por coma.

Si falta un requisito crítico, Roustix rechazará el arranque en producción de
forma intencional para impedir una operación insegura o no persistente.

## Riesgo residual y continuidad

- MFA para usuarios tenant requiere enrolamiento y recuperación propios.
- CSP todavía admite código inline de plantillas existentes.
- Rate limits distribuidos, CI PostgreSQL, E2E, observabilidad y operación de
  workers continúan en los bloques 23.3 y 23.4.