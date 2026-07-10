# MAG-03-TNT · Multi-tenant

**Código:** MAG-03-TNT · Sprint 8.3 · **Entregado**

> Una plataforma. Miles de empresas. Cero mezcla de datos.

Maintix fue diseñado como una plataforma SaaS **multi-tenant** desde su arquitectura. Todas las solicitudes, recursos y permisos existen dentro del contexto de un **tenant**, garantizando el **aislamiento completo** entre clientes.

El desarrollador nunca trabaja directamente con múltiples bases de datos ni necesita indicar qué tenant consultar. Ese contexto se obtiene automáticamente a partir del JWT o de la sesión web autenticada.

---

## 1 · ¿Qué es un tenant?

Un **tenant** es el concepto arquitectónico de aislamiento en Maintix. **En Maintix, un tenant representa una empresa cliente** (`Empresa` en el modelo de datos).

Cada tenant posee:

- usuarios
- sedes
- activos
- inventario
- órdenes de trabajo
- compras
- ventas
- configuraciones
- permisos
- auditoría

**Todo pertenece a un único tenant.**

```
Tenant
│
├── Usuarios
├── Activos
├── Inventario
├── Compras
├── Ventas
├── Reportes
└── Configuración
```

> **Nota terminológica:** En documentación MPA/MAG usamos *tenant* como concepto arquitectónico y *empresa* como implementación en BD (`empresa_id`, tabla `empresas`). Ver [MPA-03 · Arquitectura modular](/mpa/chapters/03-arquitectura-modular.md).

---

## 2 · Principio de aislamiento

Todos los datos deben pertenecer exactamente a **un** tenant.

Nunca existen registros «globales» de operación.

```
Tenant A (Empresa A)         Tenant B (Empresa B)
│                            │
├── Activos                  ├── Activos
├── Inventario               ├── Inventario
└── OTs                      └── OTs
```

**No existe comunicación** entre ambos espacios.

---

## 3 · ¿Cómo conoce Maintix el tenant?

1. El cliente inicia sesión
2. El servidor genera un JWT
3. Dentro del JWT viaja el contexto

```json
{
  "empresa_id": 4,
  "empresa_slug": "empresa-xyz",
  "rol": "admin"
}
```

4. Cada petición posterior utiliza ese contexto:

```http
Authorization: Bearer eyJhbGc...
```

El cliente **nunca** necesita enviar `empresa_id`, `tenant` ni `company` en parámetros o body.

Ver [MAG-02 · Autenticación JWT](02-autenticacion-jwt.md).

---

## 4 · Flujo completo

### 4.1 · Vista integrador

```
Usuario
     │
     ▼
Login
     │
     ▼
JWT
     │
     ▼
Middleware Tenant
     │
     ▼
empresa_id = 4
     │
     ▼
Consulta filtrada
     │
     ▼
Respuesta
```

### 4.2 · Ciclo interno Flask

```
Request
      │
      ▼
tenant_required
      │
      ▼
validar JWT / sesión
      │
      ▼
g.user_id
g.empresa_id
g.user_rol
      │
      ▼
require_module()
      │
      ▼
rol_required()
      │
      ▼
View
```

Módulos: `app/tenancy/middleware.py` · `app/tenancy/decorators.py` · `app/module_guard.py`.

---

## 5 · Filtrado automático

Todas las consultas deben ejecutarse filtrando por tenant (`empresa_id`).

**Ejemplo conceptual:**

```python
Machine.query.filter_by(empresa_id=current_empresa_id())
```

**En Maintix (patrón oficial):**

```python
query_tenant(Machine).order_by(Machine.codigo).all()
```

**SQL equivalente generado:**

```sql
SELECT *
FROM machines
WHERE empresa_id = 4
ORDER BY codigo;
```

**Nunca:**

```python
Machine.query.all()
```

ni

```sql
SELECT * FROM machines;
```

sin contexto.

Módulo: `app/tenancy/queries.py` · `query_tenant(model)`.

---

## 6 · Recurso de otro tenant

Si un usuario intenta acceder a un recurso de otro tenant:

```http
GET /api/v1/maintenance/assets/152
```

y el activo pertenece a otro tenant, Maintix responde:

**404 Not Found**

No **403 Forbidden**.

**¿Por qué?** Porque el recurso no debe revelar su existencia fuera del tenant. Mantener la existencia del recurso oculta **reduce la superficie de ataque** y evita **enumeración de recursos entre tenants**.

### Error estándar

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Activo no encontrado"
  }
}
```

Formato completo → [MAG-06 · Manejo de errores](06-manejo-errores.md).

Implementación: `verificar_pertenencia(obj)` antes de responder.

---

## 7 · Tenant en la aplicación web

La aplicación Flask utiliza el **mismo principio**.

La sesión contiene el usuario. El middleware resuelve el contexto del tenant:

- tenant (`empresa_id`, `empresa_slug`)
- plan
- módulos activos
- permisos del usuario

El resto de la aplicación trabaja únicamente con ese contexto.

**No existen pantallas «globales»** para usuarios normales.

---

## 8 · Cadena Tenant → Permisos

Toda acción en Maintix atraviesa esta cadena:

```
Usuario autenticado
        │
        ▼
     Tenant
        │
        ▼
      Plan
        │
        ▼
    Módulos
        │
        ▼
   Permisos
        │
        ▼
     Acción
```

| Eslabón | Pregunta |
|---------|----------|
| **Tenant** | ¿Contexto de empresa válido? |
| **Plan** | ¿El plan contratado permite esta capacidad? |
| **Módulos** | ¿`maintenance` / `inventory` activos? |
| **Permisos** | ¿El rol del usuario puede ejecutar la acción? |

**Ejemplo:** tenant con módulos `maintenance` + `inventory` · usuario `admin` puede leer activos · operador no puede eliminar activos.

Implementación: `empresa_tiene_modulo()` · `require_module()` · `@rol_required`.

---

## 9 · Superadministrador

Existe un único rol con visión transversal: **`superadmin`**.

Este rol pertenece a **Maintix Platform**. Puede:

- administrar tenants (empresas cliente)
- gestionar planes
- soporte
- auditoría
- impersonación controlada

Toda acción queda registrada.

Endpoints de plataforma fuera del contrato MAG público por tenant.

---

## 10 · Multi-sede

Las **sedes no son tenants**.

Jerarquía oficial:

```
Tenant (Empresa)
│
├── Sede Norte
├── Sede Centro
└── Sede Sur
```

| Separación | Campo |
|------------|-------|
| Entre tenants | `empresa_id` |
| Entre sedes (mismo tenant) | `sede_id` |

Las sedes **nunca** reemplazan al tenant.

**Estado:** 🟡 Multi-sede en evolución.

---

## 11 · Arquitectura de datos

```
Tenant (Empresa)
│
├── empresa_id
├── slug
├── plan
├── estado
└── modulos_activos

Activo (machines)
│
├── id
├── empresa_id
└── ...

Inventario (productos)
│
├── id
├── empresa_id
└── ...

OT (work_orders)
│
├── id
├── empresa_id
└── ...
```

Toda entidad operativa incorpora **`empresa_id`** como parte de su modelo.

Alineado con [MPA-04 · Arquitectura SaaS](/mpa/chapters/04-arquitectura-saas.md).

---

## 12 · Buenas prácticas

| # | Regla |
|---|-------|
| 1 | Nunca confiar en un `empresa_id` enviado por el cliente |
| 2 | El contexto siempre proviene del JWT o la sesión |
| 3 | Toda consulta debe filtrar por `empresa_id` |
| 4 | Nunca devolver recursos de otro tenant |
| 5 | Registrar accesos administrativos entre tenants |
| 6 | Cache key incluye `empresa_id` |
| 7 | Un token por usuario/servicio — no compartir entre clientes |

---

## 13 · Regla de Oro

> **Si una consulta no contiene `empresa_id`, es un bug.**

Sin excepciones en código de producción.

---

## 14 · Errores comunes

| ❌ Incorrecto | ✅ Correcto |
|--------------|------------|
| `Machine.query.get(id)` | `query_tenant(Machine).filter_by(id=id).first()` |
| `empresa_id = request.json["empresa_id"]` | `empresa_id = current_empresa_id()` |
| `SELECT * FROM machines;` | `SELECT * FROM machines WHERE empresa_id = :empresa_id;` |
| `?empresa_id=99` en query string | Tenant solo desde JWT / sesión |
| Cache global sin clave tenant | Cache key: `tenant:{empresa_id}:...` |

---

## 15 · Implementación actual

| Componente | Estado |
|------------|--------|
| JWT con `empresa_id` | ✅ Implementado |
| Middleware `@tenant_required` | ✅ Implementado |
| Filtrado `query_tenant` | ✅ Implementado |
| `verificar_pertenencia` | ✅ Implementado |
| Roles por tenant | ✅ Implementado |
| `require_module()` | ✅ Implementado |
| Multi-sede | 🟡 En evolución |
| Impersonación auditada | 📋 Roadmap |

---

## 16 · Relación con otros documentos

| Documento | Rol |
|-----------|-----|
| [MPA-03 · Arquitectura modular](/mpa/chapters/03-arquitectura-modular.md) | Activación de módulos por tenant |
| [MPA-04 · Arquitectura SaaS](/mpa/chapters/04-arquitectura-saas.md) | Modelo multi-tenant |
| [MPA-07 · Seguridad](/mpa/chapters/07-seguridad.md) | Políticas de aislamiento |
| [MAG-02 · Autenticación JWT](02-autenticacion-jwt.md) | Obtención del contexto del tenant |
| [MAG-04 · Recursos REST](04-recursos.md) | Recursos filtrados automáticamente |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [ ] El contexto del tenant se obtiene automáticamente desde el JWT o la sesión
- [ ] Todas las entidades operativas incluyen `empresa_id`
- [ ] Ninguna consulta devuelve información de otro tenant
- [ ] El middleware valida el contexto antes de ejecutar la solicitud
- [ ] Los accesos cross-tenant solo son posibles mediante `superadmin` y quedan auditados

---

## Filosofía del capítulo

El desarrollador **nunca elige el tenant**. Maintix lo determina automáticamente. Así garantizamos que cada empresa cliente vea únicamente sus propios datos, sin excepciones.

**El aislamiento multi-tenant no es una característica de la API; es un principio de toda la plataforma Maintix.** La API simplemente hereda ese comportamiento. Ver [MPA-04](/mpa/chapters/04-arquitectura-saas.md) · [MPA-09 · Filosofía técnica](/mpa/chapters/09-filosofia-tecnica.md).

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Implementación actual** | 🟢 Operativa (núcleo tenant) |
| **Compatibilidad** | JWT v1 · sesión web |
| **Legacy** | Mismo modelo en `/api/*` sin prefijo `v1` |
| **Siguiente capítulo** | [MAG-04 · Recursos REST](04-recursos.md) |

---

→ [MAG-04-RES · Recursos](04-recursos.md)
