# Sprint 22.0 · Diseño y contrato

**Estado:** Finalizado ✅

**Fecha:** 2026-07-21

**Naturaleza:** documental; sin nuevas funcionalidades públicas

## Resultado

Se formalizó la evolución de la API tenant existente hacia una API pública con
credenciales dedicadas y webhooks confiables. El diseño conserva MAG v1,
separa usuarios de integraciones y establece controles antes de exponer nuevas
operaciones.

## Decisiones cerradas

- JWT continúa para identidad humana; API keys se usan para servicios.
- Las keys son tenant-bound, con scopes, hash, expiración y revocación.
- La autorización combina empresa, suscripción, módulo, entitlement y scope.
- La primera API pública se concentra en Maintenance.
- Escrituras sensibles requieren idempotencia.
- Webhooks usan outbox, HMAC-SHA256 y entrega al menos una vez.
- La validación de URL protege contra SSRF.
- Los límites se expresan como entitlements configurables.
- OpenAPI describe implementación real, no promesas todavía no desarrolladas.

## Entregables

- [x] charter;
- [x] arquitectura lógica y modelo conceptual;
- [x] contrato REST v1 y matriz de recursos;
- [x] autenticación, scopes y ciclo de vida de credenciales;
- [x] contrato de webhooks y catálogo inicial;
- [x] estrategia de planes y límites técnicos;
- [x] roadmap 22.1–22.5;
- [x] referencias MAG/MPA y changelog documental.

## Riesgos controlados por diseño

| Riesgo | Control acordado |
|---|---|
| fuga entre empresas | tenant derivado de credencial + consultas tenant-safe |
| key filtrada | secreto único, hash, expiración, rotación y revocación |
| webhook falso/repetido | HMAC, timestamp y event ID |
| SSRF | HTTPS, bloqueo de redes internas y validación DNS |
| evento perdido | outbox transaccional |
| duplicados | idempotencia REST y webhook |
| abuso de API | rate limits por tenant y credencial |
| reglas comerciales rígidas | entitlements separados de nombres de plan |

## Próximo paso

**Sprint 22.1 · Credenciales de integración.** Antes de exponer más recursos se
implementará la identidad técnica, porque todos los endpoints y webhooks
dependen de ella.
