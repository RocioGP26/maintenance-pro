# Roadmap · Sprint 22

## 22.0 · Diseño y contrato — finalizado

- charter y arquitectura;
- convivencia JWT/API key;
- recursos y scopes iniciales;
- catálogo de eventos;
- firma, idempotencia, reintentos y SSRF;
- derechos técnicos desacoplados del nombre comercial del plan.

## 22.1 · Credenciales de integración — finalizado

- modelo y migración de API keys;
- creación, listado, rotación y revocación;
- hash, prefijo, expiración y último uso;
- middleware unificado JWT/API key;
- scopes, auditoría y pruebas tenant-safe.

## 22.2 · API pública Maintenance — finalizado

- envelopes y errores normalizados;
- activos, OT, incidencias, medidores y lecturas;
- `X-Request-Id`, paginación y filtros incrementales;
- rate limit por identidad;
- creación idempotente de incidencias y lecturas;
- notificaciones por área; integración con automatizaciones y Asset Health;
- migración `qy5n1p37u60f`; OpenAPI y colecciones Postman/Insomnia;
- pruebas de contrato.

## 22.3 · Webhooks — finalizado

- endpoints y suscripciones;
- outbox transaccional;
- worker de entregas y leases;
- HMAC, validación SSRF, reintentos e historial;
- eventos: incidencia creada/estado; OT creada/asignada/completada/cerrada;
  lectura fuera de rango; cambio de Asset Health.

## 22.4 · Seguridad y observabilidad — finalizado

- firma HMAC verificable y ventana temporal;
- límites de solicitudes / credenciales / endpoints por entitlement;
- registro de entregas, stats y retención;
- reintentos y desactivación automática auditada;
- protección de datos por tenant.

## 22.5 · Documentación y cierre — finalizado

- documentación para integradores;
- ejemplos curl/Python y receptor HMAC;
- colección de pruebas Postman Sprint 22;
- auditoría de credenciales y webhooks;
- pruebas de aislamiento entre empresas.

## Dependencias desbloqueadas

- conectores ERP y Power BI;
- Zapier, Make, n8n y Power Automate;
- SDK oficiales;
- derechos y límites técnicos por plan;
- automatizaciones externas sin acceso directo a la base de datos.
