# Sprint 22 · Charter

## Objetivo

Crear la infraestructura pública de integración de Roustix para que cada
empresa pueda consultar y registrar información autorizada, y recibir eventos
de negocio de forma segura, versionada, auditable y aislada por tenant.

## Principios obligatorios

1. El tenant se obtiene de la credencial; nunca se confía en `empresa_id` del cliente.
2. Toda credencial tiene alcance mínimo, propietario, expiración y revocación.
3. Un recurso de otra empresa responde `404`, sin revelar su existencia.
4. Los eventos se confirman en base de datos antes de intentar entregarlos.
5. Las escrituras reintentables aceptan una clave de idempotencia.
6. Los límites dependen de derechos técnicos configurables, no de condicionales por nombre de plan.
7. UTC e ISO 8601 son obligatorios en el contrato; la UI convierte a la zona del tenant.
8. Ningún secreto, token, contraseña o firma se registra en logs.

## Alcance Sprint 22

- credenciales de integración por empresa;
- scopes y autorización por módulo;
- API v1 para activos, incidencias, OT, medidores y lecturas;
- endpoints administrativos para webhooks;
- catálogo inicial de eventos;
- firma HMAC, idempotencia, reintentos e historial de entregas;
- rate limiting y derechos por suscripción;
- OpenAPI, colecciones, pruebas de seguridad y documentación.

## Fuera de alcance

- OAuth 2.1, SSO o delegación entre empresas;
- GraphQL;
- marketplace de conectores;
- SDK publicados en registros públicos;
- entrega exactamente una vez;
- sincronización bidireccional específica para un ERP;
- WebSockets como transporte para integraciones externas.

## Decisiones de contrato

| Tema | Decisión |
|---|---|
| URL | `/api/v1`; cambios incompatibles requieren `/api/v2` |
| Usuario humano | JWT existente, de corta duración según política API |
| Servicio externo | API key `rtx_live_…` o `rtx_test_…`, mostrada una sola vez |
| Autorización | scopes + módulo activo + derecho del plan + tenant |
| Listas | `data` + `meta.pagination`, máximo 200 registros |
| Errores | envelope MAG con código estable y `request_id` |
| Escrituras | `Idempotency-Key` cuando crear duplicados sea riesgoso |
| Eventos | entrega al menos una vez; receptor idempotente por `event_id` |
| Firma | HMAC-SHA256 sobre timestamp y cuerpo crudo |
| Auditoría | creación, uso, revocación, entrega, reintento y acceso |

## Definition of Done de Sprint 22 completo

- [ ] La clave secreta solo se muestra al crear o rotar una credencial.
- [ ] Los secretos persisten únicamente mediante hash seguro.
- [ ] Cada endpoint valida tenant, scope, módulo, permiso y derecho técnico.
- [ ] Activos, incidencias, OT, medidores y lecturas cumplen el contrato v1.
- [ ] Los eventos se escriben mediante outbox transaccional.
- [ ] Webhooks incluyen firma, timestamp, idempotencia e historial.
- [ ] Existen reintentos y reenvío manual autorizados.
- [ ] Rate limits devuelven `429` y `Retry-After`.
- [ ] OpenAPI y colecciones coinciden con la implementación.
- [ ] Hay pruebas de tenant, scopes, revocación, SSRF, firma y duplicados.
