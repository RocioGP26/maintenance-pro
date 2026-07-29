# Sprint 23.4 · Reporte en curso

Fecha de corte: 2026-07-28  
Estado: implementación local verificada; configuración y validación remota pendientes.

## Cierre previo registrado

- Sprint 23.1: backup de producción `30406614706` exitoso, restaurado y replicado.
- Sprint 23.2: desplegado en producción como parte de `v1.0.18`.
- Sprint 23.3: CI remota `30405490818` aprobada y cambios integrados en producción.

## Implementado en este avance

- ID de correlación global, validado y devuelto en `X-Request-Id`.
- Logs HTTP estructurados con endpoint, estado, duración, usuario y empresa cuando aplican.
- Captura opcional de excepciones mediante Sentry, sin cuerpo, cookies ni credenciales.
- Métricas Prometheus de volumen, latencia, errores no controlados y versión.
- Endpoint privado `GET /internal/metrics`, protegido por `X-Metrics-Token`.
- Readiness con latencia de base de datos y estado degradado configurable.
- Alertas deduplicadas para DB, SMTP, almacenamiento S3/R2 y webhooks.
- Avisos por correo al soporte para eventos operativos distintos de una caída SMTP.
- Aviso independiente de GitHub Actions cuando falla el backup de producción.

## Configuración requerida

- `SENTRY_DSN` y `SENTRY_TRACES_SAMPLE_RATE`.
- `METRICS_TOKEN` de al menos 32 caracteres en producción.
- `OPS_ALERT_EMAIL` y credenciales SMTP válidas.
- `OPS_ALERT_COOLDOWN_SECONDS` y `DB_HEALTH_DEGRADED_MS`.
- Los mismos secretos SMTP y `OPS_ALERT_EMAIL` en GitHub Actions para alertar backups.

## Evidencia local

- `tests.test_observability`: 6 pruebas aprobadas.
- Regresión de almacenamiento, webhooks, seguridad de webhooks y API pública:
  18 pruebas aprobadas.
- Suite unitaria completa: 247 pruebas aprobadas.
- Compilación de `app`, `scripts` y `tests`: aprobada.
- Validación sintáctica de `backup.yml` y `render.yaml`: aprobada.

## Pendiente para el siguiente avance

- Conectar Sentry y el recolector Prometheus en producción y provocar alertas controladas.
- Configurar un monitor externo contra `/health/live` y `/health/ready`.
- Implementar la outbox cifrada para correos y notificaciones.
- Versionar runbooks completos y ejecutar la prueba de carga.
- Confirmar en el dashboard que `mantis-app` usa el plan `starter`; el blueprint
  ya lo declara, pero el archivo no demuestra el estado real del servicio remoto.

## Avance 2 · Redis y worker

- Flask-Limiter usa `REDIS_URL` como almacenamiento distribuido en producción.
- La configuración productiva rechaza el fallback `memory://`.
- `render.yaml` declara Render Key Value y un background worker en plan `starter`.
- El worker procesa la outbox durable de webhooks y recupera leases vencidos.
- PostgreSQL reclama lotes con `FOR UPDATE SKIP LOCKED` para permitir varios workers.
- Los intentos reclamados se confirman antes de la llamada externa y cada resultado
  se confirma individualmente.
- Redis coordina el lock de mantenimiento y el heartbeat del worker.
- Readiness comprueba Redis y reporta heartbeat ausente como degradación.
- El runbook operativo quedó versionado en `SPRINT23.4-WORKERS-RUNBOOK.md`.
- Pruebas focalizadas del avance: 43 aprobadas.

Los correos y notificaciones todavía no se trasladaron al worker: requieren una
outbox cifrada para no persistir códigos de verificación ni tokens crudos.
