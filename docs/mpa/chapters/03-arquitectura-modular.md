# MPA-03-MOD · Arquitectura modular

**Código:** MPA-03-MOD · Sprint 6.3

> El concepto más importante de Roustix: **una plataforma, módulos activables, cero instalaciones distintas**.

---

## 1 · El stack conceptual

```
        Tenant (Empresa)
              │
              ▼
        Módulos activos
              │
              ▼
        Permisos (rol × módulo)
              │
              ▼
        Datos (aislados por empresa_id)
              │
              ▼
        Dashboards (KPIs por contexto)
```

Cada empresa activa **únicamente** lo que necesita. El resto del código existe en la plataforma pero **no es accesible** para ese tenant.

---

## 2 · Tenant

Un **tenant** es una **empresa** (`Empresa` en `app/models.py`):

| Atributo | Rol |
|----------|-----|
| `id` / `slug` | Identidad y URL amigable |
| `sector` | Plantilla sectorial al onboarding |
| `modulos_activos_json` | Módulos habilitados |
| `suspendida` | Bloqueo operativo |
| Plan activo | Límites de uso (activos, usuarios, storage) |

**Aislamiento:** casi toda query filtra por `empresa_id`. El middleware de tenancy (`app/tenancy/`) establece `g.empresa_id` en cada request autenticado.

---

## 3 · Módulos

Módulos persistidos como JSON en la empresa:

```json
["mantenimiento"]
["inventario"]
["mantenimiento", "inventario"]
```

| Clave | Constante | Descripción |
|-------|-----------|-------------|
| `mantenimiento` | `MODULO_MANTENIMIENTO` | CMMS: activos, OT, calendario, repuestos |
| `inventario` | `MODULO_INVENTARIO` | Comercial: productos, compras, ventas |

**Registro:** `app/modules.py` — única fuente de módulos válidos.

### Enforcement

1. **Middleware** — `modulo_requerido_por_endpoint()` bloquea rutas si el módulo no está activo
2. **UI** — menú lateral oculta secciones de módulos inactivos
3. **Onboarding** — preset por sector (`comercio` → solo inventario)

### Caso especial · solo inventario

Empresas de comercio pueden operar **sin** Maintenance activo. El dashboard y la terminología de roles se adaptan (ej. «Vendedor» en lugar de «Técnico»).

---

## 4 · Permisos

Jerarquía de roles (`app/permissions.py`):

| Rol | Alcance típico |
|-----|----------------|
| `superadmin` | Plataforma completa (raro en tenant) |
| `admin` | Configuración, equipo, todos los módulos activos |
| `tecnico` | Operación diaria (OT / ventas según módulo) |
| `usuario` | Lectura y acciones limitadas |

Los permisos son **por empresa**, no globales. Un usuario pertenece a un tenant.

**Regla de diseño:** un permiso nuevo debe declarar si aplica a Maintenance, Inventory o núcleo.

---

## 5 · Datos

### Principio

> Los datos de un módulo viven en las mismas tablas multi-tenant, no en bases separadas.

### Patrones

| Patrón | Ejemplo |
|--------|---------|
| `empresa_id` en toda entidad de negocio | `machines`, `productos`, `ordenes` |
| Campos base + extensión sectorial | `machines` + `activo_campo_valores` |
| JSON de configuración por empresa | `plantillas_dashboard`, `modulos_activos_json` |
| Catálogos globales de plataforma | `SectorCatalogo`, `CatalogoPlan` |

### Anti-patrón

❌ Crear `tabla_inventario_empresa_x`  
❌ Duplicar lógica de tenancy en un módulo nuevo  
✅ Nuevo módulo = nuevas tablas con `empresa_id` + registro en `modules.py`

---

## 6 · Dashboards

Los dashboards son la **capa de síntesis** del stack modular:

| Nivel | Contenido |
|-------|-----------|
| Dashboard principal | KPIs según módulos activos |
| Plantilla sectorial | Etiquetas y agrupaciones JSON |
| Dashboard comercial | Métricas de Inventory |
| Dashboard mantenimiento | OT, activos, preventivos |

Un tenant con ambos módulos ve **una experiencia unificada**, no dos apps.

---

## 7 · Añadir un módulo nuevo (checklist)

1. Definir clave en `MODULOS_VALIDOS` y `MODULO_META`
2. Mapear prefijos de endpoint en `_ENDPOINT_PREFIX_MODULO`
3. Crear blueprint o subpaquete con tenancy en todas las queries
4. Registrar en onboarding y planes (MCM-06 / `CatalogoPlan`)
5. Añadir entradas de menú condicionadas a `empresa_tiene_modulo()`
6. Documentar en MPA-02-ECO y MPA-05-ROAD
7. Cumplir MUX Laws y componentes MDL

---

## Siguiente

→ [MPA-04-SAAS · Arquitectura SaaS](04-arquitectura-saas.md)
