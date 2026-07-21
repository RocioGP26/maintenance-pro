# MAG Changelog

## [1.0.12] — 2026-07-10 · MAG-10 Límites · MAG v1.0 completo

### Added
- **MAG-10-LIM** completo — filosofía uso responsable · rate limiting · timeouts
- Reintentos y backoff · paginación · caché · seguridad · diseño de clientes
- Observabilidad · compatibilidad · integraciones recomendadas · checklist
- Roadmap MSD Sprint 9 · índice MAG v1.0 · cierre Sprint 8

### Changed
- Sprint 8 (MAG v1.0) marcado como **100% completado**

---

## [1.0.11] — 2026-07-10 · MAG-09 Ejemplos y SDK

### Added
- **MAG-09-EX** completo — filosofía ejemplos ejecutables · entorno dev/prod
- Login cURL · Python · JavaScript · consulta y CRUD de recursos
- Manejo de errores `error.code` · buenas prácticas · roadmap SDK
- Estructura SDK alineada MAG-04 · generación desde OpenAPI
- Notas legacy (`/api/auth/login`, `/api/activos`) vs contrato `/api/v1`
- Exit Criteria · enlace suite SDK

---

## [1.0.10] — 2026-07-10 · MAG-08 Webhooks

### Added
- **MAG-08-HOOK** completo — arquitectura · registro · catálogo eventos
- Payload estándar · HMAC · reintentos · `X-Event-Id` · versionado
- Auditoría · roadmap · Exit Criteria
- NOMENCLATURE: catálogo eventos Maintenance/Inventory/Platform

---

## [1.0.9] — 2026-07-10 · MAG-07 versionado

### Added
- **MAG-07-VER** completo — URL `/api/v1` · compatibilidad vs breaking
- Legacy table · Deprecation/Sunset headers · política soporte
- OpenAPI por versión · evolución contrato · Exit Criteria

---

## [1.0.8] — 2026-07-10 · MAG-06 errores (contrato)

### Added
- **MAG-06-ERR** completo — formato `error` · catálogo oficial por categoría
- HTTP 200–503 · validación `details` · cross-tenant 404
- Errores internos · `X-Request-Id` · auditoría · Exit Criteria
- NOMENCLATURE: catálogo centralizado MAG-06

---

## [1.0.7] — 2026-07-10 · MAG-05 style guide oficial

### Added
- **MAG-05-NAM** completo — guía de estilo API (15 secciones)
- Idioma oficial · recursos · methods · JSON snake_case inglés
- Códigos error UPPER_SNAKE_CASE · códigos suite MAG/MPA/MCM
- Ejemplos correcto/incorrecto · Exit Criteria · posición style guide
- MAG-06–10 deben referenciar MAG-05 sin duplicar reglas

---

## [1.0.6] — 2026-07-10 · MAG-04 consistencia REST internacional

### Changed
- Methods HTTP sin traducir (`GET`, `POST`, …) · recursos 100% inglés
- Envelope estándar `data` + `meta` + `links` · `included` · `meta.pagination`
- Tabla **Contrato v1 | Estado implementación**
- Regla sustantivo + method · recursos hijos (max 2 niveles) · idempotencia
- Filosofía atemporal · MAG fuente oficial OpenAPI/SDK
- MAG-05: claves JSON envelope en inglés

---

## [1.0.5] — 2026-07-10 · MAG-04 Recursos REST (contrato central)

### Added
- **MAG-04-RES** completo — árbol `/api/v1` por módulos
- Filosofía recursos de negocio · CRUD · relaciones · paginación `data`+`pagination`
- Filtros · `?include=` · roadmap módulos · flujo petición completo
- Exit Criteria · posición como corazón de MAG y SDK
- Árbol oficial: `maintenance/assets`, `inventory/products`, etc.

### Changed
- Rutas v1 con namespace de módulo (antes `/api/v1/assets` plano)
- MAG-05 enlazado como extensión de MAG-04 · tabla legacy actualizada

---

## [1.0.4] — 2026-07-10 · MAG-03 revisión MPA/terminología

### Changed
- Terminología **Tenant (Empresa)** alineada con MPA-03
- Ciclo interno Flask: `tenant_required` → JWT → `g.*` → `require_module` → `rol_required`
- Cadena Tenant → Plan → Módulos → Permisos → Acción
- SQL equivalente de `query_tenant(Machine)`
- 404: rationale anti-enumeración · **Regla de Oro** · Errores comunes
- Filosofía: aislamiento como principio de plataforma (MPA)

---

## [1.0.3] — 2026-07-10 · MAG-03 entregado

### Added
- **MAG-03-TNT** completo — tenant, aislamiento, flujo, 404 vs 403
- Multi-sede vs tenant · superadmin · dos niveles de permisos
- Arquitectura datos `empresa_id` · tabla implementación actual
- Exit Criteria · filosofía · estado del capítulo
- Enlaces MPA-03 · MPA-04 · MAG-02 · MAG-04 · MAG-06

---

## [1.0.2] — 2026-07-10 · MAG-02 madurez SaaS

### Added
- Exit Criteria · tabla parámetros firma (HS256, SECRET_KEY, clock skew)
- Contrato reservado `POST /api/v1/auth/refresh` (MAG v2.0)
- Error estándar auth · enlace MAG-06
- Claims reservados · bloque Estado del capítulo

---

## [1.0.1] — 2026-07-10 · MAG-02 entregado

### Changed
- **MAG-02-AUTH** refinado — flujo completo, respuesta anidada `user`/`empresa`, `expires_in`
- Claims JWT: `plan`, `modules` documentados (implementación pendiente)
- Logout `POST /api/v1/auth/logout` · Refresh Token → MAG v2.0
- Seguridad post-auth: plan, módulo, rol, tenant
- Enlaces MPA-04 · MPA-07 · MAG-03

---

## [1.0.0] — 2026-07-10 · Sprint 8 completo

### Added
- **MAG v1.0** — Roustix API Guide (10 capítulos)
- Catálogo HTML `/mag/`
- Códigos MAG-01-PHIL … MAG-10-LIM
- Contrato `/api/v1` · migración desde rutas legacy documentada
- JWT · multi-tenant · recursos · errores · webhooks · ejemplos
- Relación explícita MPA (interno) ↔ MAG (externo)

### Capítulos
- MAG-01 · Filosofía de la API
- MAG-02 · Autenticación JWT
- MAG-03 · Multi-tenant
- MAG-04 · Recursos
- MAG-05 · Convenciones de nombres
- MAG-06 · Manejo de errores
- MAG-07 · Versionado
- MAG-08 · Webhooks
- MAG-09 · Ejemplos y SDK
- MAG-10 · Límites y buenas prácticas

### Implementación pendiente
- Rutas `/api/v1/*` en código
- OpenAPI spec
- Webhooks
- Recursos work-orders · inventory
