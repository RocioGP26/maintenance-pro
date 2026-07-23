# MAG-05-NAM · Convenciones de nombres

> Una API consistente es una API predecible.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir las **reglas oficiales de nomenclatura** para todos los elementos públicos de la API Roustix: rutas, recursos, parámetros, campos JSON, identificadores y convenciones de desarrollo.

El objetivo es que cualquier desarrollador pueda **predecir un endpoint** sin consultar la documentación.

**Árbol de recursos:** [MAG-04 · Recursos REST](04-recursos.md).  
**MAG-05 es la guía de estilo oficial de la API** — MAG-06 a MAG-10 y el SDK deben referenciar este capítulo, no duplicar reglas.

---

## 1 · Filosofía

Una convención evita discusiones.

No existen:

- estilos por módulo
- nombres diferentes para el mismo concepto
- excepciones arbitrarias

Cada recurso sigue **exactamente las mismas reglas**.

---

## 2 · Idioma oficial

La documentación está escrita en **español**.  
La API está escrita en **inglés**.

| Elemento | Idioma |
|----------|--------|
| Documentación | Español |
| URLs | Inglés |
| Recursos | Inglés |
| JSON (claves envelope y campos públicos) | Inglés |
| Métodos HTTP | Inglés (`GET`, `POST`, …) |
| Errores (`error.code`) | Inglés · `UPPER_SNAKE_CASE` |
| Mensajes visibles al usuario | Español (MUX) |

| ✅ Correcto | ❌ Incorrecto |
|------------|--------------|
| `/assets` | `/activos` |
| `/work-orders` | `/ordenes` |
| `/products` | `/productos` |
| `/users` | `/usuarios` |

---

## 3 · Recursos

Todos los recursos son:

- **sustantivos**
- **plural**
- **kebab-case**

| ✅ Correcto | ❌ Incorrecto |
|------------|--------------|
| `work-orders` | `workOrders` |
| `purchase-orders` | `WorkOrders` |
| `stock-movements` | `work_order` |
| `user-groups` | `workorder` |

Namespace completo: `/api/v1/{module}/{resource}` — ver MAG-04.

---

## 4 · Métodos HTTP

Las acciones **nunca** forman parte del nombre del recurso. Los methods **no se traducen**.

| Method | Uso |
|--------|-----|
| **GET** | List · read |
| **POST** | Create · actions |
| **PUT** | Full replace |
| **PATCH** | Partial update |
| **DELETE** | Delete |

| ❌ Nunca | ✅ Siempre |
|---------|-----------|
| `/createAsset` | `POST /assets` |
| `/deleteUser` | `DELETE /users/15` |
| `/updateProduct` | `PATCH /products/8` |

---

## 5 · Identificadores

Los identificadores viajan en la **URL**:

```
/assets/25
/products/98
/work-orders/114
```

| ❌ Nunca |
|---------|
| `/assets?id=25` |

---

## 6 · Campos JSON

Todos los campos públicos utilizan **`snake_case`** en **inglés**:

```json
{
  "asset_id": 25,
  "asset_code": "CMP-001",
  "created_at": "2026-07-10T18:30:00Z",
  "critical": true
}
```

| ❌ Nunca |
|---------|
| `assetCode` · `AssetCode` · `asset-code` |

**Envelope** (MAG-04): `data`, `meta`, `links`, `included`, `pagination` — siempre en inglés.

**Legacy:** respuestas actuales pueden incluir `codigo`, `nombre` — convergencia al contrato inglés en `/api/v1`.

---

## 7 · Fechas

Formato único: **ISO 8601 UTC**.

```
2026-07-10T18:30:00Z
```

| ❌ No usar |
|-----------|
| `10/07/26` · `10-07-2026` · `Jul 10` |

---

## 8 · Parámetros

Query params en **inglés** · `snake_case`:

```http
?status=active
?page=2
?page_size=50
?include=history,work_orders
?filter[status]=operational
```

| ❌ Nunca |
|---------|
| `?Estado=Activo` · `?Pagina=2` |

No usar `empresa_id` en query — contexto desde JWT (MAG-03).

---

## 9 · Códigos internos (documentación)

Todos los códigos internos de la suite Roustix siguen nomenclatura consistente:

| Prefijo | Ejemplo |
|---------|---------|
| MAG | `MAG-05-NAM` |
| MPA | `MPA-04-SAAS` |
| MCM | `MCM-02-VALUE` |
| MRL | `MRL-03-ANAT` |
| MUX | `MUX-LAW-001` |
| MTX | `MTX-CASE-001` |

Esto mantiene alineada toda la documentación — distinto de códigos de error API (`RESOURCE_NOT_FOUND`).

---

## 10 · Errores

Los códigos de error API son:

- **MAYÚSCULAS**
- separados por **`_`**

| ✅ Correcto | ❌ Incorrecto |
|------------|--------------|
| `RESOURCE_NOT_FOUND` | `NotFound` |
| `INVALID_TOKEN` | `InvalidToken` |
| `MODULE_NOT_ENABLED` | `error_404` |
| `PERMISSION_DENIED` | `permisoDenegado` |

Detalle → [MAG-06 · Manejo de errores](06-manejo-errores.md).

---

## 11 · Versionado

| ✅ Siempre | ❌ Nunca |
|-----------|---------|
| `/api/v1/` | `/api/assets/v1` |
| | `/assets/v2` |
| | `/v1/assets/v2` |

Política completa → [MAG-07 · Versionado](07-versionado.md).

---

## 12 · Headers estándar

| Header | Valor |
|--------|-------|
| `Authorization` | `Bearer <jwt>` |
| `Content-Type` | `application/json` |
| `Accept` | `application/json` |
| `X-Request-Id` | UUID cliente (opcional, recomendado) |

---

## 13 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Una palabra = un concepto |
| 2 | No usar abreviaturas ambiguas |
| 3 | Mantener nombres estables entre versiones |
| 4 | Reutilizar recursos antes de crear nuevos |
| 5 | La documentación y el código deben coincidir |
| 6 | MAG-05 antes de añadir cualquier ruta nueva |

---

## 14 · Ejemplos completos

### ✅ Correcto

```http
GET /api/v1/maintenance/assets/25
```

```json
{
  "data": {
    "asset_id": 25,
    "asset_code": "CMP-001",
    "name": "Compressor B",
    "status": "operational"
  },
  "meta": {
    "api_version": "v1"
  },
  "links": {
    "self": "/api/v1/maintenance/assets/25"
  }
}
```

### ❌ Incorrecto

```http
GET /api/getMachine?id=25
```

```json
{
  "codigo": "CMP001"
}
```

---

## 15 · Migración legacy

| Legacy (hoy) | MAG v1 |
|--------------|--------|
| `/api/activos` | `/api/v1/maintenance/assets` |
| `/api/admin/resumen` | `/api/v1/admin/summary` |
| `/api/auth/login` | `/api/v1/auth/login` |
| `/api/me` | `/api/v1/me` |
| Campos `codigo`, `nombre` | `asset_code`, `name` |

Alias legacy con headers `Deprecation` (MAG-07).

---

## Relación con otros documentos

| Documento | Relación |
|-----------|----------|
| [MAG-04 · Recursos REST](04-recursos.md) | Define qué recursos existen |
| [MAG-06 · Manejo de errores](06-manejo-errores.md) | Usa estas convenciones |
| [MAG-07 · Versionado](07-versionado.md) | Estabilidad del contrato |
| [MPA-06 · Integraciones](/mpa/chapters/06-integraciones.md) | Base integraciones externas |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Todas las rutas usan inglés, plural y kebab-case
- [ ] Todos los cuerpos JSON utilizan `snake_case` en inglés
- [ ] Todos los códigos de error siguen `UPPER_SNAKE_CASE`
- [ ] Todas las fechas utilizan ISO 8601 UTC
- [ ] La documentación y la implementación comparten la misma nomenclatura
- [ ] No existen rutas nuevas fuera de estas convenciones

---

## Filosofía del capítulo

Una buena API no necesita memorizarse. Cuando todas las reglas son consistentes, los desarrolladores pueden **predecir** cómo funciona antes de leer la documentación.

**MAG-05 es el style guide oficial de la API Roustix** — equivalente a una guía de estilo para un lenguaje de programación. MAG-06 a MAG-10 y el SDK se apoyan en este documento.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato v1** | ✅ Definido |
| **Implementación** | 🟡 Parcial (legacy español en rutas/campos) |
| **Siguiente capítulo** | [MAG-06 · Manejo de errores](06-manejo-errores.md) |

---

→ [MAG-06-ERR · Manejo de errores](06-manejo-errores.md)
