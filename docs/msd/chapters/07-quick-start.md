# MSD-07-QS · Quick Start

**Código:** MSD-07-QS · Sprint 9.7 · **Entregado**

> La mejor documentación es aquella que permite realizar la primera integración en **menos de diez minutos**.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir la **guía oficial de Quick Start** de Roustix, permitiendo que cualquier desarrollador:

1. obtenga un JWT
2. consulte la API
3. recupere su primer recurso

…utilizando el contrato definido por **MAG v1**.

El Quick Start es el **punto de entrada recomendado** para todos los nuevos integradores y constituye el **recorrido principal** del Developer Portal.

→ [MSD-02 · Developer Portal](02-developer-portal.md) · [MSD-06 · Sandbox](06-sandbox-explorer.md)

---

## 1 · Filosofía

La primera experiencia determina la percepción de toda la plataforma.

Un desarrollador debe ser capaz de:

- autenticarse
- obtener un JWT
- consultar la API
- recibir una respuesta válida
- comprender el flujo completo

…**sin necesidad de leer toda la documentación**.

```
Crear cuenta / credenciales Sandbox
      │
      ▼
     Login
      │
      ▼
     JWT
      │
      ▼
 Primer endpoint
      │
      ▼
Primera integración
```

**Objetivo:** completar este recorrido en **menos de 10 minutos**.

---

## 2 · Requisitos

Antes de comenzar, el desarrollador necesita:

| Requisito | Detalle |
|-----------|---------|
| Developer Portal | [/msd/](/msd/) |
| Credenciales Sandbox | tenant `empresa-demo` |
| Conexión | HTTPS (prod) · HTTP local en dev |
| Herramienta | cURL · Postman · SDK · CLI |

**Entorno:** toda la guía utiliza el **Sandbox** — nunca producción en la primera prueba.

**Local:**

```powershell
python run.py
# API: http://127.0.0.1:5000
```

Variables recomendadas:

```bash
export ROUSTIX_API=http://127.0.0.1:5000/api/v1
export ROUSTIX_TOKEN=<jwt>
```

> **Legacy hoy:** login en `/api/auth/login` · `/me` en `/api/me` · activos en `/api/activos`. Los pasos muestran **contrato v1**; ver notas por paso.

---

## 3 · Paso 1 · Autenticación

**Solicitud:**

```http
POST /api/v1/auth/login
Content-Type: application/json
```

```json
{
  "username": "demo.user",
  "password": "********",
  "empresa_slug": "empresa-demo"
}
```

**Respuesta (contrato v1):**

```json
{
  "token": "<jwt>",
  "expires_in": 86400
}
```

**Legacy hoy:**

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"***","empresa_slug":"empresa-demo"}'
```

```json
{
  "token": "<jwt>",
  "empresa_id": 4,
  "empresa_slug": "empresa-demo",
  "rol": "admin",
  "username": "admin"
}
```

**Conservar el JWT** para las siguientes solicitudes.

→ [MAG-02 · JWT](/mag/chapters/02-autenticacion-jwt.md)

---

## 4 · Paso 2 · Obtener información del usuario

```http
GET /api/v1/me
Authorization: Bearer <token>
```

**Respuesta (contrato v1):**

```json
{
  "data": {
    "user_id": 15,
    "name": "Demo User",
    "role": "admin",
    "empresa": "Empresa Demo"
  }
}
```

**Legacy hoy (`GET /api/me`):**

```json
{
  "user_id": 15,
  "empresa_id": 4,
  "empresa_slug": "empresa-demo",
  "rol": "admin"
}
```

Este endpoint **confirma** que la autenticación y el contexto tenant fueron exitosos.

---

## 5 · Paso 3 · Consultar el primer recurso

```http
GET /api/v1/maintenance/assets
Authorization: Bearer <token>
```

**Respuesta (contrato v1):**

```json
{
  "data": [
    {
      "asset_id": 25,
      "asset_code": "CMP-001",
      "name": "Compressor B"
    }
  ],
  "meta": {
    "pagination": { "page": 1, "page_size": 50, "total": 1 }
  }
}
```

**Legacy hoy (`GET /api/activos`):**

```json
{
  "total": 3,
  "items": [
    {
      "id": 1,
      "codigo": "M-001",
      "nombre": "Compresor A",
      "status": "operativo"
    }
  ]
}
```

El desarrollador ya ha realizado su **primera consulta completa** a la API.

→ [MAG-04 · Recursos](/mag/chapters/04-recursos.md)

---

## 6 · Ejemplos por lenguaje

Todos los ejemplos oficiales se ofrecen en **cURL**, **Python**, **JavaScript** y **PHP**.

Los ejemplos se **generan desde OpenAPI** ([MSD-03](03-openapi.md)) para permanecer sincronizados con MAG.

### cURL (recorrido completo)

```bash
# 1 · Login
TOKEN=$(curl -s -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"***","empresa_slug":"empresa-demo"}' \
  | jq -r .token)

# 2 · Me
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/me | jq

# 3 · Activos
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:5000/api/activos | jq
```

### Python

```python
import os
import requests

BASE = os.getenv("ROUSTIX_API", "http://127.0.0.1:5000/api/v1")
# Legacy local: usar http://127.0.0.1:5000/api para auth/login y /activos

r = requests.post(
    f"{BASE.replace('/api/v1', '/api')}/auth/login",
    json={
        "username": "admin",
        "password": "***",
        "empresa_slug": "empresa-demo",
    },
    timeout=30,
)
token = r.json()["token"]

me = requests.get(
    f"{BASE.replace('/api/v1', '/api')}/me",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10,
)
print(me.json())

assets = requests.get(
    f"{BASE.replace('/api/v1', '/api')}/activos",
    headers={"Authorization": f"Bearer {token}"},
    timeout=10,
)
print(assets.json())
```

### JavaScript

```javascript
const BASE = "http://127.0.0.1:5000/api";

const login = await fetch(`${BASE}/auth/login`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    username: "admin",
    password: "***",
    empresa_slug: "empresa-demo",
  }),
});
const { token } = await login.json();

const me = await fetch(`${BASE}/me`, {
  headers: { Authorization: `Bearer ${token}` },
});
console.log(await me.json());

const assets = await fetch(`${BASE}/activos`, {
  headers: { Authorization: `Bearer ${token}` },
});
console.log(await assets.json());
```

### PHP

```php
$base = 'http://127.0.0.1:5000/api';

$ch = curl_init("$base/auth/login");
curl_setopt_array($ch, [
    CURLOPT_POST => true,
    CURLOPT_HTTPHEADER => ['Content-Type: application/json'],
    CURLOPT_POSTFIELDS => json_encode([
        'username' => 'admin',
        'password' => '***',
        'empresa_slug' => 'empresa-demo',
    ]),
    CURLOPT_RETURNTRANSFER => true,
]);
$token = json_decode(curl_exec($ch), true)['token'];

$headers = ["Authorization: Bearer $token"];
$me = file_get_contents("$base/me", false, stream_context_create([
    'http' => ['header' => implode("\r\n", $headers)],
]));
echo $me;
```

---

## 7 · Uso del SDK

**Python** (conceptual · [MSD-04](04-sdk-oficiales.md)):

```python
from roustix import RoustixClient

client = RoustixClient(
    base_url="http://127.0.0.1:5000/api/v1",
    token="JWT",
)

assets = client.maintenance.assets.list()
print(assets)
```

El mismo flujo existe para **JavaScript** y **PHP** cuando los paquetes estén publicados.

---

## 8 · Uso de la CLI

```bash
roustix login
roustix whoami
roustix assets list
```

La CLI utiliza el mismo contrato que el SDK y la API REST → [MSD-05](05-cli.md).

---

## 9 · Próximos pasos

Una vez completado el Quick Start:

| Paso | Recurso |
|------|---------|
| Explorar recursos REST | [MAG-04](/mag/chapters/04-recursos.md) |
| API Explorer | [MSD-06](06-sandbox-explorer.md) |
| Descargar OpenAPI | [MSD-03](03-openapi.md) · `/api/v1/openapi.json` |
| Instalar SDK | [MSD-04](04-sdk-oficiales.md) |
| Probar Webhooks | [MAG-08](/mag/chapters/08-webhooks.md) |
| Sandbox avanzado | [MSD-06](06-sandbox-explorer.md) |
| Errores y límites | [MAG-06](/mag/chapters/06-manejo-errores.md) · [MAG-10](/mag/chapters/10-limites-buenas-practicas.md) |

El Quick Start es **únicamente el punto de partida**.

---

## 10 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Utilizar siempre el **Sandbox** para las primeras pruebas |
| 2 | Conservar el JWT de forma segura |
| 3 | Revisar los códigos de error definidos en MAG-06 |
| 4 | Utilizar los SDK oficiales cuando estén disponibles |
| 5 | Consultar OpenAPI antes de implementar nuevos recursos |
| 6 | Migrar a **Producción** únicamente tras validar la integración |

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MSD-02 · Developer Portal](02-developer-portal.md) | Punto de entrada · CTA «Comenzar» |
| [MSD-03 · OpenAPI](03-openapi.md) | Fuente de los ejemplos |
| [MSD-04 · SDK](04-sdk-oficiales.md) | Implementación simplificada |
| [MSD-05 · CLI](05-cli.md) | Ejecución desde terminal |
| [MSD-06 · Sandbox](06-sandbox-explorer.md) | Entorno de pruebas |
| [MAG-02 · JWT](/mag/chapters/02-autenticacion-jwt.md) | Obtención del token |
| [MAG-04 · Recursos](/mag/chapters/04-recursos.md) | Primer recurso consultado |
| [MAG-09 · Ejemplos](/mag/chapters/09-ejemplos.md) | Ejemplos ampliados del contrato |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Un desarrollador puede autenticarse en menos de 2 minutos
- [ ] El recorrido completo (login → `/me` → primer recurso) puede realizarse en menos de 10 minutos
- [x] Existen ejemplos oficiales en cURL, Python, JavaScript y PHP
- [x] Los ejemplos están alineados a OpenAPI / MAG v1 (con notas legacy)
- [ ] El Quick Start está integrado en el Developer Portal (UI interactiva)
- [x] La guía utiliza exclusivamente el entorno Sandbox
- [ ] Todos los ejemplos provienen automáticamente de la especificación OpenAPI (generación CI)

**Guía documental:** ✅ · **Portal interactivo + generación automática:** 🟡 pendiente

---

## Filosofía del capítulo

El Quick Start representa la **primera experiencia** con Roustix. Debe ser breve, práctico y reproducible. En pocos minutos, cualquier desarrollador debe comprender el flujo de autenticación, ejecutar su primera llamada a la API y estar preparado para construir una integración completa.

**MSD-07 establece el recorrido oficial de onboarding** para desarrolladores, convirtiendo la documentación en una experiencia guiada y lista para usar.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Quick Start** | ✅ Definido |
| **Sandbox** | 🟡 Dependiente de MSD-06 |
| **OpenAPI** | 🟢 Fuente oficial de ejemplos |
| **SDK** | 🟡 En desarrollo |
| **Siguiente capítulo** | [MSD-08 · Colecciones](08-colecciones.md) |

---

→ [MSD-08-COLL · Postman e Insomnia](08-colecciones.md)
