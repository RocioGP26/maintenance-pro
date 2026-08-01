# Sprint 23.4 · Certificación de outbox cifrada

## Alcance implementado

- Los correos de verificación, bienvenida y recuperación se escriben en
  `email_outbox` y ya no esperan la respuesta de SMTP dentro de la petición.
- Destinatario, asunto y cuerpos de texto/HTML se cifran y autentican con
  Fernet antes de persistirse.
- La idempotencia se aplica por empresa y clave de negocio.
- El worker reclama lotes con `FOR UPDATE SKIP LOCKED` en PostgreSQL, usa un
  arrendamiento recuperable y reintenta a 1, 5 y 15 minutos, 1 y 4 horas.
- Los errores persistidos sólo contienen el tipo saneado; nunca incluyen
  contraseñas SMTP, tokens, códigos ni contenido del proveedor.
- Las filas terminales se eliminan en el mantenimiento periódico después de
  `EMAIL_OUTBOX_RETENTION_DAYS` (30 días por defecto).
- `sent_at` de verificaciones y recuperaciones sólo se registra después de una
  entrega aceptada por SMTP.
- Las notificaciones internas (campana) permanecen en la transacción de
  negocio porque no realizan I/O externo y deben aparecer atómicamente. Las
  entregas externas se procesan mediante el worker.

## Variables

Configurar el mismo valor en `mantis-app` y `roustix-worker`:

- `OUTBOX_ENCRYPTION_KEY`: aleatoria, de mínimo 32 caracteres.

El sistema puede derivar temporalmente una clave separada desde `SECRET_KEY`,
pero la clave dedicada evita acoplar el descifrado a una futura rotación de la
sesión. Al adoptar por primera vez la clave dedicada, el worker mantiene lectura
de sobres pendientes creados con la derivación anterior.

Variables opcionales:

- `WORKER_EMAIL_BATCH_SIZE=50`
- `EMAIL_OUTBOX_MAX_ATTEMPTS=5`
- `EMAIL_OUTBOX_LEASE_SECONDS=60`
- `EMAIL_OUTBOX_RETENTION_DAYS=30`

## Evidencia local

| Control | Resultado |
| --- | --- |
| Pruebas focalizadas | ✅ 35 aprobadas |
| Cifrado sin código ni destinatario en claro | ✅ |
| Idempotencia aislada por empresa | ✅ |
| Reintento y error saneado | ✅ |
| Rechazo de sobre alterado | ✅ |
| Regresión de verificación y recuperación | ✅ |
| Alembic | ✅ una sola cabeza: `rt9u4v06w18y_email_outbox` |

## Gate de producción

1. Definir `OUTBOX_ENCRYPTION_KEY` primero en el worker, esperar que vuelva a
   estar saludable y después definir exactamente el mismo valor en la web.
2. Desplegar primero la web (la migración crea `email_outbox`) y después el
   worker.
3. Solicitar un código de verificación y una recuperación de contraseña.
4. Confirmar que la petición responde sin depender de la latencia SMTP.
5. Confirmar en PostgreSQL que las filas pasan de `pending` a `sent`, sin
   buscar ni imprimir `payload_sealed`.
6. Confirmar la recepción de ambos mensajes y que `sent_at` queda informado.
7. Repetir una clave de negocio en un ensayo controlado y comprobar que no se
   crea ni entrega un duplicado.
8. Interrumpir SMTP en un entorno de ensayo, nunca en producción, y comprobar
   reintento, alerta operativa y recuperación posterior.
9. Registrar fecha, responsable, commit, versión y capturas en este documento.

El ensayo de idempotencia se ejecuta desde la Shell del servicio web de Render.
El primer comando crea un solo sobre aunque el servicio sea invocado dos veces:

```powershell
flask --app run:app email-outbox certify-idempotency `
  --empresa-slug EMPRESA_PILOTO `
  --user-email CORREO_RECEPTOR `
  --run-id pilot-AAAAMMDD
```

El resultado aprobado muestra `approved: true`, `same_id: true` y
`row_count: 1`. Después de que actúe el worker, repetir exactamente el mismo
comando y comprobar además `status: sent`, `sent: true` y que `row_count`
continúa en `1`. La salida no imprime destinatario, asunto ni contenido cifrado.

## Evidencia remota

| Campo | Resultado |
| --- | --- |
| Fecha Colombia | 2026-07-30; hora exacta no registrada |
| Responsable | Gladis Rocio Gelves Pabon |
| Commit / versión | `805d14a` / `1.0.37` |
| Verificación entregada | Pendiente de comprobar con un código nuevo de onboarding |
| Recuperación entregada | ✅ Correo recibido, contraseña cambiada y nueva clave aceptada |
| Uso único y sesiones | ✅ Enlace reutilizado rechazado y sesión anterior revocada |
| Idempotencia | ✅ Automatizada por empresa; ensayo remoto específico pendiente |
| Reintento controlado | ✅ El correo pendiente se conservó y entregó tras corregir la configuración SMTP |
| Health y worker | ✅ `/health/ready` en `ok`; heartbeat estable |
| Veredicto | Recuperación aprobada; cierre total pendiente de verificación e idempotencia remotas |

### Incidencias observadas y correcciones

- Una configuración inválida de `MAIL_SERVER` produjo un error IDNA en el
  worker. Desde `1.0.35` el fallo se convierte en reintento controlado y no
  interrumpe el ciclo completo.
- La reutilización del enlace desde una sesión autenticada redirigía al
  dashboard. Las versiones `1.0.36` y `1.0.37` garantizan rechazo visible del
  token consumido y permiten solicitar un enlace nuevo sin abandonar el flujo.
- El dashboard registró una latencia cercana a 9 segundos y bloqueó
  temporalmente el health check. `1.0.36` habilitó concurrencia `gthread` para
  mantener las sondas operativas mientras se atienden peticiones lentas.
