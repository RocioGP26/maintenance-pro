# Sprint 23.4 · Runbook de Redis y worker

## Arquitectura

- El servicio web usa Render Key Value como almacenamiento compartido de
  Flask-Limiter.
- `roustix-worker` procesa la outbox PostgreSQL de webhooks y las tareas de
  mantenimiento periódico.
- PostgreSQL conserva estados, intentos y leases de webhooks. Redis coordina el
  lock de mantenimiento y publica el heartbeat del worker.
- Desarrollo y pruebas pueden usar `memory://`; producción rechaza ese fallback.

## Configuración de Render

1. Crear o sincronizar `roustix-keyvalue` en plan de pago.
2. Verificar que web y worker reciben su `connectionString` como `REDIS_URL`.
3. Copiar al worker la misma `SECRET_KEY` del servicio web. Si son diferentes,
   el worker no podrá abrir los secretos HMAC de endpoints existentes.
4. Configurar `DATABASE_URL`, Sentry y SMTP en el worker.
5. Desplegar `roustix-worker` y comprobar el heartbeat antes de habilitar
   `WORKER_HEARTBEAT_REQUIRED=true` en la web.

## Verificación

1. `GET /health/ready` debe devolver:
   - `checks.redis.ok: true`;
   - `checks.worker.ok: true`;
   - latencias inferiores a sus umbrales.
2. Enviar un webhook de prueba y confirmar transición
   `pending → processing → delivered`.
3. Confirmar en logs el evento `worker_cycle_completed`.
4. Ejecutar dos workers temporalmente y verificar que una entrega solo se procesa
   una vez; PostgreSQL usa `FOR UPDATE SKIP LOCKED`.
5. Confirmar que login y API devuelven cabeceras de rate limit compartidas entre
   instancias web.

## Incidente: Redis no disponible

- Severidad: P1 si bloquea login/API o readiness; P2 si solo aumenta latencia.
- La web devuelve readiness `503` cuando Redis es obligatorio.
- No cambiar manualmente a `memory://` en producción: permitiría límites distintos
  por instancia y debilitaría login, recuperación y API.
- Revisar estado y memoria de Render Key Value, eventos de mantenimiento y red
  privada. Recuperar Redis y validar `/health/ready`.

## Incidente: heartbeat ausente

- La web permanece disponible pero readiness informa `status: degraded`.
- Revisar despliegue, reinicios, consumo de memoria y conexión PostgreSQL/Redis del
  worker.
- Reiniciar el worker si no hay un ciclo activo. Los leases vencidos de webhooks se
  recuperan automáticamente.
- Confirmar que el heartbeat reaparece dentro de 90 segundos y que baja la cola.

## Operación manual

```bash
# Procesar un lote puntual
flask --app run:app webhooks deliver --limit 50

# Ejecutar mantenimiento idempotente
flask --app run:app maintenance run

# Iniciar el worker continuo
python -m scripts.worker
```

## Alcance pendiente

Los correos de identidad continúan síncronos para no persistir códigos o tokens en
texto plano. El siguiente avance debe crear una outbox cifrada específica para
correo y notificaciones antes de mover esos mensajes al worker.
