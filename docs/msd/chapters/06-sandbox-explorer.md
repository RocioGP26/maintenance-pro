# MSD-06-SBOX · Sandbox y API Explorer

**Código:** MSD-06-SBOX · Sprint 9.6 · **Entregado**

> Antes de integrar en producción, todo comienza en el Sandbox.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir el **entorno oficial de pruebas (Sandbox)** y el **API Explorer** de Roustix, permitiendo a desarrolladores, partners e integradores experimentar con la API en un entorno completamente aislado, utilizando datos de demostración y el contrato oficial de **MAG v1**.

El Sandbox proporciona una experiencia **segura** para desarrollar, validar integraciones y aprender a utilizar la plataforma **sin riesgo** para información de clientes.

→ [MSD-02 · Developer Portal](02-developer-portal.md) · [MSD-03 · OpenAPI](03-openapi.md)

---

## 1 · Filosofía

Toda integración debe poder desarrollarse **sin acceder a un entorno productivo**.

El Sandbox replica el comportamiento de la API oficial utilizando **datos de demostración** y **aislamiento multi-tenant**.

```
Developer
      │
      ▼
Developer Portal
      │
      ▼
 API Explorer
      │
      ▼
   Sandbox
      │
      ▼
  MAG v1
```

El comportamiento funcional debe ser **equivalente** al de producción — mismos endpoints, mismos códigos de error, mismo envelope JSON.

| Producción | Sandbox |
|------------|---------|
| Datos reales de clientes | Datos ficticios |
| Integraciones externas | Deshabilitadas |
| SLA completo | Rate limit reducido |
| Persistencia indefinida | Reinicio periódico |

---

## 2 · Objetivos

El Sandbox permite:

- aprender la API
- probar autenticación JWT
- consumir recursos REST
- validar SDK
- probar la CLI
- generar ejemplos
- realizar pruebas automatizadas

**Nunca** debe utilizar información real de clientes.

---

## 3 · Tenant de demostración

**Tenant oficial:**

```
empresa-demo
```

| Recurso | Estado |
|---------|--------|
| **Activos** | Datos de ejemplo |
| **Inventario** | Datos de ejemplo |
| **Órdenes de trabajo** | Datos de ejemplo |
| **Compras** | Datos de ejemplo |
| **Usuarios** | Limitados |
| **Auditoría** | Simulada |

Los datos pueden **reiniciarse periódicamente** — los integradores no deben asumir persistencia a largo plazo.

→ [MAG-03 · Multi-tenant](/mag/chapters/03-multi-tenant.md)

**Entorno local (desarrollo):**

```powershell
python run.py
# Tenant demo según seed de la base de datos local
```

**Producción sandbox (planificado):** `https://sandbox.api.roustix.app/api/v1` o tenant `empresa-demo` en API compartida con aislamiento estricto.

---

## 4 · API Explorer

El Portal para Desarrolladores incorpora un **explorador interactivo** basado en [OpenAPI 3.1](03-openapi.md).

```http
GET /api/v1/maintenance/assets
```

**Funciones:**

- editar parámetros
- ejecutar solicitudes
- visualizar respuestas
- copiar ejemplos
- generar código

El Explorer consume **`openapi.v1.yaml`** — no definiciones duplicadas.

| URL | Rol |
|-----|-----|
| `/msd/` → sección Sandbox | Acceso desde portal |
| OpenAPI spec | `/api/v1/openapi.json` |

---

## 5 · Autenticación

El Sandbox utiliza el mismo flujo definido en [MAG-02](/mag/chapters/02-autenticacion-jwt.md):

```http
POST /api/v1/auth/login
```

**Credenciales de demostración** (publicadas únicamente en el Developer Portal):

| Campo | Valor demo |
|-------|------------|
| Usuario | *(publicado en portal)* |
| Contraseña | *(publicado en portal)* |
| Empresa | `empresa-demo` |

```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"***","empresa_slug":"empresa-demo"}'
```

**Legacy hoy:** `POST /api/auth/login`

Las credenciales oficiales **nunca** se incluyen en el repositorio — solo en el portal o documentación controlada.

---

## 6 · Datos de ejemplo

Cada módulo incluye información **representativa** del contrato MAG:

```
Maintenance
├── Assets
├── Work Orders
├── Lubrication
└── Schedules

Inventory
├── Products
├── Stock
└── Movements
```

Todos los ejemplos siguen el contrato [MAG-04](/mag/chapters/04-recursos.md) y convenciones [MAG-05](/mag/chapters/05-convenciones-nombres.md).

**Ejemplo — activos demo:**

```json
{
  "data": [
    {
      "asset_id": 1,
      "asset_code": "M-001",
      "name": "Compresor A",
      "status": "operational",
      "critical": true
    }
  ],
  "meta": {
    "pagination": { "page": 1, "page_size": 50, "total": 3 }
  }
}
```

---

## 7 · Limitaciones

El Sandbox posee **restricciones deliberadas**:

| Restricción | Motivo |
|-------------|--------|
| Sin envío de correos reales | Seguridad |
| Sin integraciones externas | Aislamiento |
| Datos reiniciables | Consistencia |
| Rate limit reducido | Protección |
| Sin información sensible | Privacidad |

→ [MAG-10 · Límites](/mag/chapters/10-limites-buenas-practicas.md)

---

## 8 · Generación de ejemplos

El Explorer permite ejecutar cualquier endpoint documentado.

**Ejemplo:**

```http
GET /api/v1/me
```

Respuesta inmediata en el navegador.

También genera ejemplos para:

| Lenguaje | Origen |
|----------|--------|
| **cURL** | OpenAPI operation |
| **Python** | SDK / requests |
| **JavaScript** | fetch / SDK |
| **PHP** | SDK |

Utilizando **OpenAPI como fuente** ([MSD-03](03-openapi.md)).

---

## 9 · Casos de uso

El Sandbox está pensado para:

| Audiencia | Uso |
|-----------|-----|
| **Desarrolladores** | Primera integración |
| **Partners** | Validación de conectores |
| **Consultores** | POC rápidos |
| **Integradores** | Pruebas de contrato |
| **Capacitación** | Formación interna |
| **Demostraciones comerciales** | MCM · ventas |

> **Nota:** el Sandbox **no sustituye** un entorno de staging corporativo del cliente.

Herramientas complementarias:

- [MSD-04 · SDK](04-sdk-oficiales.md) — pruebas desde código
- [MSD-05 · CLI](05-cli.md) — pruebas desde terminal
- [MSD-08 · Colecciones](08-colecciones.md) — Postman · Insomnia

---

## 10 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Utilizar Sandbox **antes** de Producción |
| 2 | No almacenar datos importantes en el tenant demo |
| 3 | Asumir reinicio periódico de la información |
| 4 | Validar integraciones con OpenAPI |
| 5 | Utilizar siempre JWT |
| 6 | No depender de IDs específicos entre sesiones |
| 7 | Probar errores MAG-06 con respuestas simuladas (roadmap) |

---

## 11 · Roadmap

Próximas funcionalidades:

- datos de prueba personalizables
- reinicio automático del tenant (`POST /sandbox/reset`)
- colecciones Postman integradas en el Explorer
- API Explorer avanzado (historial · entornos)
- **Mock Server** (Prism) para desarrollo offline
- pruebas de Webhooks ([MAG-08](/mag/chapters/08-webhooks.md))
- simulación de errores MAG-06
- escenarios completos por módulo (maintenance · inventory · sales)

| Fase | Entrega |
|------|---------|
| **Fase 0** ✅ | Especificación MSD-06 · tenant `empresa-demo` documentado |
| **Fase 1** | Sección Sandbox en `/msd/` |
| **Fase 2** | API Explorer UI desde OpenAPI |
| **Fase 3** | Sandbox API dedicado · reset programado |

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MSD-02 · Developer Portal](02-developer-portal.md) | Acceso al Sandbox |
| [MSD-03 · OpenAPI](03-openapi.md) | Base del Explorer |
| [MSD-04 · SDK](04-sdk-oficiales.md) | Ejemplos ejecutables |
| [MSD-05 · CLI](05-cli.md) | Pruebas desde terminal |
| [MAG-02 · JWT](/mag/chapters/02-autenticacion-jwt.md) | Inicio de sesión |
| [MAG-04 · Recursos](/mag/chapters/04-recursos.md) | Recursos disponibles |
| [MAG-06 · Errores](/mag/chapters/06-manejo-errores.md) | Simulación de errores |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Existe un Sandbox oficial accesible desde el Developer Portal
- [ ] Se dispone de un tenant `empresa-demo` operativo
- [ ] El API Explorer consume la especificación OpenAPI
- [ ] Los ejemplos pueden ejecutarse directamente desde la documentación
- [ ] Los datos del Sandbox están completamente aislados de Producción
- [ ] Se ofrecen ejemplos en cURL, Python, JavaScript y PHP
- [ ] El entorno puede reiniciarse sin afectar integraciones reales

**Especificación:** ✅ · **Sandbox + Explorer en producción:** 📋 pendiente

---

## Filosofía del capítulo

El Sandbox convierte la documentación en una **experiencia interactiva**. Un desarrollador no solo lee cómo funciona la API: la **prueba**, experimenta con ella y valida su integración antes de escribir una sola línea de código para producción.

**MSD-06 establece el entorno oficial de experimentación de Roustix**, garantizando que cualquier integración pueda desarrollarse de forma segura, repetible y alineada con el contrato definido por MAG.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Sandbox** | 📋 Planificado |
| **API Explorer** | 📋 Basado en OpenAPI 3.1 |
| **Tenant demo** | 📋 `empresa-demo` |
| **Implementación** | 📋 Pendiente |
| **Siguiente capítulo** | [MSD-07 · Quick Start](07-quick-start.md) |

---

→ [MSD-07-QS · Quick Start y guías](07-quick-start.md)
