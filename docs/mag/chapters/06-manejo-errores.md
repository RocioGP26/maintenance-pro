# MAG-06-ERR · Manejo de errores

**Código:** MAG-06-ERR · Sprint 8.6 · **Entregado**

> Los errores también forman parte del contrato.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir el **formato oficial** de manejo de errores de Maintix.

Un error nunca debe depender del framework, de SQLAlchemy ni del servidor. El cliente siempre recibe una respuesta **consistente**, independientemente del módulo.

MAG-06 establece el contrato que utilizarán la aplicación web, las integraciones, el **SDK oficial** y futuros clientes móviles.

**Convenciones de códigos:** [MAG-05 · §10 Errores](05-convenciones-nombres.md#10--errores).

---

## 1 · Filosofía

Un error debe responder tres preguntas:

1. **¿Qué ocurrió?** → `error.code`
2. **¿Por qué ocurrió?** → `message` + `details`
3. **¿Qué puede hacer el desarrollador ahora?** → HTTP status + código estable

Nunca debe exponer detalles internos del servidor.

---

## 2 · Formato oficial

Todas las respuestas de error utilizan **exactamente** la misma estructura:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Activo no encontrado",
    "details": {}
  }
}
```

| Campo | Descripción |
|-------|-------------|
| **`code`** | Código estable para programación · `UPPER_SNAKE_CASE` |
| **`message`** | Mensaje legible en español (MUX) |
| **`details`** | Información adicional opcional |

El cliente **nunca** debe interpretar el texto de `message`. Siempre debe utilizar **`error.code`**.

**Legacy:** muchos endpoints devuelven `{"error": "mensaje"}` — convergencia planificada hacia este formato.

---

## 3 · Códigos HTTP

Maintix utiliza únicamente códigos HTTP estándar.

| HTTP | Uso |
|------|-----|
| **200** | OK |
| **201** | Recurso creado |
| **204** | Sin contenido |
| **400** | Solicitud inválida |
| **401** | No autenticado |
| **403** | Sin permisos |
| **404** | Recurso inexistente |
| **409** | Conflicto |
| **422** | Validación |
| **429** | Rate limit |
| **500** | Error interno |
| **503** | Servicio temporalmente no disponible |

---

## 4 · Catálogo oficial de errores

Todos los códigos siguen [MAG-05](05-convenciones-nombres.md): **`UPPER_SNAKE_CASE`**.

### Autenticación

| Código | HTTP típico |
|--------|-------------|
| `INVALID_TOKEN` | 401 |
| `TOKEN_EXPIRED` | 401 |
| `LOGIN_FAILED` | 401 |
| `USER_DISABLED` | 403 |
| `SESSION_EXPIRED` | 401 |

### Permisos

| Código | HTTP típico |
|--------|-------------|
| `PERMISSION_DENIED` | 403 |
| `MODULE_NOT_ENABLED` | 403 |
| `PLAN_NOT_ALLOWED` | 403 |
| `TENANT_SUSPENDED` | 403 |

### Recursos

| Código | HTTP típico |
|--------|-------------|
| `RESOURCE_NOT_FOUND` | 404 |
| `RESOURCE_ALREADY_EXISTS` | 409 |
| `RESOURCE_CONFLICT` | 409 |

### Validación

| Código | HTTP típico |
|--------|-------------|
| `VALIDATION_ERROR` | 422 |
| `INVALID_PARAMETER` | 400 |
| `INVALID_REQUEST` | 400 |

### Plataforma

| Código | HTTP típico |
|--------|-------------|
| `INTERNAL_ERROR` | 500 |
| `DATABASE_ERROR` | 500 |
| `SERVICE_UNAVAILABLE` | 503 |
| `RATE_LIMIT_EXCEEDED` | 429 |

Nuevos códigos → documentar aquí **antes** de implementar (MAG-05 §13).

---

## 5 · Ejemplos

### 404

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Activo no encontrado"
  }
}
```

### 401

```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Token inválido"
  }
}
```

### 403

```json
{
  "error": {
    "code": "MODULE_NOT_ENABLED",
    "message": "El módulo Inventory no está habilitado para esta empresa"
  }
}
```

### 422

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Existen errores de validación",
    "details": {
      "name": [
        "Este campo es obligatorio."
      ]
    }
  }
}
```

---

## 6 · Validaciones

Cuando existen varios errores de validación:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Hay errores en la solicitud",
    "details": {
      "asset_code": [
        "Ya existe."
      ],
      "name": [
        "Campo obligatorio."
      ]
    }
  }
}
```

El cliente puede mostrar cada error directamente. Claves en `details` → `snake_case` inglés (MAG-05).

---

## 7 · Errores multi-tenant

Si un recurso pertenece a otra empresa:

```http
GET /api/v1/maintenance/assets/52
```

**Respuesta:** **404** · `RESOURCE_NOT_FOUND`

**Nunca 403** — el recurso no debe revelar su existencia.

→ [MAG-03 · Multi-tenant](03-multi-tenant.md)

---

## 8 · Errores internos

**Nunca devolver:**

- Stack trace
- SQL
- Flask exception
- SQLAlchemy exception
- Rutas internas
- Nombres de tablas

| ❌ Incorrecto |
|--------------|
| `sqlalchemy.exc.NoResultFound...` |

| ✅ Correcto |
|------------|
| `{ "error": { "code": "INTERNAL_ERROR", "message": "Ha ocurrido un error interno." } }` |

El detalle completo queda **únicamente en los logs** de la plataforma.

---

## 9 · Correlation ID

Todas las respuestas pueden incluir:

```http
X-Request-Id: 6c1d0d82-b6d8-46db-a5db-924d9d79c06d
```

El cliente puede enviar su propio UUID; el servidor lo propaga o genera uno.

Si el cliente reporta un problema, soporte localiza exactamente la petición.

---

## 10 · Ejemplo completo

**Solicitud:**

```http
GET /api/v1/maintenance/assets/900
Authorization: Bearer <token>
```

```
JWT válido
     ↓
Tenant resuelto
     ↓
Activo inexistente
     ↓
404
```

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Activo no encontrado"
  }
}
```

---

## 11 · Errores y auditoría

Todos los errores relevantes quedan registrados en la plataforma.

**Se registran:**

- usuario
- tenant (`empresa_id`)
- endpoint
- código HTTP
- `error.code`
- fecha
- `request_id`

**Nunca:** contraseña · token · datos sensibles

→ [MPA-07 · Seguridad](/mpa/chapters/07-seguridad.md)

---

## 12 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Utilizar siempre `error.code` |
| 2 | No analizar el texto de `message` |
| 3 | Nunca exponer excepciones internas |
| 4 | Mantener códigos estables entre versiones |
| 5 | Registrar errores en auditoría |
| 6 | Toda respuesta de error sigue el mismo formato |
| 7 | Documentar nuevos códigos antes de implementarlos |

### Integradores

- Reintentar **solo** `429` y `503` con backoff exponencial
- No reintentar 4xx excepto `429`
- Incluir `X-Request-Id` en reportes a soporte

---

## 13 · Webhooks

Las respuestas de verificación de endpoint webhook usan el mismo formato `error`. Ver [MAG-08](08-webhooks.md).

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MAG-02 · Autenticación JWT](02-autenticacion-jwt.md) | Errores de autenticación |
| [MAG-03 · Multi-tenant](03-multi-tenant.md) | Errores cross-tenant · 404 |
| [MAG-05 · Convenciones](05-convenciones-nombres.md) | Formato de códigos |
| [MAG-07 · Versionado](07-versionado.md) | Compatibilidad del contrato |
| [MPA-07 · Seguridad](/mpa/chapters/07-seguridad.md) | Auditoría y registros |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Todas las respuestas de error utilizan el objeto `error`
- [ ] Todos los códigos siguen `UPPER_SNAKE_CASE`
- [ ] Ningún endpoint devuelve excepciones internas
- [ ] Los errores de validación utilizan `details`
- [ ] Los recursos cross-tenant responden **404**
- [ ] Todas las respuestas incluyen `X-Request-Id` cuando esté disponible
- [ ] El catálogo oficial de errores está centralizado y reutilizado por todos los módulos

---

## Filosofía del capítulo

Los errores también son una **interfaz**. Un contrato consistente permite que personas, SDKs e integraciones reaccionen de forma predecible, independientemente del módulo o de la implementación interna.

**MAG-06 convierte el manejo de errores en parte del contrato público de Maintix**, garantizando estabilidad para todos los clientes de la API.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato** | ✅ Definido |
| **Implementación actual** | 🟡 Parcial (respuestas legacy `{"error": "..."}`) |
| **Compatibilidad** | JWT v1 · REST v1 |
| **Siguiente capítulo** | [MAG-07 · Versionado](07-versionado.md) |

---

→ [MAG-07-VER · Versionado](07-versionado.md)
