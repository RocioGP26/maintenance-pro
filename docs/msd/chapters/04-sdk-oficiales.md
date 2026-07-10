# MSD-04-SDK · SDK oficiales

**Código:** MSD-04-SDK · Sprint 9.4 · **Entregado**

> Una API excelente merece un SDK excelente.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir la **estrategia oficial** para los SDK Maintix — bibliotecas nativas que encapsulan autenticación, consumo de la API, manejo de errores y buenas prácticas definidas en MAG.

Los SDK eliminan la necesidad de construir manualmente solicitudes HTTP y garantizan que todas las integraciones utilicen el **mismo contrato**.

**MSD-04 convierte la API documentada en una experiencia de desarrollo lista para usar.**

→ [MSD-03 · OpenAPI 3.1](03-openapi.md) · [Developer Portal](02-developer-portal.md)

---

## 1 · Filosofía

El SDK **no reemplaza** la API.

La API sigue siendo el **contrato oficial**.

El SDK únicamente ofrece una forma más **cómoda y segura** de consumir ese contrato.

```
Aplicación
      │
      ▼
 Maintix SDK
      │
      ▼
   OpenAPI
      │
      ▼
  REST API
```

Toda mejora del SDK debe mantenerse **alineada con MAG**.

| Principio | Regla |
|-----------|-------|
| API primero | El contrato vive en MAG + OpenAPI |
| SDK idiomático | Cada lenguaje expone la misma semántica, sintaxis nativa |
| Sin atajos | No omitir tenant, JWT ni errores estructurados |

---

## 2 · Lenguajes oficiales

**MSD v1.0** contempla tres SDK oficiales.

| Lenguaje | Paquete | Estado |
|----------|---------|--------|
| **Python** | `maintix` | 📋 Implementación pendiente |
| **JavaScript / TypeScript** | `@maintix/sdk` | 📋 Implementación pendiente |
| **PHP** | `maintix/sdk` | 📋 Implementación pendiente |

**Roadmap futuro:**

- Java
- C# (.NET)
- Go

---

## 3 · Instalación

**Python:**

```bash
pip install maintix
```

**JavaScript:**

```bash
npm install @maintix/sdk
```

**PHP:**

```bash
composer require maintix/sdk
```

Todos los paquetes siguen el **mismo versionado** que MAG (`1.x` → MAG v1).

---

## 4 · Inicialización

Ejemplo conceptual — base URL incluye `/api/v1`:

**Python:**

```python
from maintix import MaintixClient

client = MaintixClient(
    base_url="https://api.maintix.app/api/v1",
    token="JWT",
)
```

**JavaScript:**

```javascript
import { MaintixClient } from "@maintix/sdk";

const client = new MaintixClient({
  baseUrl: process.env.MAINTIX_API,
  token: process.env.MAINTIX_TOKEN,
});
```

**PHP:**

```php
use Maintix\Client;

$client = new Client(
    token: getenv('MAINTIX_TOKEN'),
    baseUrl: 'https://api.maintix.app/api/v1',
);
```

Variables de entorno recomendadas: `MAINTIX_API` · `MAINTIX_TOKEN` ([MAG-09](/mag/chapters/09-ejemplos.md)).

---

## 5 · Organización

Todos los SDK exponen la **misma estructura** — alineada a [MAG-04](/mag/chapters/04-recursos.md):

```
client
│
├── auth
├── me
├── maintenance
│     ├── assets
│     ├── work_orders
│     └── schedules
├── inventory
│     ├── products
│     └── stock
├── purchasing
├── sales
├── crm
└── admin
```

**Ejemplos:**

```python
client.maintenance.assets.list()
client.inventory.products.get(25)
client.auth.login(username="...", password="...", empresa_slug="...")
```

Convenciones de nombres en superficie del SDK → [MAG-05](/mag/chapters/05-convenciones-nombres.md) (contrato JSON en inglés `snake_case`; JS puede exponer `camelCase` en props con mapeo interno).

---

## 6 · Manejo automático

El SDK administra automáticamente:

| Responsabilidad | Referencia MAG |
|-----------------|----------------|
| **JWT** | Header `Authorization: Bearer` · [MAG-02](/mag/chapters/02-autenticacion-jwt.md) |
| **Headers** | `Content-Type` · `Accept` · `User-Agent` |
| **JSON** | Serialización / deserialización |
| **Timeouts** | [MAG-10](/mag/chapters/10-limites-buenas-practicas.md) |
| **Reintentos** | 429 · 503 · backoff exponencial |
| **Errores MAG-06** | `error.code` → excepciones |
| **User-Agent** | `maintix-python/1.0.0` (por lenguaje) |

El desarrollador trabaja únicamente con **objetos y métodos** — no con URLs ni headers crudos.

---

## 7 · Manejo de errores

Los errores MAG se convierten en **excepciones tipadas**.

**Python:**

```python
from maintix.errors import ResourceNotFoundError

try:
    client.maintenance.assets.get(500)
except ResourceNotFoundError as exc:
    print(exc.code)  # RESOURCE_NOT_FOUND
```

**JavaScript:**

```javascript
try {
  await client.maintenance.assets.get(500);
} catch (error) {
  if (error instanceof ResourceNotFoundError) {
    console.log(error.code);
  }
}
```

**PHP:**

```php
try {
    $client->maintenance->assets->get(500);
} catch (ResourceNotFoundException $e) {
    echo $e->getCode(); // RESOURCE_NOT_FOUND
}
```

Todos los códigos provienen del catálogo [MAG-06](/mag/chapters/06-manejo-errores.md). El cliente **nunca** interpreta `error.message`.

---

## 8 · Generación

Los SDK se generan **parcialmente** desde OpenAPI ([MSD-03](03-openapi.md)):

```
OpenAPI
     │
     ▼
 Generador
     │
     ▼
 SDK Base
     │
     ▼
Wrappers Maintix
```

| Capa | Contenido |
|------|-----------|
| **Generado** | Models · paths · request/response types |
| **Manual (wrappers)** | Auth flow · retries · pagination helpers · ergonomía |

La generación automática evita **inconsistencias** entre lenguajes.

Herramientas previstas: OpenAPI Generator · Speakeasy · `openapi-typescript` (tipos JS).

---

## 9 · Versionado

Los SDK utilizan el **mismo ciclo de vida** que MAG ([MAG-07](/mag/chapters/07-versionado.md)):

| SDK | API |
|-----|-----|
| **1.x** | MAG v1 |
| **2.x** | MAG v2 |

**Nunca** mezclar varias versiones de API dentro del mismo major del SDK.

| Bump SDK | Cuándo |
|----------|--------|
| **MAJOR** | MAG v2 · breaking en contrato |
| **MINOR** | Nuevos recursos en MAG v1 |
| **PATCH** | Fixes sin cambio de contrato |

---

## 10 · Ejemplo completo

**Python:**

```python
from maintix import MaintixClient

client = MaintixClient(
    base_url="https://api.maintix.app/api/v1",
    token="JWT",
)

assets = client.maintenance.assets.list()

for asset in assets:
    print(asset.name)
```

Sin construir manualmente requests HTTP.

**Estado:** ejemplo ilustrativo · paquete `maintix` en implementación.

→ [MAG-09 · Ejemplos](/mag/chapters/09-ejemplos.md)

---

## 11 · Publicación

| Plataforma | Paquete | Estado |
|------------|---------|--------|
| **PyPI** | `maintix` | 📋 |
| **npm** | `@maintix/sdk` | 📋 |
| **Packagist** | `maintix/sdk` | 📋 |

**Repositorios oficiales (planificados):**

- `github.com/maintix/sdk-python`
- `github.com/maintix/sdk-js`
- `github.com/maintix/sdk-php`

Publicación detallada → [MSD-09 · Publicación](09-publicacion.md)

Código fuente local de referencia → [`docs/sdk/`](../../sdk/README.md)

---

## 12 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | No modificar el SDK generado manualmente sin actualizar OpenAPI |
| 2 | Toda mejora permanente debe originarse en OpenAPI |
| 3 | Mantener el mismo modelo de objetos entre lenguajes |
| 4 | Respetar MAG-06 para manejo de errores |
| 5 | Versionar junto con MAG |
| 6 | Publicar ejemplos ejecutables para cada lenguaje |
| 7 | Usar el SDK oficial cuando exista — no construir URLs a mano ([MAG-09](/mag/chapters/09-ejemplos.md)) |

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MAG-04 · Recursos REST](/mag/chapters/04-recursos.md) | Recursos disponibles |
| [MAG-05 · Convenciones](/mag/chapters/05-convenciones-nombres.md) | Nombres y estructuras |
| [MAG-06 · Errores](/mag/chapters/06-manejo-errores.md) | Excepciones del SDK |
| [MAG-07 · Versionado](/mag/chapters/07-versionado.md) | Versionado del SDK |
| [MSD-03 · OpenAPI](03-openapi.md) | Fuente de generación |
| [MSD-05 · CLI](05-cli.md) | Herramienta complementaria |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Existe un SDK oficial para Python
- [ ] Existe un SDK oficial para JavaScript
- [ ] Existe un SDK oficial para PHP
- [ ] Los SDK se generan desde OpenAPI
- [ ] El manejo de errores implementa MAG-06
- [ ] La autenticación JWT es automática
- [ ] Los SDK se publican en PyPI, npm y Packagist

**Estrategia y contrato SDK:** ✅ · **Paquetes publicados:** 📋 pendiente

---

## Filosofía del capítulo

Una buena API permite integrar una plataforma.

Un buen SDK hace que esa integración sea **natural**.

El desarrollador no debería preocuparse por construir solicitudes HTTP, gestionar encabezados o interpretar respuestas. Su trabajo debe centrarse en el **negocio**, mientras el SDK aplica automáticamente el contrato definido por MAG.

**MSD-04 convierte la API de Maintix en una experiencia de desarrollo idiomática, consistente y lista para producción.**

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato** | ✅ Definido |
| **Generación** | 🟡 Basada en OpenAPI (MSD-03) |
| **Implementación** | 📋 Pendiente |
| **Publicación** | 📋 PyPI · npm · Packagist |
| **Siguiente capítulo** | [MSD-05 · CLI](05-cli.md) |

---

→ [MSD-05-CLI · CLI](05-cli.md)
