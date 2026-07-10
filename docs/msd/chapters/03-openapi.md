# MSD-03-OAPI · OpenAPI 3.1

**Código:** MSD-03-OAPI · Sprint 9.3 · **Entregado**

> Una única especificación. Todo el ecosistema.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir **OpenAPI 3.1** como la fuente oficial del contrato técnico de Maintix.

Toda la documentación interactiva, los SDK oficiales, el CLI, las colecciones Postman, el API Explorer y futuras herramientas se **generan a partir de esta especificación**.

| Audiencia | Documento |
|-----------|-----------|
| Personas | **MAG** — describe la API |
| Herramientas | **OpenAPI** — describe exactamente la misma API |

→ [MSD-02 · Developer Portal](02-developer-portal.md)

---

## 1 · Filosofía

OpenAPI **no es documentación adicional**.

Es la **representación machine-readable** del contrato MAG.

- Toda herramienta debe consumir OpenAPI.
- **Nunca** redefinir endpoints manualmente en SDK, Explorer o colecciones.

---

## 2 · Fuente única de verdad

```
MAG
      │
      ▼
OpenAPI 3.1
      │
 ┌────┼────┬─────┬─────┐
 ▼    ▼    ▼     ▼     ▼
SDK Explorer CLI Postman Docs
```

| Regla | Descripción |
|-------|-------------|
| MAG → OpenAPI | MAG define el contrato; OpenAPI lo codifica |
| OpenAPI → herramientas | SDK, Explorer, CLI y Postman se generan |
| Sin bifurcación | Una sola especificación por versión API |

---

## 3 · Ubicación

| Artefacto | Ruta |
|-----------|------|
| **Repositorio** | `docs/api/openapi.v1.yaml` |
| **Runtime JSON** | `GET /api/v1/openapi.json` |
| **Runtime YAML** | `GET /api/v1/openapi.yaml` |
| **Portal** | `/msd/openapi` → especificación en vivo |

```powershell
python run.py
curl http://127.0.0.1:5000/api/v1/openapi.json
```

---

## 4 · Versión

```yaml
openapi: 3.1.0
info:
  title: Maintix API
  version: 1.0.0
```

| Campo | Significado |
|-------|-------------|
| `openapi` | Versión del formato OpenAPI (3.1.0) |
| `info.version` | Versión del contrato API (alineada a MAG v1.0) |

---

## 5 · Organización

Estructura de `openapi.v1.yaml`:

```
openapi.v1.yaml
├── info
├── servers
├── security
├── tags
├── paths
└── components
    ├── schemas
    ├── responses
    ├── parameters
    └── securitySchemes
```

Cada sección tiene responsabilidad única — sin duplicar definiciones fuera de `components/`.

---

## 6 · Relación con MAG

Cada capítulo MAG alimenta una parte de OpenAPI.

| MAG | OpenAPI |
|-----|---------|
| [MAG-02 · JWT](/mag/chapters/02-autenticacion-jwt.md) | `securitySchemes` · `/auth/login` |
| [MAG-03 · Multi-tenant](/mag/chapters/03-multi-tenant.md) | Contexto tenant en schemas · `/me` |
| [MAG-04 · Recursos](/mag/chapters/04-recursos.md) | `paths` · tags por módulo |
| [MAG-05 · Convenciones](/mag/chapters/05-convenciones-nombres.md) | Naming · `snake_case` en schemas |
| [MAG-06 · Errores](/mag/chapters/06-manejo-errores.md) | `components/responses` · `ErrorResponse` |
| [MAG-07 · Versionado](/mag/chapters/07-versionado.md) | `info.version` · `openapi.v1.yaml` |
| [MAG-08 · Webhooks](/mag/chapters/08-webhooks.md) | Roadmap · callbacks |

**Regla:** si un endpoint existe en MAG-04, debe existir en OpenAPI antes de publicarse.

---

## 7 · Servidores

```yaml
servers:
  - url: https://api.maintix.app/api/v1
    description: Producción
  - url: http://127.0.0.1:5000/api/v1
    description: Desarrollo local
```

Los clientes y el API Explorer seleccionan servidor según entorno.

---

## 8 · Seguridad

JWT Bearer — referencia directa a [MAG-02](/mag/chapters/02-autenticacion-jwt.md).

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
```

Rutas públicas (login) declaran `security: []`.

---

## 9 · Tags

Tags oficiales alineados a módulos MAG-04:

| Tag | Módulo |
|-----|--------|
| **Authentication** | `auth` · `/me` |
| **Maintenance** | `maintenance/*` |
| **Inventory** | `inventory/*` |
| **Purchasing** | `purchasing/*` |
| **Sales** | `sales/*` |
| **CRM** | `crm/*` |
| **Admin** | `admin/*` |

Cada operación en `paths` usa exactamente un tag principal.

---

## 10 · Schemas

Todos los modelos públicos viven en `components/schemas`.

| Schema | Descripción |
|--------|-------------|
| **Asset** | Activo de mantenimiento |
| **WorkOrder** | Orden de trabajo |
| **Product** | Producto de inventario |
| **User** | Usuario |
| **ErrorResponse** | Formato error MAG-06 |
| **Pagination** | `meta.pagination` |

Ejemplo — `Asset`:

```yaml
Asset:
  type: object
  properties:
    asset_id:
      type: integer
    asset_code:
      type: string
    name:
      type: string
    status:
      type: string
      enum: [operational, maintenance, inactive]
    critical:
      type: boolean
```

Recursos planificados pueden incluir `x-mag-status: planned` hasta implementación en código.

---

## 11 · Responses

Respuestas reutilizables en `components/responses` — alineadas con [MAG-06](/mag/chapters/06-manejo-errores.md):

| Response | HTTP | Código ejemplo |
|----------|------|----------------|
| **Unauthorized** | 401 | `UNAUTHORIZED` |
| **Forbidden** | 403 | `FORBIDDEN` |
| **NotFound** | 404 | `RESOURCE_NOT_FOUND` |
| **ValidationError** | 422 | `VALIDATION_ERROR` |
| **RateLimitExceeded** | 429 | `RATE_LIMIT_EXCEEDED` |
| **InternalError** | 500 | `INTERNAL_ERROR` |

Todas referencian el schema `ErrorResponse`.

---

## 12 · Generación

OpenAPI genera automáticamente:

| Artefacto | Capítulo MSD |
|-----------|--------------|
| SDK Python | [MSD-04](04-sdk-oficiales.md) |
| SDK JavaScript | MSD-04 |
| SDK PHP | MSD-04 |
| API Explorer | [MSD-06](06-sandbox-explorer.md) |
| Postman | [MSD-08](08-colecciones.md) |
| Insomnia | MSD-08 |

**Herramientas previstas:** OpenAPI Generator · Speakeasy · `openapi-typescript`

---

## 13 · Validación

Pipeline CI (objetivo MSD v1.0):

```
OpenAPI
   │
   ▼
Spectral        ← reglas MAG-05 / MAG-06
   │
   ▼
Prism           ← mock / contract tests
   │
   ▼
CI
   │
   ▼
Deploy
```

El contrato **siempre** debe validar antes del despliegue.

| Herramienta | Rol |
|-------------|-----|
| **Spectral** | Lint del YAML · naming · responses |
| **Prism** | Mock server · contract testing |

> **Estado:** pipeline documentado · CI en roadmap MSD v1.0.

---

## 14 · Compatibilidad

OpenAPI sigue exactamente [MAG-07](/mag/chapters/07-versionado.md):

```
openapi.v1.yaml  →  API v1
openapi.v2.yaml  →  API v2   (futuro)
```

**Nunca mezclar versiones** en un mismo archivo.

| Cambio | Acción |
|--------|--------|
| Compatible en v1 | Patch `info.version` · mismo `openapi.v1.yaml` |
| Breaking | Nuevo archivo `openapi.v2.yaml` |

---

## 15 · Roadmap OpenAPI

| Capacidad | Estado |
|-----------|--------|
| Webhooks en spec | 📋 MAG-08 · callbacks OpenAPI 3.1 |
| **Callbacks** | 📋 Eventos outbound |
| **AsyncAPI** | Roadmap · eventos asíncronos |
| **GraphQL Gateway** | Evaluación |

---

## 16 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Nunca editar la documentación HTML de referencia directamente |
| 2 | **OpenAPI es la fuente oficial** para herramientas |
| 3 | MAG explica; OpenAPI describe |
| 4 | Todo SDK proviene de OpenAPI |
| 5 | Todo endpoint debe existir en OpenAPI **antes** de publicarse |
| 6 | Reutilizar `components/responses` — no duplicar errores |
| 7 | Mantener `openapi.v1.yaml` sincronizado con MAG-04 |

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MAG-02 · JWT](/mag/chapters/02-autenticacion-jwt.md) | Seguridad |
| [MAG-04 · Recursos](/mag/chapters/04-recursos.md) | Catálogo de paths |
| [MAG-06 · Errores](/mag/chapters/06-manejo-errores.md) | Responses |
| [MAG-07 · Versionado](/mag/chapters/07-versionado.md) | Evolución v1/v2 |
| [MSD-02 · Portal](02-developer-portal.md) | Consume OpenAPI en UI |
| [MSD-04 · SDK](04-sdk-oficiales.md) | Generado desde OpenAPI |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] `openapi.v1.yaml` publicado con estructura MAG (schemas · responses · paths core)
- [x] `/api/v1/openapi.json` disponible
- [x] `/api/v1/openapi.yaml` disponible
- [x] Portal expone spec vía `/msd/openapi`
- [ ] Validación automática en CI (Spectral · Prism)
- [ ] Referencia interactiva en Portal alimentada por OpenAPI
- [ ] SDK generado desde OpenAPI
- [ ] Colecciones Postman generadas automáticamente

**Documentación y runtime básico:** ✅ · **Generación y CI:** 🟡 roadmap MSD v1.0

---

## Filosofía del capítulo

OpenAPI convierte el contrato de Maintix en un **estándar consumible por personas y herramientas**. Es la fuente única de verdad sobre la API y el **punto de partida de todo el ecosistema de desarrollo**.

Así como [MAG-04](/mag/chapters/04-recursos.md) fue el documento central del Sprint 8, **MSD-03 es el documento central del Sprint 9**.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato** | 🟡 En construcción (paths core + catálogo MAG) |
| **Especificación** | OpenAPI 3.1 |
| **Fuente** | MAG v1.0 |
| **Consumidores** | Portal · SDK · CLI · Explorer |
| **Siguiente capítulo** | [MSD-05 · CLI](05-cli.md) |

---

→ [MSD-04-SDK · SDK oficiales](04-sdk-oficiales.md)
