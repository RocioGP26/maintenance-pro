# Sprint 23.4 · Observabilidad, workers y operación

## Objetivo

Hacer observable y operable Roustix bajo carga real, detectar degradaciones antes
de que las reporte un cliente y desacoplar el trabajo asíncrono de las peticiones
HTTP, sin ampliar funcionalidades de negocio.

## Alcance

### 1. Observabilidad

- Logs JSON estructurados y libres de secretos.
- ID de correlación para todas las peticiones y respuestas.
- Captura centralizada de excepciones con contexto de versión y entorno.
- Métricas de latencia, volumen, errores y disponibilidad.
- Health checks separados para liveness, readiness y dependencias externas.

### 2. Alertas operativas

- Aplicación no disponible o readiness degradado.
- Base de datos no disponible o lenta.
- Backup fallido.
- Errores repetidos de SMTP, almacenamiento S3/R2 y webhooks.
- Notificación al correo de soporte con deduplicación y ventana de silencio.

### 3. Workers

- Entrega confiable de webhooks mediante cola.
- Mantenimientos programados fuera del proceso web.
- Notificaciones y correo transaccional pendientes.
- Reintentos con backoff, idempotencia y registro de resultado.

### 4. Rate limiting distribuido

- Redis/Render Key Value como almacenamiento compartido.
- Límites diferenciados para login, recuperación, API y plataforma.
- Fail-safe documentado si Redis no está disponible.

### 5. Operación

- Runbooks de aplicación caída, base degradada, SMTP, R2 y workers.
- Prueba de carga reproducible con umbrales de aceptación.
- Política de escalamiento, recuperación, responsables y severidades.

## Secuencia

1. Correlación, logging HTTP, captura de excepciones y health checks.
2. Métricas y alertas de disponibilidad/dependencias.
3. Redis compartido y rate limiting distribuido.
4. Cola y workers idempotentes.
5. Pruebas de carga, runbooks y simulacro operativo.

## Gate de infraestructura

`mantis-app` no puede recibir clientes reales en un plan que se suspenda por
inactividad. Antes del piloto debe verificarse en Render una instancia web de
pago, siempre activa, con capacidad y escalamiento definidos. El archivo
`render.yaml` debe describir el mismo plan aplicado realmente en el dashboard.

## Definition of Done

- [x] Toda respuesta incluye un ID de correlación y los errores lo conservan.
- [x] Excepciones no controladas llegan al capturador central sin datos sensibles.
- [x] Existen métricas y alertas probadas para disponibilidad, DB y dependencias.
- [x] Los límites críticos usan almacenamiento distribuido.
- [x] Webhooks y correos salen de workers con reintentos e idempotencia.
- [x] Los runbooks y la prueba de carga están versionados.
- [x] La instancia de Render de pago fue verificada y quedó registrada.
