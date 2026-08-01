# Sprint 23.4 · Reporte en curso

Fecha de corte: 2026-07-30
Estado: observabilidad, workers, monitor externo y outbox desplegados; escalón de carga de 1 usuario aprobado, concurrencia 5/10/20 pendiente.

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

- Completar los runbooks y ejecutar los escalones de carga de 5, 10 y 20 usuarios.
- Mejorar la entregabilidad del correo operativo mediante SPF, DKIM y DMARC.
- Actualizar las acciones de GitHub que aún generan la advertencia de
  compatibilidad con Node.js 20.

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

## Avance 3 · Monitor externo y gate operativo

- El panel de infraestructura incorpora una tarjeta segura de observabilidad:
  informa si Sentry, el token de métricas y el destino de alertas están activos
  sin exponer sus valores.
- El SuperAdmin dispone de una prueba controlada y auditada para Sentry y correo
  operativo; no altera datos de tenants ni degrada dependencias.
- GitHub Actions ejecuta un monitor externo cada cinco minutos contra liveness y
  readiness.
- El monitor considera `degraded` como fallo operativo, conserva el fallo del
  workflow como canal independiente e intenta notificar por SMTP.
- Se versionó el runbook `SPRINT23.4-OBSERVABILITY-RUNBOOK.md` con configuración,
  gate remoto y respuesta operativa.

### Criterios del gate remoto

- [x] Confirmar la tarjeta **Observabilidad · Operativa** en producción.
- [x] Ejecutar manualmente el workflow externo y registrar el run.
- [x] Enviar, con confirmación de la responsable, una alerta controlada y
  comprobar Sentry, correo y auditoría.
- [x] Implementar la outbox cifrada de correos/notificaciones y comprobar la
  recuperación de cuenta mediante el worker.
- [ ] Ejecutar la prueba de carga antes de cerrar completamente Sprint 23.4.

### Gate remoto parcial · 2026-07-29

- Roustix `1.0.32` desplegada desde `366fe4e`.
- `/health/ready`: PostgreSQL, migraciones, Redis y worker en verde.
- Panel: SMTP operativo con autenticación correcta; worker activo y health
  saludable.
- Bloqueo encontrado: la tarjeta **Observabilidad** reporta ausentes
  `SENTRY_DSN`, `METRICS_TOKEN` y `OPS_ALERT_EMAIL`.
- La alerta controlada no se ejecutó: hacerlo sin esos destinos produciría una
  evidencia inválida. Deben configurarse las variables y repetir el gate.

### Gate de alerta controlada · 2026-07-29

- Responsable: Gladis Rocio Gelves Pabon.
- La tarjeta **Observabilidad** quedó en estado **Operativa** después de
  configurar `SENTRY_DSN`, `METRICS_TOKEN` y `OPS_ALERT_EMAIL`.
- Sentry recibió un evento del endpoint auditado de prueba en el proyecto
  Roustix (`ROUSTIX-FRASCO-1`).
- El correo `[Roustix][WARNING] operations: controlled_test` fue recibido a las
  `2026-07-30 04:26 UTC` (`2026-07-29 23:26`, hora de Colombia).
- Veredicto del canal de alertas: **aprobado** para Sentry y SMTP.
- Observación: Outlook clasificó el mensaje como correo no deseado. La entrega
  funciona, pero deben validarse SPF, DKIM, DMARC y alineación del remitente
  antes del piloto.
- El nombre del remitente se corrigió en producción a
  `Roustix <gladis.rocio.gelves.pabon@gmail.com>`.
- La auditoría fue verificada mediante consulta de solo lectura en producción:
  registro `ops_alert_test` ID `60`, fecha `2026-07-30 04:26:54 UTC`, actor
  `Soporte Roustix (Plataforma)` y detalle de prueba controlada.
- GitHub Actions registró `uptime-monitor.yaml` después de incorporar un
  disparador limitado a cambios del propio workflow y publicar la definición
  operativa en la rama predeterminada `develop`.
- La primera ejecución manual detectó correctamente que `develop` aún no
  contenía `scripts/monitor_health.py`; el script se publicó de forma aislada y
  se repitió el gate.
- Ejecución manual final `30515172554`: **Success**, duración total `14 s`, job
  `health` aprobado en `9 s`, evento `workflow_dispatch`, commit `8ed2af8`.
- Veredicto del gate operativo: **aprobado** para monitor externo, Sentry,
  correo y auditoría.

## Avance 4 · Outbox cifrada y recuperación

- `email_outbox` cifra destinatario, asunto y contenido mediante Fernet.
- El worker entrega verificación, bienvenida y recuperación con leases,
  idempotencia por empresa y reintentos controlados.
- `OUTBOX_ENCRYPTION_KEY` fue configurada con el mismo valor en web y worker.
- La recuperación real fue aprobada en producción: correo recibido, cambio de
  contraseña, rechazo del enlace reutilizado y revocación de sesión anterior.
- La versión `1.0.37` quedó saludable en producción desde `805d14a`.
- El cierre total de la certificación de outbox requiere todavía comprobar un
  código nuevo de verificación y ejecutar un ensayo remoto de idempotencia.
