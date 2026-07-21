# MPA-11-LOG · Arquitectura lógica

**Código:** MPA-11-LOG · Complemento Sprint 6  
**Audiencia:** Desarrolladores nuevos · arquitectos · onboarding técnico

> Mapa **conceptual** de capas — no un inventario de archivos.  
> Objetivo: que cualquier persona entienda en cinco minutos **por dónde fluye una petición** en Roustix.

---

## 1 · Vista en una imagen

```
┌─────────────────────────────────────┐
│  Frontend                           │
│  Plantillas · Bootstrap · MDL       │
└─────────────────┬───────────────────┘
                  │ HTTP
                  ▼
┌─────────────────────────────────────┐
│  Flask                              │
│  Blueprints · rutas · middleware    │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Services                           │
│  Reglas de negocio · orquestación   │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Repositories                       │
│  Acceso a datos · queries tenant    │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  SQLAlchemy                         │
│  Modelos · sesión · migraciones     │
└─────────────────┬───────────────────┘
                  │
                  ▼
┌─────────────────────────────────────┐
│  Database                           │
│  SQLite (dev) · PostgreSQL (prod)    │
└─────────────────────────────────────┘
```

**Regla de lectura:** de arriba hacia abajo es el camino de una acción del usuario. De abajo hacia arriba es de dónde salen los datos.

---

## 2 · Capa por capa

### Frontend · Presentación

| Qué es | Qué hace |
|--------|----------|
| Plantillas Jinja2 | HTML server-rendered por ruta Flask |
| Bootstrap | Grid, utilidades base, componentes estructurales |
| **MDL** | Tokens `--mdl-*`, componentes `mtx-*`, patrones visuales oficiales |
| JavaScript puntual | Validaciones, campos dinámicos, UX (sin SPA global hoy) |

**Responsabilidad:** mostrar información, capturar input, cumplir **MUX Laws** (empty states, feedback, CTA clara).

**No debe:** contener reglas de negocio ni queries a base de datos.

→ Componentes: [MDL](/mdl/) · Experiencia: [MUX](/mux/)

---

### Flask · Entrada HTTP

| Qué es | Qué hace |
|--------|----------|
| Blueprints | Agrupan rutas por dominio (`main`, `inv_comercial`, `platform`…) |
| Rutas | Reciben request, validan permisos, llaman services |
| Middleware tenancy | Establece `empresa_id`, verifica módulo activo y suspensión |
| Auth | Sesión web (Flask-Login) · JWT (API) |

**Responsabilidad:** traducir HTTP en llamadas de aplicación seguras y acotadas al tenant.

**No debe:** lógica de negocio extensa ni SQL embebido en templates.

---

### Services · Lógica de negocio

| Qué es | Qué hace |
|--------|----------|
| Módulos `*_service.py` | Orquestan reglas: onboarding, sectores, suscripciones, KPIs… |
| Coordinación | Varios modelos, validaciones, side effects (email, auditoría) |
| Independencia de HTTP | Misma lógica usable desde ruta web o API |

**Ejemplos conceptuales:** crear plantilla sectorial · calcular KPIs · procesar import Excel · gestionar plan.

**Responsabilidad:** el **qué** y el **por qué** del dominio.

**No debe:** conocer detalles de HTML ni duplicar queries en cada ruta.

---

### Repositories · Acceso a datos

| Qué es | Qué hace |
|--------|----------|
| Capa de persistencia | Encapsula **cómo** se lee y escribe cada agregado |
| Filtro tenant | Toda query incluye `empresa_id` (o usa helpers de tenancy) |
| Abstracción ORM | Services no necesitan saber SQL ni joins internos |

**Estado en Roustix hoy:** capa **conceptual en evolución**. Parte del acceso vive en services; existen helpers como `query_tenant()` en tenancy. La dirección es **concentrar queries** aquí, no dispersarlas en rutas.

**Responsabilidad:** un solo lugar para «obtener OT por empresa», «listar productos activos», etc.

**No debe:** reglas de negocio (eso es Service) ni renderizar UI.

---

### SQLAlchemy · Mapeo objeto-relacional

| Qué es | Qué hace |
|--------|----------|
| Modelos (`models.py`) | Tablas como clases Python |
| Sesión (`db`) | Unit of work · transacciones |
| Migraciones (Alembic) | Evolución de esquema versionada |

**Responsabilidad:** definir **estructura** de datos y relaciones.

**No debe:** lógica de pantalla ni permisos de usuario.

---

### Database · Persistencia

| Entorno | Motor |
|---------|-------|
| Desarrollo local | SQLite |
| Producción | PostgreSQL (Neon) |

**Responsabilidad:** almacenar datos de todos los tenants con aislamiento lógico por `empresa_id`.

---

## 3 · Capas transversales (cruzan todo)

Estas no son «otra fila» del diagrama — atraviesan varias capas:

| Capa transversal | Dónde actúa |
|------------------|-------------|
| **Tenancy** | Middleware → repositories → modelos |
| **Permisos** | Flask (decoradores) → services (validación) |
| **Módulos activos** | Middleware bloquea rutas de módulo inactivo |
| **MUX** | Frontend + criterios de aceptación en PR |
| **MDL** | Frontend exclusivamente |
| **Auditoría** | Services sensibles · plataforma |

---

## 4 · Flujo ejemplo · Crear una orden de trabajo

```
Usuario pulsa «Guardar OT»
        │
        ▼
Frontend: formulario mtx-* validado (MUX)
        │
        ▼
Flask: ruta POST · login · permiso · módulo mantenimiento
        │
        ▼
Service: valida reglas OT · numeración · estado inicial
        │
        ▼
Repository / query: insert con empresa_id del tenant
        │
        ▼
SQLAlchemy: persiste OrdenTrabajo
        │
        ▼
Database: fila nueva en tabla ordenes
        │
        ▼
Flask: redirect + flash de éxito (MUX Law #2)
        │
        ▼
Frontend: pantalla de confirmación / detalle OT
```

---

## 5 · Qué capa tocar según el cambio

| Si cambias… | Toca principalmente… |
|-------------|----------------------|
| Color de botón | MDL · CSS |
| Texto de ayuda | Template · MUX copy |
| Validación «OT no vacía» | Service |
| Nueva columna en BD | Modelo · migración · repository |
| Bloquear ruta sin módulo | Flask middleware · `modules.py` |
| Nuevo módulo completo | Todas — empezar por MPA-03 checklist |

---

## 6 · Dirección de madurez

Roustix es un monolito modular maduro en producto, **en evolución** en separación de capas:

| Hoy | Dirección |
|-----|-----------|
| Lógica en services | Mantener y extraer de rutas |
| Queries en services y rutas | Mover a repositories / `query_tenant` |
| UI server-rendered | MDL consistente; evitar CSS ad hoc |
| Un despliegue | Mantener; escalar horizontalmente (MPA-08) |

---

## Relación con otros capítulos

| Capítulo | Conexión |
|----------|----------|
| MPA-03 | Módulos y permisos en Flask |
| MPA-04 | Tenancy en middleware y repositories |
| MPA-09 | Filosofía «código al servicio de la plataforma» |
| MPA-12 | Reglas de evolución de cada capa |
| Developer Docs (09) | Detalle Flask, migraciones, despliegue |

---

**Anterior:** [MPA-10-2030 · Roadmap 2030](10-roadmap-2030.md)  
**Complemento:** [MPA-12-EVO · Principios de evolución](12-principios-evolucion.md)

---

*MPA-11-LOG · Roustix Platform Architecture · 2026*
