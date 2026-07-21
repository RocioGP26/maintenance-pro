# MAG-09-EX · Ejemplos y SDK

**Código:** MAG-09-EX · Sprint 8.9 · **Entregado**

> Una buena API se entiende. Una excelente API también se puede ejecutar.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Proporcionar **ejemplos oficiales** de consumo de la API Roustix y definir las bases del **SDK oficial**, que permitirá integrar la plataforma desde cualquier lenguaje.

Mientras MAG-01 a MAG-08 definen el contrato, **MAG-09 demuestra cómo utilizarlo**.

Todos los ejemplos utilizan:

- contrato oficial `/api/v1` ([MAG-04](04-recursos.md))
- JWT ([MAG-02](02-autenticacion-jwt.md))
- multi-tenant ([MAG-03](03-multi-tenant.md))
- convenciones ([MAG-05](05-convenciones-nombres.md))
- errores ([MAG-06](06-manejo-errores.md))

> **Legacy hoy:** login y lectura de activos funcionan en `/api/auth/login` y `/api/activos` — ver [MAG-07](07-versionado.md). Los ejemplos muestran el **contrato v1** objetivo.

---

## 1 · Filosofía

La documentación no termina en la especificación. Debe incluir ejemplos que funcionen **igual que la implementación real**.

Todos los ejemplos deben ser:

- **completos**
- **ejecutables**
- **consistentes con OpenAPI**
- **compatibles con el SDK oficial**

---

## 2 · Entorno de desarrollo

| Entorno | Base URL |
|---------|----------|
| Servidor local | `http://127.0.0.1:5000` |
| API oficial (local) | `http://127.0.0.1:5000/api/v1` |
| Producción | `https://api.roustix.app/api/v1` |

Variables recomendadas:

```bash
export ROUSTIX_API=https://api.roustix.app/api/v1
export ROUSTIX_TOKEN=<jwt>
```

Iniciar servidor local:

```powershell
python run.py
```

---

## 3 · Login

### cURL

```bash
curl -X POST \
  http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "********",
    "empresa_slug": "empresa-demo"
  }'
```

**Legacy (funciona hoy):** `POST http://127.0.0.1:5000/api/auth/login`

**Respuesta contrato v1:**

```json
{
  "token": "eyJhbGc...",
  "expires_in": 86400,
  "user": {
    "id": 15,
    "nombre": "Admin",
    "rol": "admin"
  },
  "empresa": {
    "id": 4,
    "slug": "empresa-demo",
    "nombre": "Empresa Demo"
  }
}
```

**Legacy hoy:** `{ "token", "empresa_id", "empresa_slug", "rol", "username" }`

### Python

```python
import os
import requests

BASE = os.getenv("ROUSTIX_API", "http://127.0.0.1:5000/api/v1")

response = requests.post(
    f"{BASE}/auth/login",
    json={
        "username": "admin",
        "password": "********",
        "empresa_slug": "empresa-demo",
    },
    timeout=30,
)
response.raise_for_status()
token = response.json()["token"]
```

### JavaScript

```javascript
const BASE = "/api/v1";

const response = await fetch(`${BASE}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "admin",
    password: "********",
    empresa_slug: "empresa-demo",
  }),
});

const { token } = await response.json();
```

---

## 4 · Consultar recursos

```http
GET /api/v1/maintenance/assets
Authorization: Bearer <token>
```

### cURL

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:5000/api/v1/maintenance/assets
```

**Legacy (lectura hoy):**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:5000/api/activos
```

**Respuesta legacy:**

```json
{
  "total": 3,
  "items": [
    {
      "id": 1,
      "codigo": "M-001",
      "nombre": "Compresor A",
      "status": "operativo",
      "ubicacion": "Planta 1",
      "es_critico": true
    }
  ]
}
```

**Respuesta contrato v1 (objetivo):**

```json
{
  "data": [
    {
      "asset_id": 1,
      "asset_code": "M-001",
      "name": "Compressor A",
      "status": "operational",
      "critical": true
    }
  ],
  "meta": {
    "pagination": { "page": 1, "page_size": 50, "total": 3 }
  },
  "links": {
    "self": "/api/v1/maintenance/assets?page=1&page_size=50"
  }
}
```

### Contexto tenant

```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:5000/api/v1/me
```

Legacy: `GET /api/me`

---

## 5 · Crear un recurso

```http
POST /api/v1/maintenance/assets
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "asset_code": "CMP-001",
  "name": "Compressor B",
  "critical": true
}
```

**Respuesta:**

```http
HTTP/1.1 201 Created
```

```json
{
  "data": {
    "asset_id": 25
  },
  "meta": {
    "api_version": "v1"
  }
}
```

**Estado implementación:** 📋 Planificado

---

## 6 · Actualizar un recurso

```http
PATCH /api/v1/maintenance/assets/25
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "status": "maintenance"
}
```

**Estado implementación:** 📋 Planificado

---

## 7 · Manejo de errores

```http
GET /api/v1/maintenance/assets/900
```

**Respuesta:**

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Activo no encontrado"
  }
}
```

**Legacy hoy:**

```json
{"error": "Activo no encontrado"}
```

Los clientes deben utilizar **`error.code`** — nunca interpretar el texto de `message`.

→ [MAG-06](06-manejo-errores.md)

---

## 8 · SDK oficial

Roustix dispondrá de SDKs oficiales construidos sobre el contrato MAG.

| SDK | Estado |
|-----|--------|
| **Python** | 📋 Planificado |
| **JavaScript / TypeScript** | 📋 Planificado |
| **PHP** | 📋 Planificado |
| **C# (.NET)** | Roadmap |
| **Java** | Roadmap |

Todos consumen **exactamente la misma API**.

→ [SDK (suite 08)](../../sdk/README.md)

---

## 9 · Estructura del SDK

Ejemplo conceptual (Python):

```python
from roustix import Client

client = Client(
    token="...",
    base_url="https://api.roustix.app/api/v1",
)

assets = client.maintenance.assets.list()
```

Crear activo:

```python
client.maintenance.assets.create(
    asset_code="CMP-001",
    name="Compressor B",
    critical=True,
)
```

---

## 10 · Organización del SDK

```
Roustix Client
│
├── auth
├── maintenance
│      ├── assets
│      ├── work_orders
│      └── schedules
│
├── inventory
│
├── admin
│
└── webhooks
```

La estructura **replica exactamente** [MAG-04](04-recursos.md).

---

## 11 · OpenAPI

El SDK se genera desde:

```
/api/v1/openapi.json
```

o

```
docs/api/openapi.v1.yaml
```

No debe implementarse manualmente cada cliente cuando pueda **derivarse del contrato**.

→ [MAG-07 · OpenAPI](07-versionado.md#11--openapi)

---

## 12 · Ejemplo completo

```python
from roustix import Client

client = Client(token="JWT...")

assets = client.maintenance.assets.list()

for asset in assets:
    print(asset.name)
```

**Resultado esperado:**

```
Compressor A
Compressor B
Compressor C
```

**Estado:** SDK planificado · ejemplo ilustrativo.

---

## 13 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Utilizar siempre el SDK cuando exista |
| 2 | Mantener el JWT fuera del código fuente |
| 3 | No construir URLs manualmente |
| 4 | Respetar el contrato MAG |
| 5 | Manejar errores mediante `error.code` |
| 6 | Configurar tiempos de espera razonables |
| 7 | Registrar `X-Request-Id` cuando esté disponible |

---

## 14 · Roadmap

Próximas capacidades del SDK:

- renovación automática de tokens
- reintentos configurables
- paginación automática
- cliente asíncrono
- tipado completo
- generación automática desde OpenAPI
- CLI oficial (`roustix-cli`)

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MAG-02 · Auth JWT](02-autenticacion-jwt.md) | Obtención del token |
| [MAG-04 · Recursos REST](04-recursos.md) | Recursos utilizados |
| [MAG-05 · Convenciones](05-convenciones-nombres.md) | Nombres y estructuras |
| [MAG-06 · Errores](06-manejo-errores.md) | Tratamiento de respuestas |
| [MAG-07 · Versionado](07-versionado.md) | Compatibilidad del SDK |
| [MAG-08 · Webhooks](08-webhooks.md) | Recepción de eventos |
| [MPA-06 · Integraciones](/mpa/chapters/06-integraciones.md) | Ecosistema de integración |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Todos los ejemplos utilizan `/api/v1`
- [ ] Existe al menos un ejemplo funcional en cURL, Python y JavaScript
- [ ] El SDK replica la estructura oficial de recursos
- [ ] El SDK se genera a partir de OpenAPI
- [ ] Todos los ejemplos respetan MAG-05 y MAG-06
- [ ] La documentación puede ejecutarse sin modificaciones significativas

---

## Filosofía del capítulo

Una API bien diseñada debe ser fácil de aprender, pero también **rápida de integrar**. Los ejemplos y el SDK reducen el tiempo entre leer la documentación y tener una integración funcionando.

**MAG-09 transforma el contrato de Roustix en una experiencia práctica** — referencia ejecutable para desarrolladores, partners e integradores.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato** | ✅ Definido |
| **Implementación actual** | 🟡 Ejemplos legacy ejecutables · SDK planificado |
| **Compatibilidad** | API REST v1 |
| **Roadmap** | SDK Python · JavaScript · PHP |
| **Siguiente capítulo** | — · **MAG v1.0 completo** |

---

→ [MAG-10-LIM · Límites y buenas prácticas](10-limites-buenas-practicas.md)
