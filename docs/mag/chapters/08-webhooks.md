# MAG-08-HOOK · Webhooks

**Código:** MAG-08-HOOK · Sprint 8.8 · **Entregado**

> La mejor API responde cuando se le consulta. Una gran plataforma también sabe avisar cuando algo ocurre.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir el **estándar oficial de Webhooks Roustix** — el mecanismo mediante el cual la plataforma notifica eventos a sistemas externos en **tiempo real**.

Mientras la API REST ([MAG-04](04-recursos.md)) funciona bajo **request → response**, los Webhooks permiten que Roustix **inicie la comunicación** cuando ocurre un evento de negocio.

Los Webhooks forman parte del **contrato público** y utilizan el mismo modelo de autenticación, versionado y nomenclatura definido en MAG.

---

## 1 · Filosofía

**REST responde. Webhooks notifican.**

```
Cliente                    Roustix
   │                          │
   │  GET /assets             │
   │ ───────────────────────► │
   │ ◄─────────────────────── │
   │     response             │
```

vs

```
Orden creada
      │
      ▼
  Roustix
      │
 POST Webhook
      │
      ▼
Sistema externo
```

El objetivo es eliminar consultas periódicas (**polling**) innecesarias.

---

## 2 · Arquitectura

```
Evento de negocio
        │
        ▼
Módulo Roustix
        │
        ▼
Event Dispatcher
        │
        ▼
Firma HMAC
        │
        ▼
HTTP POST
        │
        ▼
Endpoint del cliente
```

Los eventos son generados por los módulos de negocio y enviados por un **único servicio de Webhooks**.

**Implementación prevista:** `app/platform/webhooks/`

---

## 3 · Registro de Webhooks

Cada tenant puede registrar uno o varios endpoints.

```http
POST /api/v1/admin/webhooks
Authorization: Bearer <token>
Content-Type: application/json
```

```json
{
  "url": "https://empresa.com/webhooks/roustix",
  "events": [
    "work_order.created",
    "stock.low"
  ]
}
```

**Respuesta:**

```json
{
  "data": {
    "id": 18,
    "status": "active"
  },
  "meta": {
    "api_version": "v1"
  }
}
```

El `secret` para HMAC se genera en el registro y se muestra **una sola vez** (roadmap: rotación en panel admin).

---

## 4 · Eventos oficiales

Todos los nombres siguen [MAG-05](05-convenciones-nombres.md):

- inglés
- `snake_case` en payload
- eventos en **dot notation** (`resource.action`)

### Maintenance

| Evento | Estado |
|--------|--------|
| `asset.created` | 📋 |
| `asset.updated` | 📋 |
| `work_order.created` | 📋 |
| `work_order.updated` | 📋 |
| `work_order.closed` | 📋 |

### Inventory

| Evento | Estado |
|--------|--------|
| `product.created` | 📋 |
| `product.updated` | 📋 |
| `stock.updated` | 📋 |
| `stock.low` | 📋 |
| `movement.created` | 📋 |

### Platform

| Evento | Estado |
|--------|--------|
| `tenant.created` | 📋 |
| `user.created` | 📋 |
| `subscription.updated` | 📋 |
| `plan.changed` | 📋 |

Nuevos eventos → documentar aquí **antes** de implementar.

---

## 5 · Payload estándar

Todo webhook utiliza **exactamente** la misma estructura:

```json
{
  "event": "work_order.created",
  "timestamp": "2026-07-10T18:30:00Z",
  "tenant": {
    "id": 4,
    "slug": "empresa-xyz"
  },
  "data": {
    "work_order_id": 128,
    "asset_id": 15,
    "status": "open"
  }
}
```

| Campo | Descripción |
|-------|-------------|
| **`event`** | Tipo de evento (dot notation) |
| **`timestamp`** | ISO 8601 UTC |
| **`tenant`** | Tenant origen (`id`, `slug`) |
| **`data`** | Información del recurso afectado |

Claves en **inglés** — envelope alineado con MAG-04/MAG-05.

---

## 6 · Firma de seguridad

Cada entrega incluye:

```http
X-Roustix-Timestamp: 1784664930
X-Roustix-Signature: v1=6f9c...
```

| Aspecto | Valor |
|---------|-------|
| Algoritmo | **HMAC-SHA256** |
| Secreto | Compartido en registro del webhook |
| Input | `timestamp + "." + raw body JSON` |

```
Payload JSON
        │
        ▼
HMAC(secret)
        │
        ▼
SHA256
        │
        ▼
Header Signature
```

El receptor **debe** validar la firma en tiempo constante y rechazar timestamps
con más de cinco minutos de diferencia antes de procesar el evento.

→ [MPA-07 · Seguridad](/mpa/chapters/07-seguridad.md)

---

## 7 · Reintentos

| Respuesta cliente | Acción |
|-------------------|--------|
| **2xx** | Entregado · no reintentar |
| **5xx** · timeout · network error | Reintento automático |
| **408**, **425**, **429** | Reintentar; respetar `Retry-After` acotado |
| Otros **4xx** | **No** reintentar · marcar fallo |

| Intento | Espera |
|---------|--------|
| 1 | Inmediato |
| 2 | 1 minuto |
| 3 | 5 minutos |
| 4 | 15 minutos |
| 5 | 1 hora |

Tras el intento 5 → estado **`FAILED`** · registrado · notificación al admin del tenant (roadmap).

---

## 8 · Idempotencia

Cada evento posee un identificador único:

```http
X-Roustix-Event-Id: 6a1d92b4-8c3e-4f1a-9d2b-1e7f8a9b0c1d
```

El cliente debe almacenar ese ID para **no procesar dos veces** el mismo evento. Esto permite reintentos seguros.

---

## 9 · Versionado

Los Webhooks siguen la versión de la API: **v1**.

**No** incluyen versión en el nombre del evento.

| ✅ Correcto | ❌ Incorrecto |
|------------|--------------|
| `work_order.created` | `v1.work_order.created` |

Cambios incompatibles de payload → política [MAG-07](07-versionado.md).

---

## 10 · Ejemplo completo

**Evento:** OT creada

```http
POST https://empresa.com/webhooks/roustix
Content-Type: application/json
X-Roustix-Signature: sha256=...
X-Roustix-Timestamp: 1784664930
X-Roustix-Event-Id: 89fd...
```

```json
{
  "event": "work_order.created",
  "timestamp": "2026-07-10T18:30:00Z",
  "tenant": {
    "id": 4,
    "slug": "empresa-xyz"
  },
  "data": {
    "work_order_id": 128,
    "status": "open"
  }
}
```

**Respuesta esperada del cliente:** `HTTP 200 OK` (≤ 5 s)

Errores de validación del endpoint receptor → fuera de alcance MAG; Roustix solo registra HTTP status.

---

## 11 · Auditoría

Todos los envíos quedan registrados.

**Información almacenada:**

- evento
- tenant
- endpoint URL
- fecha
- respuesta HTTP
- tiempo de respuesta
- cantidad de reintentos
- `X-Roustix-Event-Id`

**No se almacena** información sensible del payload cuando el plan de retención lo prohíba.

Alineado con [MAG-06 · Auditoría de errores](06-manejo-errores.md) y MPA-07.

---

## 12 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Validar siempre `X-Roustix-Signature` |
| 2 | Responder rápidamente (≤ 5 s) |
| 3 | Procesar de forma asíncrona cuando sea posible |
| 4 | Implementar idempotencia usando `X-Roustix-Event-Id` |
| 5 | No depender del orden de llegada de los eventos |
| 6 | Responder **2xx** únicamente cuando el evento haya sido **aceptado** |
| 7 | Registrar errores para facilitar soporte |

---

## 13 · Roadmap

Implementaciones futuras:

- reenvío manual desde el panel
- historial de entregas
- filtros avanzados por módulo
- firma rotativa de secretos
- múltiples endpoints por entorno (test / production)
- cola de eventos distribuida

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MAG-04 · Recursos REST](04-recursos.md) | Recursos que generan eventos |
| [MAG-05 · Convenciones](05-convenciones-nombres.md) | Nombres de eventos y payload |
| [MAG-06 · Errores](06-manejo-errores.md) | Validación registro webhook |
| [MAG-07 · Versionado](07-versionado.md) | Evolución del contrato |
| [MPA-06 · Integraciones](/mpa/chapters/06-integraciones.md) | Arquitectura general |
| [MPA-07 · Seguridad](/mpa/chapters/07-seguridad.md) | HMAC y auditoría |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Existe un servicio centralizado de Webhooks
- [ ] Todos los eventos siguen la nomenclatura oficial
- [ ] Todos los payloads utilizan el formato estándar
- [ ] Los Webhooks incluyen firma `X-Roustix-Signature`
- [ ] Se implementan reintentos automáticos para errores temporales
- [ ] Todos los envíos quedan auditados
- [ ] La documentación y el código utilizan el mismo catálogo de eventos

---

## Filosofía del capítulo

Una integración moderna no espera a que el cliente pregunte qué ocurrió. La plataforma informa los cambios **en el momento en que suceden**, de forma segura, verificable y predecible.

**MAG-08 convierte a Roustix en una plataforma orientada a eventos**, preparada para integrarse con ERP, CRM, Power BI, plataformas de mensajería y futuros servicios distribuidos.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato** | ✅ Definido |
| **Implementación actual** | 🟡 Contrato Sprint 22.0 · código previsto en 22.3 |
| **Seguridad** | HMAC-SHA256 · `X-Roustix-Signature` |
| **Compatibilidad** | API REST v1 |
| **Siguiente capítulo** | [MAG-09 · Ejemplos y SDK](09-ejemplos.md) |

---

→ [MAG-09-EX · Ejemplos y SDK](09-ejemplos.md)
