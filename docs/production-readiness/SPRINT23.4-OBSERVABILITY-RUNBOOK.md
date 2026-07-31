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

El workflow `uptime-monitor.yaml` requiere los mismos secretos SMTP y
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
| Fecha Colombia | 2026-07-29 |
| Responsable | Gladis Rocio Gelves Pabon |
| Commit / versión | `366fe4e` · `1.0.32` |
| Panel Observabilidad | ✅ Operativa; Sentry, métricas y correo configurados |
| Workflow externo | ✅ Ejecución manual `30515172554` aprobada en 14 s (`health` en verde) |
| Evento Sentry | ✅ `platforma.infraestructura_probar_alerta` recibido en el proyecto Roustix (`ROUSTIX-FRASCO-1`) |
| Correo operativo | ✅ Alerta `operations / controlled_test` recibida a las 2026-07-30 04:26 UTC (2026-07-29 23:26 Colombia) |
| Auditoría | ✅ Registro `ops_alert_test` ID 60 confirmado en PostgreSQL de producción (`2026-07-30 04:26:54 UTC`) |
| Veredicto | ✅ Gate aprobado: monitor externo, Sentry, correo y auditoría operativos |

### Observación de entregabilidad

Outlook recibió correctamente la alerta, pero la clasificó como **Correo no
deseado**. La ruta SMTP queda funcional; antes del piloto se debe revisar SPF,
DKIM, DMARC y la alineación del remitente para mejorar la entrega en bandeja de
entrada. El nombre de remitente fue corregido en producción a
`Roustix <gladis.rocio.gelves.pabon@gmail.com>`.

## Respuesta

- **Aplicación caída:** revisar deploy y logs de Render; mantener el monitor en
  fallo hasta recuperar `/health/live`.
- **Readiness degradado:** identificar la tarjeta afectada (DB, Redis o worker),
  aplicar el runbook correspondiente y validar tres ejecuciones verdes.
- **Correo no entregado:** conservar Sentry y el fallo de GitHub como canales
  alternos; revisar credenciales SMTP sin imprimirlas.
- **Sentry no recibe:** confirmar DSN y release; los logs estructurados continúan
  siendo la evidencia primaria durante la recuperación.
