# MAG-04-RES · Recursos REST

**Código:** MAG-04-RES · Sprint 8.4 · **Entregado**

> La API no expone tablas.  
> Expone **recursos de negocio**.

**Toda la operación. Una sola plataforma.**

> **Política MAG:** La documentación se lee en español; el **contrato API** (URLs, métodos HTTP, claves JSON) es **siempre en inglés** — igual que Stripe, GitHub, Microsoft o Google.

---

## Objetivo del capítulo

Definir la **organización oficial** de los recursos REST de Roustix: nombres, operaciones CRUD, relaciones entre módulos y evolución del contrato `/api/v1`.

MAG-01 definió la filosofía. MAG-02 la autenticación. MAG-03 el aislamiento multi-tenant. **MAG-04 es el contrato central de la API.** Los capítulos MAG-05–10 y el SDK oficial se construyen sobre este documento.

---

## 1 · Filosofía de los recursos

La API representa **conceptos del negocio**, no la estructura interna de la base de datos.

| ❌ Prohibido | ✅ Correcto |
|-------------|------------|
| `/tbl_maquinas` | `/maintenance/assets` |
| `/getMachine` | `GET /maintenance/assets/{id}` |
| `/updateEquipo` | `PATCH /maintenance/assets/{id}` |
| `/closeWorkOrder` | `POST /work-orders/{id}/close` |

**Reglas:**

1. Cada endpoint representa un **recurso de negocio**, no una tabla SQL.
2. Un recurso siempre es un **sustantivo**. Las acciones pertenecen al **método HTTP**, nunca al nombre del endpoint.
3. Rutas y claves JSON del contrato → **inglés**. Explicación y mensajes de error humanos → español (`message`).

Un recurso REST representa una **capacidad del negocio**, no una implementación técnica. Cuando la arquitectura evoluciona, el contrato permanece estable para quienes integran con Roustix.

---

## 2 · Estructura general

```
/api/v1
│
├── auth
├── me
├── maintenance
│     ├── assets
│     ├── work-orders
│     ├── schedules
│     └── lubrications
│
├── inventory
│     ├── products
│     ├── stock
│     ├── movements
│     └── warehouses
│
├── purchasing
├── sales
├── crm
├── admin
└── platform
```

Cada rama es un **namespace en inglés** activable por tenant (MPA-03). Si el módulo no está activo → **403** `MODULE_NOT_ENABLED`.

---

## 3 · Recursos oficiales

| Recurso | Contrato v1 | Estado implementación |
|---------|-------------|------------------------|
| `/auth` | ✅ Definido | ✅ `POST /api/auth/login` |
| `/me` | ✅ Definido | ✅ `GET /api/me` |
| `/maintenance/assets` | 🟢 Estable | 🟢 GET legacy `/api/activos` |
| `/maintenance/work-orders` | 🟢 Estable | 📋 Pendiente |
| `/maintenance/schedules` | 🟡 Evolución | 📋 Pendiente |
| `/maintenance/lubrications` | 🟡 Evolución | 📋 Pendiente |
| `/inventory/products` | 🟢 Estable | 📋 Pendiente |
| `/inventory/stock` | 🟢 Estable | 📋 Pendiente |
| `/inventory/movements` | 🟢 Estable | 📋 Pendiente |
| `/inventory/warehouses` | 🟡 Evolución | 📋 Pendiente |
| `/purchasing/requests` | 🟢 Contrato estable | 📋 API pendiente · UI Sprint 16 ✅ |
| `/purchasing/orders` | 🟢 Contrato estable | 📋 API pendiente · UI Sprint 16 ✅ |
| `/purchasing/receipts` | 🟢 Contrato estable | 📋 API pendiente · UI Sprint 16 ✅ |
| `/purchasing/payables` | 🟢 Contrato estable | 📋 API pendiente · CxP Sprint 16 ✅ |
| `/sales/orders` | 📋 Planificado | 📋 Pendiente |
| `/crm/customers` | 📋 Planificado | 📋 Pendiente |
| `/admin/users` | 🟢 Estable | 📋 Pendiente |
| `/admin/summary` | 🟢 Estable | ✅ `GET /api/admin/resumen` |

**Leyenda contrato:** ✅ Definido · 🟢 Estable · 🟡 En evolución · 📋 Planificado

Rutas legacy sin prefijo `v1` — migración en [MAG-07](07-versionado.md).

---

## 4 · Operaciones REST

Todos los recursos siguen el **mismo patrón**. Los verbos HTTP **no se traducen**:

| Method | Path | Uso |
|--------|------|-----|
| **GET** | `/api/v1/{module}/{resource}` | Colección |
| **GET** | `/api/v1/{module}/{resource}/{id}` | Recurso único |
| **POST** | `/api/v1/{module}/{resource}` | Crear |
| **PUT** | `/api/v1/{module}/{resource}/{id}` | Reemplazar |
| **PATCH** | `/api/v1/{module}/{resource}/{id}` | Actualización parcial |
| **DELETE** | `/api/v1/{module}/{resource}/{id}` | Eliminar |

### Ejemplo · `maintenance/assets`

```http
GET    /api/v1/maintenance/assets
GET    /api/v1/maintenance/assets/25
POST   /api/v1/maintenance/assets
PUT    /api/v1/maintenance/assets/25
PATCH  /api/v1/maintenance/assets/25
DELETE /api/v1/maintenance/assets/25
```

Acciones de dominio → sub-recurso + **POST**: `POST /api/v1/maintenance/work-orders/42/close`

### Idempotencia

| Method | Idempotente |
|--------|-------------|
| **GET** | Sí |
| **PUT** | Sí |
| **DELETE** | Sí |
| **PATCH** | Depende de la operación |
| **POST** | No |

---

## 5 · Convenciones

Detalle → [MAG-05 · Convenciones de nombres](05-convenciones-nombres.md).

| Aspecto | Regla |
|---------|-------|
| URLs | Inglés · plural · kebab-case |
| Methods | `GET` · `POST` · `PUT` · `PATCH` · `DELETE` (sin traducir) |
| JSON envelope | `data` · `meta` · `links` · `included` · `pagination` |
| Field names | `snake_case` · inglés — ver [MAG-05](05-convenciones-nombres.md) |
| Fechas | ISO 8601 UTC |

---

## 6 · Relaciones entre recursos

### Maintenance

```
Asset
 │
 ├── work-orders
 ├── lubrications
 ├── attachments
 └── history
```

### Inventory

```
Product
 │
 ├── stock
 ├── movements
 ├── purchases
 └── sales
```

### Recursos hijos · cuándo usarlos

| ✅ Correcto | Profundidad |
|------------|-------------|
| `/maintenance/assets/{id}/history` | 2 niveles bajo módulo |
| `/maintenance/assets/{id}/work-orders` | 2 niveles |
| `/inventory/products/{id}/movements` | 2 niveles |

| ❌ Evitar | Motivo |
|----------|--------|
| `/assets/25/history/15/work-orders/2/details/...` | URLs demasiado profundas |
| `/getAssetHistory` | Verbo en URL |

**Regla:** máximo **2 segmentos** bajo el recurso padre (`{resource}/{id}/{child}`). Más allá → recurso de primer nivel + filtros o `?include=`.

Alternativa a anidamiento profundo:

```http
GET /api/v1/maintenance/assets/25?include=history,work_orders,attachments
```

---

## 7 · Paginación

```http
GET /api/v1/inventory/products?page=2&page_size=50
```

Envelope de lista (dentro del estándar §13):

```json
{
  "data": [],
  "meta": {
    "pagination": {
      "page": 2,
      "page_size": 50,
      "total": 438
    }
  },
  "links": {
    "self": "/api/v1/inventory/products?page=2&page_size=50",
    "next": "/api/v1/inventory/products?page=3&page_size=50",
    "prev": "/api/v1/inventory/products?page=1&page_size=50"
  }
}
```

| Query param | Default | Max |
|-------------|---------|-----|
| `page` | 1 | — |
| `page_size` | 50 | 200 |

**Legacy:** `{ "total": N, "items": [...] }` en `/api/activos` — convergencia al envelope MAG.

---

## 8 · Filtros

Nunca `empresa_id` en query (JWT, MAG-03).

```http
GET /api/v1/maintenance/assets?status=operativo
GET /api/v1/inventory/products?stock_low=true
GET /api/v1/maintenance/work-orders?assigned_to=18
GET /api/v1/maintenance/work-orders?from=2026-01-01&to=2026-01-31
```

Convención: `filter[field]=value` o parámetros cortos documentados por recurso (MAG-05).

---

## 9 · Inclusión de relaciones

```http
GET /api/v1/maintenance/assets/25?include=history,work_orders,attachments
```

```json
{
  "data": {
    "id": 25,
    "codigo": "M-025",
    "nombre": "Compresor B",
    "status": "operativo"
  },
  "included": {
    "history": [],
    "work_orders": [],
    "attachments": []
  }
}
```

Claves en **`included`**, nunca traducidas. Ideal para clientes móviles.

**Estado:** 📋 Planificado post-v1 lectura básica.

---

## 10 · Recursos futuros

```
maintenance ──► inventory
       │
       ▼
  purchasing ──► sales ──► crm
       │
       ▼
    finance ──► analytics ──► ai
```

Nuevos módulos = nuevas ramas bajo `/api/v1/{module}/` — sin romper contratos existentes.

→ [MPA-02 · Mapa de módulos](/mpa/chapters/02-mapa-modulos.md)

---

## 11 · Flujo de petición

```
GET /api/v1/maintenance/assets/25
        │
        ▼
   JWT (MAG-02)
        │
        ▼
   Tenant (MAG-03)
        │
        ▼
   Plan + module + permissions
        │
        ▼
   query_tenant(Machine).filter_by(id=25)
        │
        ▼
   JSON response envelope
        │
        ▼
   Logs + audit
```

Otro tenant → **404** `RESOURCE_NOT_FOUND` (MAG-06).

---

## 12 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Recursos y módulos en **inglés**, siempre en plural donde aplique |
| 2 | Methods HTTP originales — nunca traducir |
| 3 | Nunca exponer tablas/modelos internos (`machines`, `WorkOrder`) en URLs |
| 4 | IDs en path — no en body de lectura |
| 5 | Relaciones vía URL hijo (≤2 niveles) o `include` |
| 6 | Envelope `data` + `meta` + `links` en todas las respuestas exitosas |
| 7 | Versionar en `/v1` — no por recurso |

---

## 13 · Envelope de respuesta estándar

Contrato completo para toda respuesta **exitosa**:

```json
{
  "data": {},
  "meta": {},
  "links": {}
}
```

| Clave | Uso |
|-------|-----|
| **`data`** | Recurso único, colección o `null` |
| **`meta`** | `pagination`, `api_version`, `warnings`, `trace_id` |
| **`links`** | `self`, `next`, `prev`, recursos relacionados |

### Recurso único

```json
{
  "data": {
    "id": 25,
    "codigo": "M-025",
    "nombre": "Compresor B",
    "status": "operativo",
    "es_critico": true
  },
  "meta": {
    "api_version": "v1"
  },
  "links": {
    "self": "/api/v1/maintenance/assets/25"
  }
}
```

Errores → [MAG-06](06-manejo-errores.md) · Versionado → [MAG-07](07-versionado.md) · Webhooks → [MAG-08](08-webhooks.md) · Ejemplos → [MAG-09](09-ejemplos.md).

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MAG-02 · Auth JWT](02-autenticacion-jwt.md) | Token en cada petición |
| [MAG-03 · Multi-tenant](03-multi-tenant.md) | Filtrado por tenant |
| [MAG-05 · Convenciones](05-convenciones-nombres.md) | Naming detallado |
| [MAG-06 · Errores](06-manejo-errores.md) | Formato `error.code` |
| [MPA-03 · Modular](/mpa/chapters/03-arquitectura-modular.md) | Módulos por tenant |
| [MPA-06 · Integraciones](/mpa/chapters/06-integraciones.md) | Estrategia API |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Árbol `/api/v1/{module}/{resource}` disponible en código
- [ ] `maintenance/assets` y `auth`/`me` operativos bajo v1
- [ ] CRUD documentado coincide con endpoints reales
- [ ] Envelope `data` + `meta` + `links` unificado
- [ ] Legacy alias con headers `Deprecation` (MAG-07)
- [ ] OpenAPI generado desde este catálogo

**Este documento es la fuente oficial** para generar la especificación OpenAPI del producto y el SDK (Sprint 9).

---

## Filosofía del capítulo

Un recurso REST representa una **capacidad del negocio**, no una implementación técnica.

**MAG-04 define el contrato público de la plataforma.** Todos los clientes, SDKs, integraciones y futuras versiones de la API se construyen sobre este documento.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato v1** | ✅ Definido · árbol `/api/v1` completo |
| **Implementación** | 🟡 Parcial (auth · me · assets read legacy) |
| **Idioma contrato** | Inglés (URLs · methods · JSON keys) |
| **Legacy** | `/api/activos` → `/api/v1/maintenance/assets` |
| **Siguiente capítulo** | [MAG-05 · Convenciones](05-convenciones-nombres.md) |

---

→ [MAG-05-NAM · Convenciones de nombres](05-convenciones-nombres.md)
