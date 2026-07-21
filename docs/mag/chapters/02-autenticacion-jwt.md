# MAG-02-AUTH · Autenticación JWT

**Código:** MAG-02-AUTH · Sprint 8.2 · **Entregado**

> Una identidad. Un token. Una empresa.

Toda petición autenticada a Roustix se realiza mediante **JSON Web Token (JWT)**. El token identifica al usuario, la empresa (tenant) y el rol, evitando que el cliente tenga que enviar información sensible en cada solicitud.

La autenticación no solo valida quién es el usuario; también determina **qué empresa está usando**, **qué módulos tiene activos** y **qué permisos posee**.

---

## 1 · Flujo de autenticación

```
Login
   │
   ▼
Usuario + contraseña + empresa
   │
   ▼
Validación
   │
   ▼
JWT firmado
   │
   ▼
Cliente almacena token
   │
   ▼
Authorization: Bearer <token>
   │
   ▼
API Roustix
```

---

## 2 · Endpoint oficial

```http
POST /api/v1/auth/login
Content-Type: application/json
```

**Ruta actual (legacy):** `POST /api/auth/login`

### Request

```json
{
  "username": "ana.garcia",
  "password": "********",
  "empresa_slug": "empresa-xyz"
}
```

### Respuesta exitosa (200)

```json
{
  "token": "<jwt>",
  "expires_in": 86400,
  "user": {
    "id": 15,
    "nombre": "Ana García",
    "rol": "admin"
  },
  "empresa": {
    "id": 4,
    "slug": "empresa-xyz",
    "nombre": "Empresa XYZ"
  }
}
```

| Campo | Descripción |
|-------|-------------|
| `token` | JWT firmado (ver §4) |
| `expires_in` | Segundos hasta expiración (86400 = 24 h) |
| `user` | Identidad y rol del usuario |
| `empresa` | Tenant activo tras login |

**Implementación actual:** respuesta plana (`token`, `empresa_id`, `empresa_slug`, `rol`, `username`) — convergencia planificada hacia el formato anidado anterior.

---

## 3 · Header estándar

Todas las solicitudes autenticadas utilizan:

```http
Authorization: Bearer eyJhbGc...
```

**No se aceptan otros métodos** para la API pública (no query string, no Basic Auth).

---

## 4 · Parámetros de firma

| Parámetro | Valor |
|-----------|-------|
| **Algoritmo** | HS256 |
| **Firma** | `SECRET_KEY` de la aplicación |
| **Expiración** | 24 h |
| **Clock skew** | ±30 s recomendado |

Implementación: `app/tenancy/jwt_auth.py` · `jwt.encode` / `jwt.decode` con `algorithms=["HS256"]`.

---

## 5 · Payload del JWT

El token contiene únicamente la información necesaria para identificar el **contexto de operación**.

| Campo | Descripción | Obligatorio v1 |
|-------|-------------|----------------|
| `sub` | ID del usuario | Sí |
| `empresa_id` | Empresa del usuario | Sí |
| `empresa_slug` | Identificador público de la empresa | Sí |
| `rol` | Rol principal | Sí |
| `plan` | Plan contratado (`start`, `grow`, `scale`, …) | Sí* |
| `modules` | Módulos activos del tenant | Sí* |
| `iat` | Fecha de emisión (Unix timestamp) | Sí |
| `exp` | Fecha de expiración (Unix timestamp) | Sí |

\* Documentado en MAG v1 · implementación en curso.

### Ejemplo

```json
{
  "sub": 15,
  "empresa_id": 4,
  "empresa_slug": "empresa-xyz",
  "rol": "admin",
  "plan": "grow",
  "modules": ["maintenance", "inventory"],
  "iat": 1783670400,
  "exp": 1783756800
}
```

El servidor **nunca** confía en `empresa_id` enviado en query o body si contradice el token.

### Claims reservados

Roustix reserva los siguientes claims para futuras versiones. **No deben ser usados por integradores:**

| Claim | Uso previsto |
|-------|--------------|
| `tenant_type` | Tipo de tenant (empresa, partner, sandbox) |
| `permissions` | Permisos granulares más allá del rol |
| `locale` | Locale preferido del usuario |
| `timezone` | Zona horaria IANA del tenant |
| `features` | Feature flags activos |

Esto evita romper el contrato cuando se añadan capacidades sin bump de versión JWT.

---

## 6 · Tiempo de vida y renovación

| Token | Duración | Estado |
|-------|----------|--------|
| **Access Token** | 24 horas | ✅ Operativo |
| **Refresh Token** | 7–30 días (por definir) | 📋 MAG v2.0 |

### Refresh (contrato reservado)

```http
POST /api/v1/auth/refresh
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

**Estado:** 📋 Planificado para **MAG v2.0**.

Respuesta prevista: nuevo `token` + `expires_in` sin reenviar credenciales.

---

## 7 · Códigos de respuesta

| Código | Significado |
|--------|-------------|
| **200** | Login exitoso |
| **400** | Solicitud inválida · username ambiguo sin `empresa_slug` |
| **401** | Usuario o contraseña incorrectos |
| **403** | Usuario suspendido o sin acceso · sin empresa asignada |
| **429** | Demasiados intentos (5 / 15 min por IP) |
| **500** | Error interno |

### Error estándar (auth)

```json
{
  "error": {
    "code": "LOGIN_FAILED",
    "message": "Usuario o contraseña incorrectos"
  }
}
```

Formato completo de errores → [MAG-06 · Manejo de errores](06-manejo-errores.md).

---

## 8 · Cierre de sesión

```http
POST /api/v1/auth/logout
Authorization: Bearer <token>
```

En la versión actual el cliente **elimina el token almacenado**. En futuras versiones podrá invalidarse mediante lista de revocación.

---

## 9 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Nunca almacenar el JWT en URLs |
| 2 | Utilizar siempre HTTPS en producción |
| 3 | No incluir información confidencial en el payload |
| 4 | Renovar el token al expirar (o vía refresh en MAG v2) |
| 5 | El servidor valida firma y expiración en cada solicitud |

---

## 10 · Seguridad

La autenticación **no concede permisos por sí sola**.

Después de validar el token, Roustix verifica:

1. Que el usuario exista
2. Que la empresa esté activa
3. Que el plan permita el módulo solicitado
4. Que el rol tenga permisos para la acción
5. Que el recurso pertenezca al mismo tenant

Solo entonces se procesa la petición.

---

## 11 · Sesión web vs API

| Modo | Uso |
|------|-----|
| **Cookie de sesión** | App web Roustix (Flask-Login) |
| **JWT Bearer** | Integraciones, scripts, partners |

`@tenant_required` acepta ambos: JWT en header o sesión activa.

---

## 12 · Filosofía del capítulo

El JWT no solo identifica al usuario. Identifica el **contexto completo de operación**: empresa, plan, módulos y permisos. Cada solicitud a Roustix ocurre dentro de ese contexto.

---

## Relación con otros documentos

| Doc | Rol |
|-----|-----|
| [MPA-04 · Arquitectura SaaS](/mpa/chapters/04-arquitectura-saas.md) | Estructura multi-tenant |
| [MPA-07 · Seguridad](/mpa/chapters/07-seguridad.md) | Políticas auth y autorización |
| [MAG-03 · Multi-tenant](03-multi-tenant.md) | Aislamiento por `empresa_id` |
| [MAG-06 · Errores](06-manejo-errores.md) | Formato `error.code` |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] El endpoint `/api/v1/auth/login` está disponible
- [ ] El JWT contiene los claims mínimos definidos por MAG
- [ ] Todas las rutas protegidas aceptan `Authorization: Bearer`
- [ ] El middleware valida firma, expiración y tenant
- [ ] La documentación coincide con la implementación

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Implementación actual** | 🟢 Operativa (legacy `/api/auth/login`) |
| **Compatibilidad** | JWT v1 |
| **Legacy** | `/api/auth/login` |
| **Siguiente capítulo** | [MAG-03 · Multi-tenant](03-multi-tenant.md) |

---

→ [MAG-03-TNT · Multi-tenant](03-multi-tenant.md)
