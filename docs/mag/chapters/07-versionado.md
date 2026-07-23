# MAG-07-VER · Versionado

> Una API cambia. El contrato no se rompe.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir la **estrategia oficial de versionado** de la API Roustix, garantizando que las integraciones existentes continúen funcionando mientras la plataforma evoluciona.

El objetivo del versionado no es permitir múltiples APIs diferentes, sino ofrecer una **evolución controlada** del contrato público.

MAG-07 establece las reglas para introducir cambios, retirar endpoints legacy y mantener la compatibilidad entre versiones.

---

## 1 · Filosofía

Una integración representa una **inversión**. Por esa razón:

- una actualización **nunca** debe romper clientes existentes dentro de la misma versión;
- los cambios incompatibles requieren una **nueva versión** (`/api/v2/`);
- los cambios compatibles pueden incorporarse dentro de **`/api/v1`**.

El contrato evoluciona de forma **predecible**.

---

## 2 · Estrategia oficial

Roustix versiona la API mediante la **URL**:

```
/api/v1/
```

Ejemplos:

```http
GET /api/v1/me
GET /api/v1/maintenance/assets
POST /api/v1/auth/login
```

**No se utiliza** versionado mediante:

- headers (`Accept-Version`, etc.)
- query string (`?version=1`)
- media types (`application/vnd.roustix.v1+json`)

→ [MAG-05 · §11 Versionado](05-convenciones-nombres.md#11--versionado)

---

## 3 · Versiones soportadas

| Versión | Estado |
|---------|--------|
| **Legacy** (`/api/*` sin `v1`) | Compatibilidad temporal |
| **v1** | Contrato oficial |
| **v2** | Roadmap |

La documentación MAG hace referencia **únicamente a v1** como contrato público activo.

---

## 4 · Compatibilidad

Una versión mayor garantiza **estabilidad**.

Dentro de `/api/v1` **se permiten**:

- nuevos endpoints
- nuevos campos opcionales en respuestas
- nuevos recursos
- nuevos módulos (`/api/v1/crm`, …)

**No se permite** dentro de v1:

- eliminar campos existentes
- cambiar significado de un campo
- modificar códigos HTTP de un endpoint documentado
- cambiar formatos de respuesta (`data`/`error` envelope)

---

## 5 · Cambios compatibles

### Agregar campo opcional

```json
{
  "data": {
    "asset_id": 25,
    "name": "Compressor B",
    "critical": true
  }
}
```

Los clientes anteriores **continúan funcionando** — ignoran campos desconocidos.

### Agregar endpoint

```http
GET /api/v1/maintenance/history
```

No afecta integraciones existentes.

### Agregar módulo

```
/api/v1/crm
```

No rompe el contrato v1.

---

## 6 · Cambios incompatibles

Requieren **`/api/v2/`**.

| Cambio | Ejemplo |
|--------|---------|
| Renombrar campo | `name` → `asset_name` |
| Eliminar campo | quitar `status` |
| Cambiar semántica HTTP | `404` → `200` para mismo caso |
| Cambiar ruta de recurso | `/maintenance/assets` → `/assets` |

Todos estos cambios requieren nueva versión mayor de API.

---

## 7 · Legacy

Actualmente existen endpoints **sin versión** en el código:

| Legacy | v1 |
|--------|-----|
| `/api/auth/login` | `/api/v1/auth/login` |
| `/api/me` | `/api/v1/me` |
| `/api/activos` | `/api/v1/maintenance/assets` |
| `/api/admin/resumen` | `/api/v1/admin/summary` |

Durante el período de transición **ambos** permanecen disponibles.

MAG documenta ambos hasta completar migración. Árbol oficial → [MAG-04](04-recursos.md).

---

## 8 · Deprecation

Los endpoints legacy deben responder con headers de deprecación:

```http
Deprecation: true
Sunset: Wed, 31 Dec 2026 23:59:59 GMT
Link: </api/v1/maintenance/assets>; rel="successor-version"
```

Esto permite que los clientes detecten automáticamente que existe una ruta más reciente.

**Periodo mínimo** de convivencia: **6 meses** entre anuncio y `Sunset`.

---

## 9 · Política de soporte

| Versión | Soporte |
|---------|---------|
| **Legacy** | Temporal · headers `Deprecation` |
| **v1** | Activo · contrato MAG |
| **v2** | Futuro |

Una versión solo puede retirarse cuando:

1. Existe una versión sucesora documentada
2. OpenAPI de la nueva versión está publicado
3. El período de migración ha finalizado

---

## 10 · Evolución del contrato

```
Legacy (/api/*)
    │
    ▼
/api/v1  ← contrato oficial
    │
    ▼
Mejoras compatibles (campos, endpoints, módulos)
    │
    ▼
/api/v2  ← solo breaking changes
```

El objetivo es mantener **una única versión activa** durante el mayor tiempo posible.

---

## 11 · OpenAPI

Cada versión publica su **propio** documento OpenAPI:

```
/api/v1/openapi.json
```

Documentación humana:

```
/docs/api/v1
```

Nunca compartirán el mismo esquema entre v1 y v2.

**MAG-04** es la fuente oficial para generar `openapi.v1.yaml` · SDK Sprint 9.

---

## 12 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Versionar únicamente en la URL |
| 2 | No romper contratos dentro de una versión |
| 3 | Agregar antes que reemplazar |
| 4 | Utilizar headers `Deprecation` y `Sunset` |
| 5 | Mantener documentación sincronizada con código |
| 6 | Publicar OpenAPI por versión |
| 7 | Avisar cambios incompatibles antes de retirar endpoints |

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MAG-04 · Recursos REST](04-recursos.md) | Árbol de recursos v1 |
| [MAG-05 · Convenciones](05-convenciones-nombres.md) | Nombres estables |
| [MAG-06 · Errores](06-manejo-errores.md) | Contrato de respuestas |
| [MAG-08 · Webhooks](08-webhooks.md) | Versionado de eventos |
| [MPA-06 · Integraciones](/mpa/chapters/06-integraciones.md) | Estrategia de integración |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Toda la API pública utiliza `/api/v1`
- [ ] Los endpoints legacy publican headers `Deprecation`
- [ ] Existe una política oficial para cambios incompatibles (este documento)
- [ ] OpenAPI se publica por versión (`/api/v1/openapi.json`)
- [ ] Ningún cambio rompe clientes dentro de la misma versión
- [ ] La documentación y el código utilizan la misma versión

---

## Filosofía del capítulo

Una API estable permite que las integraciones duren **años**. El versionado protege esa estabilidad, haciendo posible que Roustix evolucione sin obligar a sus clientes a reescribir integraciones en cada actualización.

**MAG-07 define el ciclo de vida del contrato público de Roustix** — compatibilidad, migraciones controladas y evolución predecible.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato** | ✅ Definido |
| **Implementación actual** | 🟡 Migración legacy → `/api/v1` |
| **Compatibilidad** | Legacy + REST v1 |
| **Siguiente capítulo** | [MAG-08 · Webhooks](08-webhooks.md) |

---

→ [MAG-08-HOOK · Webhooks](08-webhooks.md)
