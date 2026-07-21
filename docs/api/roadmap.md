# Roadmap · Sprint 22

## 22.0 · Diseño y contrato — finalizado

- charter y arquitectura;
- convivencia JWT/API key;
- recursos y scopes iniciales;
- catálogo de eventos;
- firma, idempotencia, reintentos y SSRF;
- derechos técnicos desacoplados del nombre comercial del plan.

## 22.1 · Credenciales de integración

- modelo y migración de API keys;
- creación, listado, rotación y revocación;
- hash, prefijo, expiración y último uso;
- middleware unificado JWT/API key;
- scopes, auditoría y pruebas tenant-safe.

## 22.2 · API pública Maintenance

- convergencia de envelopes y errores;
- activos y OT con filtros incrementales;
- incidencias de lectura y creación;
- medidores y registro idempotente de lecturas;
- rate limit general y actualización de OpenAPI/colecciones.

## 22.3 · Webhooks

- endpoints y suscripciones;
- outbox transaccional;
- worker de entregas y leases;
- HMAC, validación SSRF, reintentos e historial;
- eventos iniciales de Maintenance y Asset Health.

## 22.4 · Derechos técnicos y observabilidad

- entitlements por catálogo/tenant;
- límites de credenciales, solicitudes, endpoints y retención;
- métricas, alertas, dashboard administrativo y reenvío manual;
- matriz comercial aprobada para Trial, Start, Scale y Enterprise.

## 22.5 · Integración y cierre

- OpenAPI como contrato verificable;
- Postman/Insomnia actualizados;
- pruebas de carga y seguridad;
- runbook operativo y recuperación;
- alineación MAG, MPA, MSD, SDK y release.

## Dependencias desbloqueadas

- conectores ERP y Power BI;
- Zapier, Make, n8n y Power Automate;
- SDK oficiales;
- derechos y límites técnicos por plan;
- automatizaciones externas sin acceso directo a la base de datos.
