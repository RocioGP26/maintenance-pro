# Sprint 23.4 · Runbook de observabilidad y alertas

## Objetivo

Comprobar que Roustix detecta una degradación desde fuera de Render, conserva
correlación en sus logs y entrega una alerta segura a Sentry y al correo de
operaciones.

## Configuración productiva

### Render · `mantis-app`

- `SENTRY_DSN`
- `SENTRY_TRACES_SAMPLE_RATE=0.1`
- `METRICS_TOKEN` aleatorio de al menos 32 caracteres
- `OPS_ALERT_EMAIL`
- `OPS_ALERT_COOLDOWN_SECONDS=300`
- `DB_HEALTH_DEGRADED_MS=750`
- SMTP real (`MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD` y
  `MAIL_DEFAULT_SENDER`)

### GitHub Actions

El workflow `uptime-monitor.yml` requiere los mismos secretos SMTP y
`OPS_ALERT_EMAIL`. Ejecuta cada cinco minutos:

- `GET /health/live`
- `GET /health/ready`

Un HTTP distinto de 200, una respuesta inválida o `status != ok` hace fallar el
workflow y dispara el aviso por correo cuando SMTP está disponible.

## Gate remoto

1. Abrir **Platform → Infraestructura**.
2. Confirmar **Observabilidad · Operativa** sin mostrar DSN, token ni correo.
3. Confirmar SMTP, workers y health check en verde.
4. Ejecutar manualmente `Roustix uptime monitor` en GitHub Actions y comprobar
   resultado verde.
5. Pulsar **Enviar alerta de prueba** una sola vez.
6. Confirmar el evento `operations / controlled_test` en Sentry.
7. Confirmar la recepción del correo operativo.
8. Verificar el registro `ops_alert_test` en la auditoría de plataforma.

La prueba controlada no modifica datos de tenants ni fuerza la caída de ninguna
dependencia. No deben simularse fallos de PostgreSQL, Redis o R2 en producción.

## Evidencia

| Campo | Resultado |
| --- | --- |
| Fecha Colombia | Pendiente |
| Responsable | Pendiente |
| Commit / versión | Pendiente |
| Panel Observabilidad | Pendiente |
| Workflow externo | Pendiente |
| Evento Sentry | Pendiente |
| Correo operativo | Pendiente |
| Auditoría | Pendiente |
| Veredicto | Pendiente |

## Respuesta

- **Aplicación caída:** revisar deploy y logs de Render; mantener el monitor en
  fallo hasta recuperar `/health/live`.
- **Readiness degradado:** identificar la tarjeta afectada (DB, Redis o worker),
  aplicar el runbook correspondiente y validar tres ejecuciones verdes.
- **Correo no entregado:** conservar Sentry y el fallo de GitHub como canales
  alternos; revisar credenciales SMTP sin imprimirlas.
- **Sentry no recibe:** confirmar DSN y release; los logs estructurados continúan
  siendo la evidencia primaria durante la recuperación.
