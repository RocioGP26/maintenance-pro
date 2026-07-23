# MAG-01-PHIL · Filosofía de la API

> La API de Roustix no es un acceso técnico al backend. Es la **forma oficial** de que sistemas externos operen con la plataforma.

---

## 1 · Contrato externo vs arquitectura interna

| Pieza | Audiencia | Pregunta que responde |
|-------|-----------|----------------------|
| **MAG** (esta guía) | Integradores · partners · desarrolladores | ¿Cómo me conecto de forma correcta? |
| **OpenAPI / MSD** | Mismos | ¿Qué herramientas y especificación uso? |
| Arquitectura de plataforma | Equipo Roustix | ¿Cómo está construido? *(no forma parte del contrato público)* |

MAG define el **contrato público** de integración.

---

## 2 · Principios MAG

| # | Principio |
|---|-----------|
| 1 | **REST predecible** — recursos, verbos HTTP estándar, JSON |
| 2 | **Tenant-first** — toda operación ocurre en contexto de empresa |
| 3 | **Segura por defecto** — JWT, roles, límites, sin datos cruzados |
| 4 | **Versionada** — `/api/v1` estable; cambios breaking → v2 |
| 5 | **Honesta** — errores claros, códigos HTTP correctos |
| 6 | **Documentada aquí** — si no está en MAG, no es contrato oficial |

---

## 3 · Qué no es la API

| ❌ No es | ✅ Es |
|---------|------|
| Scraping de HTML de la app | Contrato JSON estable |
| Acceso directo a BD | Capa de aplicación con reglas de negocio |
| Pantalla custom por cliente | Integración reutilizable |
| Referencia de endpoints suelta | Guía completa: auth, tenant, errores, webhooks |

---

## 4 · Casos de uso

- ERP / contabilidad sincronizando activos y órdenes
- Dashboard externo (Power BI, Looker)
- Automatización interna del cliente (scripts, n8n)
- Partners que extienden Roustix sin fork del código
- Webhooks para alertas operativas en tiempo real

---

## 5 · Estado actual vs contrato objetivo

| Aspecto | Hoy (código) | Contrato MAG v1 |
|---------|--------------|-----------------|
| Base URL | `/api/...` | `/api/v1/...` |
| Activos | `GET /api/activos` | `GET /api/v1/maintenance/assets` |
| Auth | `POST /api/auth/login` | `POST /api/v1/auth/login` |
| Webhooks | Diseño | Especificado en MAG-08 |

La migración a `/api/v1` es **evolutiva** — MAG define el destino; el código converge hacia él.

---

→ [MAG-02-AUTH · Autenticación](02-autenticacion-jwt.md) · [OpenAPI](/api/v1/openapi.yaml) · [MSD](/msd/)
