# MAG-10-LIM · Límites y buenas prácticas

**Código:** MAG-10-LIM · Sprint 8.10 · **Entregado**

> Una API rápida no es suficiente. Debe ser **estable, segura y predecible**.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Definir las **políticas oficiales** de uso responsable, límites operativos y buenas prácticas para consumir la API de Roustix.

Este capítulo **cierra la especificación MAG v1.0**, consolidando las reglas que deben seguir integradores, SDKs y futuros clientes móviles para garantizar una plataforma escalable y confiable.

---

## 1 · Filosofía

La API de Roustix es un **recurso compartido** entre miles de empresas.

Por ello, todas las integraciones deben:

- respetar los límites establecidos
- minimizar llamadas innecesarias
- manejar errores de forma adecuada
- mantener compatibilidad con futuras versiones

Una buena integración consume la API de forma **eficiente, no agresiva**.

---

## 2 · Rate Limiting

Para proteger la plataforma se aplican límites por **IP**, **usuario** y **tenant**.

| Endpoint | Límite |
|----------|--------|
| Login | 5 intentos / 15 min |
| API autenticada | 120 solicitudes / minuto (valor inicial) |
| Webhooks | Sin límite de recepción |
| Exportaciones | Según plan contratado |

Cuando se supera un límite:

```http
HTTP/1.1 429 Too Many Requests
```

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Se ha excedido el límite de solicitudes."
  }
}
```

El servidor puede incluir:

```http
Retry-After: 60
```

→ [MAG-06 · `RATE_LIMIT_EXCEEDED`](06-manejo-errores.md)

**Implementación hoy:**

| Endpoint | Estado |
|----------|--------|
| `POST /api/auth/login` | ✅ 5 / 15 min por IP (`@limiter`) |
| API autenticada general | 📋 Planificado (120 / min) |
| Exportaciones por plan | 📋 Planificado |

**Legacy hoy:** login en `/api/auth/login` — contrato v1: `/api/v1/auth/login` ([MAG-07](07-versionado.md)).

---

## 3 · Timeouts

Los clientes deben configurar tiempos de espera razonables.

| Operación | Recomendado |
|-----------|-------------|
| Lectura | 10 s |
| Escritura | 30 s |
| Exportaciones | 60 s |
| Webhooks | 5 s |

**Nunca esperar indefinidamente.**

---

## 4 · Reintentos

Solo deben reintentarse **errores temporales**.

| Código | Reintentar |
|--------|------------|
| **429** | ✅ Sí |
| **503** | ✅ Sí |
| **Timeout** | ✅ Sí |
| **500** | ⚠️ Opcional |
| **400** | ❌ No |
| **401** | ❌ No |
| **403** | ❌ No |
| **404** | ❌ No |
| **422** | ❌ No |

Se recomienda **backoff exponencial**.

Ejemplo:

```
1 s → 2 s → 4 s → 8 s → 16 s
```

Respetar el header `Retry-After` cuando esté presente.

→ [MAG-06 · Reintentos](06-manejo-errores.md)

---

## 5 · Paginación

Nunca solicitar listas completas cuando existan múltiples páginas.

**Correcto:**

```http
GET /api/v1/inventory/products?page=1&page_size=50
```

**Incorrecto:**

```http
GET /api/v1/inventory/products?page_size=100000
```

**Límite máximo permitido:**

```
page_size = 200
```

Para volúmenes grandes usar exportaciones (MRL) en lugar de paginación masiva.

→ [MAG-04 · Paginación](04-recursos.md)

---

## 6 · Caché

Los datos que cambian poco pueden almacenarse temporalmente.

**Ejemplos cacheables:**

- activos
- productos
- sedes
- usuarios

**No deben almacenarse en caché:**

- permisos
- autenticación
- stock crítico
- órdenes activas

Cuando el recurso incluya **`ETag`** o **`Last-Modified`**, el cliente debería utilizarlos.

Incluir siempre la clave de tenant (`empresa_id` / slug) en la clave de caché del cliente.

---

## 7 · Seguridad

Toda integración debe:

- utilizar **HTTPS** en producción
- proteger el **JWT**
- validar certificados
- renovar tokens expirados
- verificar firmas de Webhooks

**Nunca:**

- almacenar tokens en texto plano
- compartir un mismo JWT entre empresas
- enviar credenciales por URL

→ [MAG-02 · JWT](02-autenticacion-jwt.md) · [MAG-08 · Webhooks](08-webhooks.md)

---

## 8 · Diseño de clientes

Los clientes oficiales deben:

- reutilizar conexiones HTTP
- centralizar autenticación
- registrar **`X-Request-Id`**
- encapsular el manejo de errores
- utilizar el **SDK oficial** cuando exista

**No construir URLs manualmente.**

→ [MAG-09 · SDK](../../sdk/README.md)

---

## 9 · Observabilidad

Toda integración debería registrar:

- endpoint
- método HTTP
- tiempo de respuesta
- código HTTP
- `error.code`
- `X-Request-Id`

**Ejemplo:**

```
GET /maintenance/assets
200
152 ms
Request ID: 6c1d0d82...
```

Esto facilita el diagnóstico junto con el equipo de soporte.

---

## 10 · Compatibilidad

Los clientes deben asumir que pueden aparecer:

- nuevos campos JSON
- nuevos recursos
- nuevos módulos
- nuevos códigos opcionales

**No deben fallar** ante propiedades desconocidas.

Solo deben **utilizar los campos documentados**.

→ [MAG-07 · Versionado](07-versionado.md)

---

## 11 · Integraciones recomendadas

Roustix está diseñado para integrarse con:

| Plataforma | Estado |
|------------|--------|
| **Power BI** | 📋 |
| **Excel** | ✅ |
| **ERP** | 📋 |
| **CRM** | 📋 |
| **Zapier** | Roadmap |
| **Make** | Roadmap |
| **n8n** | Roadmap |
| **Microsoft Power Automate** | Roadmap |

Todas las integraciones utilizan el **contrato MAG**.

→ [MPA-06 · Integraciones](/mpa/chapters/06-integraciones.md)

---

## 12 · Checklist para integradores

Antes de poner una integración en producción:

- [ ] Utiliza `/api/v1`
- [ ] Implementa autenticación JWT
- [ ] Maneja correctamente 401, 403, 404, 429 y 503
- [ ] Respeta la paginación
- [ ] Implementa backoff exponencial
- [ ] Registra `X-Request-Id`
- [ ] Utiliza HTTPS
- [ ] No depende de campos no documentados
- [ ] Valida firmas de Webhooks (si aplica)

---

## 13 · Roadmap

Próximas capacidades del contrato MAG:

- Refresh Tokens
- OAuth 2.1
- API Keys para servicios
- GraphQL Gateway (evaluación)
- SDK oficiales
- Portal para desarrolladores
- Sandbox público
- Marketplace de integraciones

**Siguiente hito:** Sprint 9 · **MSD v1.0** (Roustix SDK & Developer Portal)

| Entrega MSD | Descripción |
|-------------|-------------|
| Portal | developer.roustix.app |
| OpenAPI 3.1 | `openapi.v1.yaml` |
| SDK | Python · JavaScript · PHP |
| CLI | `roustix-cli` |
| Sandbox | API Explorer |
| Quick Start | Guías paso a paso |
| Colecciones | Postman e Insomnia |

---

## Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MAG-02 · Auth JWT](02-autenticacion-jwt.md) | Gestión del token |
| [MAG-04 · Recursos REST](04-recursos.md) | Consumo de recursos |
| [MAG-06 · Errores](06-manejo-errores.md) | Reintentos y respuestas |
| [MAG-07 · Versionado](07-versionado.md) | Compatibilidad |
| [MAG-08 · Webhooks](08-webhooks.md) | Buenas prácticas de eventos |
| [MAG-09 · Ejemplos y SDK](09-ejemplos.md) | Implementación recomendada |
| [MPA-06 · Integraciones](/mpa/chapters/06-integraciones.md) | Estrategia de integración |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] Existe una política oficial de Rate Limiting
- [ ] Los clientes conocen cuándo reintentar solicitudes
- [ ] La documentación define tiempos de espera recomendados
- [ ] Las buenas prácticas de seguridad están documentadas
- [ ] Los SDK oficiales siguen estas recomendaciones
- [ ] Todas las integraciones utilizan el contrato MAG v1

**Documentación:** ✅ · **Implementación en código:** 🟡 parcial (login rate limit activo)

---

## Filosofía del capítulo

Una API bien diseñada no solo define **qué** puede hacerse, sino también **cómo** hacerlo correctamente. Las buenas prácticas garantizan que todas las integraciones se comporten de forma consistente, segura y eficiente, permitiendo que Roustix escale sin sacrificar estabilidad.

**MAG-10 cierra la especificación oficial de Roustix API Guidelines (MAG v1.0)**, estableciendo las reglas de convivencia entre la plataforma y todos sus consumidores.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Contrato** | ✅ Completo |
| **Implementación actual** | 🟡 Parcial (Rate Limit y OpenAPI en evolución) |
| **Compatibilidad** | API REST v1 |
| **Resultado** | ✅ **MAG v1.0 Finalizado** |

---

## MAG v1.0 · Índice completo

| Código | Capítulo | Estado |
|--------|----------|--------|
| MAG-01 | Filosofía de la API | ✅ |
| MAG-02 | Autenticación JWT | ✅ |
| MAG-03 | Multi-tenant | ✅ |
| MAG-04 | Recursos REST | ✅ |
| MAG-05 | Convenciones de nombres | ✅ |
| MAG-06 | Manejo de errores | ✅ |
| MAG-07 | Versionado | ✅ |
| MAG-08 | Webhooks | ✅ |
| MAG-09 | Ejemplos y SDK | ✅ |
| MAG-10 | Límites y buenas prácticas | ✅ |

### Sprint 8 · Estado

**Sprint 8 (MAG v1.0) queda 100% completado.**

Con este sprint, Roustix dispone de un estándar de API de nivel empresarial — comparable en estructura documental con plataformas como Stripe, GitHub, Microsoft Graph o Notion — adaptado a la arquitectura multi-tenant y modular de Roustix.

---

→ [Índice MAG](/mag/) · [MPA-06](/mpa/chapters/06-integraciones.md) · [SDK](../../sdk/README.md) · [Roustix Docs](/docs/)
