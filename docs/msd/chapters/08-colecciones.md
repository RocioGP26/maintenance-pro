# MSD-08-COLL · Colecciones Postman e Insomnia

**Código:** MSD-08-COLL · Sprint 9.8 · **Entregado**

> La primera llamada a la API no debería comenzar escribiendo una petición desde cero.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir las **colecciones oficiales** de Postman e Insomnia de Roustix, generadas automáticamente desde la especificación **OpenAPI 3.1**, permitiendo que cualquier desarrollador explore, pruebe y documente la API sin configuración manual.

Las colecciones representan una implementación práctica del contrato **MAG v1.0**, garantizando consistencia entre documentación, SDK y herramientas de prueba.

→ [MSD-03 · OpenAPI](03-openapi.md) · [MSD-07 · Quick Start](07-quick-start.md)

---

## 1 · Filosofía

La documentación **explica** la API.

Las colecciones permiten **ejecutarla**.

```
OpenAPI
      │
      ▼
Colección oficial
      │
      ├── Postman
      │
      └── Insomnia
            │
            ▼
       API Roustix
```

Las colecciones **nunca se editan manualmente** de forma permanente — siempre se **generan desde OpenAPI**.

| Regla | Descripción |
|-------|-------------|
| OpenAPI primero | Cambio en MAG → OpenAPI → regenerar colecciones |
| Sin drift | No duplicar paths fuera del contrato |
| Sandbox | Variables apuntan a `empresa-demo` |

---

## 2 · Objetivos

Las colecciones permiten:

- explorar todos los endpoints
- autenticarse mediante JWT
- probar recursos REST
- validar respuestas
- compartir ejemplos
- acelerar el desarrollo

Son una herramienta de **aprendizaje** y de **pruebas**.

---

## 3 · Colección Postman

**Nombre oficial:** `Roustix API v1`

**Estructura:**

```
Roustix API v1
│
├── Authentication
├── Me
├── Maintenance
│     ├── Assets
│     ├── Work Orders
│     ├── Schedules
│     └── Lubrication
│
├── Inventory
├── Purchases
├── Sales
├── CRM
└── Admin
```

Cada carpeta corresponde a un **módulo definido en MAG-04**.

**Archivo:** [`docs/api/collections/roustix-api-v1.postman_collection.json`](../../api/collections/roustix-api-v1.postman_collection.json)

**Entorno Sandbox:** [`roustix-sandbox.postman_environment.json`](../../api/collections/roustix-sandbox.postman_environment.json)

---

## 4 · Colección Insomnia

La organización **replica exactamente** la colección de Postman.

```
Roustix API v1
│
├── Authentication
├── Maintenance
├── Inventory
├── Admin
└── ...
```

El objetivo es que ambas herramientas ofrezcan la **misma experiencia**.

**Archivo:** [`docs/api/collections/roustix-api-v1.insomnia.json`](../../api/collections/roustix-api-v1.insomnia.json)

---

## 5 · Variables de entorno

Las colecciones utilizan variables **reutilizables**:

| Variable | Descripción |
|----------|-------------|
| `base_url` | URL base del servidor (`http://127.0.0.1:5000`) |
| `api_v1` | `{{base_url}}/api/v1` |
| `token` | JWT activo |
| `empresa_slug` | Tenant Sandbox (`empresa-demo`) |
| `asset_id` | Activo de ejemplo |
| `work_order_id` | OT de ejemplo |

**Ejemplo:**

```
{{api_v1}}/me
Authorization: Bearer {{token}}
```

**No se almacenan credenciales reales** dentro de las colecciones — solo placeholders.

> **Local hoy:** algunos endpoints legacy usan `/api/auth/login` y `/api/activos`. La colección base incluye rutas v1; ver [`collections/README.md`](../../api/collections/README.md) para importación local.

---

## 6 · Autenticación automática

La carpeta **Authentication** incluye el flujo completo:

```http
POST /api/v1/auth/login
```

El JWT obtenido se almacena automáticamente como variable `token` (script Postman / Insomnia chain).

```
Login
   │
   ▼
 JWT
   │
   ▼
Variable token
   │
   ▼
Resto de endpoints
```

→ [MAG-02 · JWT](/mag/chapters/02-autenticacion-jwt.md)

---

## 7 · Generación

Las colecciones se generan automáticamente desde:

```
docs/api/openapi.v1.yaml
```

**Proceso:**

```
MAG
   │
   ▼
OpenAPI
   │
   ▼
Generador (OpenAPI Generator · openapi2postman · insomnia-importer)
   │
   ▼
Postman · Insomnia
```

**No existen colecciones mantenidas manualmente** en el flujo de release — la versión en repo es **snapshot** hasta CI automatizado (MSD v1.0).

| Herramienta | Comando (planificado) |
|-------------|----------------------|
| Postman | `openapi2postmanv2 -s openapi.v1.yaml -o roustix-api-v1.postman_collection.json` |
| Insomnia | Generación desde OpenAPI import en CI |

---

## 8 · Casos de uso

Las colecciones permiten:

| Caso | Audiencia |
|------|-----------|
| Probar nuevos endpoints | Desarrollo |
| Validar autenticación | Integradores |
| Demostrar funcionalidades | Comercial · MCM |
| Depurar integraciones | Soporte L2 |
| Capacitación | Partners |
| Verificar cambios pre-release | QA API |

También sirven como **base** para pruebas automatizadas (Newman · Insomnia CLI).

---

## 9 · Versionado

Las colecciones siguen el mismo ciclo de vida que la API ([MAG-07](/mag/chapters/07-versionado.md)):

| Colección | API |
|-----------|-----|
| **Roustix API v1** | MAG v1 |
| **Roustix API v2** | MAG v2 |

Cada versión mantiene su **propia colección independiente**.

---

## 10 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Generar las colecciones desde OpenAPI |
| 2 | No editar colecciones manualmente en release |
| 3 | Utilizar variables de entorno |
| 4 | No almacenar credenciales reales |
| 5 | Sincronizar cada publicación con MAG |
| 6 | Probar todas las solicitudes antes de cada versión |

---

## 11 · Distribución

Las colecciones están disponibles desde:

| Recurso | Ubicación |
|---------|-----------|
| **Developer Portal** | Descarga directa (MSD-02) |
| **Repositorio** | `docs/api/collections/` |
| **OpenAPI** | Regeneración automática (CI) |
| **Sandbox** | Importación inmediata |

**Archivos:**

| Archivo | Formato |
|---------|---------|
| `roustix-api-v1.postman_collection.json` | Postman Collection v2.1 |
| `roustix-api-v1.insomnia.json` | Insomnia Export v4 |
| `roustix-sandbox.postman_environment.json` | Postman Environment |

**Importar en Postman:** File → Import → seleccionar colección + entorno Sandbox.

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MSD-02 · Developer Portal](02-developer-portal.md) | Descarga de colecciones |
| [MSD-03 · OpenAPI](03-openapi.md) | Fuente de generación |
| [MSD-06 · Sandbox](06-sandbox-explorer.md) | Entorno de pruebas |
| [MSD-07 · Quick Start](07-quick-start.md) | Primer recorrido |
| [MAG-04 · Recursos](/mag/chapters/04-recursos.md) | Recursos incluidos |
| [MAG-07 · Versionado](/mag/chapters/07-versionado.md) | Versionado de colecciones |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] Existe una colección oficial para Postman (snapshot v1)
- [x] Existe una colección oficial para Insomnia (snapshot v1)
- [ ] Ambas se generan automáticamente desde OpenAPI en CI
- [x] Incluyen recursos core definidos en MAG-04 (auth · me · assets · admin)
- [x] Incorporan variables de entorno reutilizables
- [x] El flujo de autenticación JWT está preconfigurado (Postman test script)
- [ ] Las colecciones están disponibles desde el Developer Portal (UI descarga)

**Colecciones base + documentación:** ✅ · **Generación CI + portal UI:** 🟡 pendiente

---

## Filosofía del capítulo

Las colecciones oficiales convierten el contrato de la API en una **experiencia interactiva**. En lugar de construir solicitudes manualmente, el desarrollador importa una colección, se autentica y comienza a trabajar en minutos.

**MSD-08 establece las herramientas oficiales de exploración y prueba de Roustix**, garantizando que documentación, OpenAPI y herramientas de desarrollo evolucionen siempre de forma sincronizada.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Colección Postman** | 🟢 Snapshot v1 en repo |
| **Colección Insomnia** | 🟢 Snapshot v1 en repo |
| **Generación** | 🟡 Desde OpenAPI 3.1 (CI planificado) |
| **Distribución** | 🟡 Repo · 📋 Developer Portal UI |
| **Siguiente capítulo** | [MSD-09 · Publicación](09-publicacion.md) |

---

→ [MSD-09-PUB · Publicación de paquetes](09-publicacion.md)
