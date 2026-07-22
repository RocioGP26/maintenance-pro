# Sprint 22.1 · Credenciales de integración

**Estado:** Finalizado ✅

**Fecha:** 2026-07-22

## Resultado

Roustix dispone de identidades técnicas independientes de los usuarios. Cada
API key queda ligada de forma inmutable a una empresa, funciona únicamente en
`/api/v1` y solo autoriza los scopes concedidos.

## Entregables

- [x] modelo `integration_credentials` y migración Alembic;
- [x] creación con secreto completo visible una sola vez;
- [x] persistencia exclusiva de hash `scrypt` y prefijo identificable;
- [x] ambientes `test` y `live`;
- [x] scopes validados contra catálogo cerrado;
- [x] expiración y actualización acotada de último uso;
- [x] rotación con ventana configurable de convivencia;
- [x] revocación inmediata;
- [x] administración web y endpoints administrativos;
- [x] middleware unificado JWT/API key;
- [x] auditoría por tenant;
- [x] pruebas de scopes, expiración, revocación y aislamiento tenant.

## Controles de seguridad

| Riesgo | Control implementado |
|---|---|
| secreto recuperable | solo se persiste hash `scrypt` |
| acceso cruzado | tenant derivado de la credencial, nunca del cliente |
| privilegio excesivo | catálogo cerrado y decoradores de scope |
| acceso a interfaz web | API keys limitadas estrictamente a `/api/v1` |
| credencial filtrada | revocación inmediata, expiración y rotación |
| administración remota | endpoints de gestión requieren sesión administrativa |

## Próximo paso

**Sprint 22.3 · Webhooks:** endpoints, suscripciones, outbox, firma HMAC y
reintentos.
