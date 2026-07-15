# MRG-07-ADMIN · Administración

**Código:** MRG-07-ADMIN · Sprint 10.7 · **Entregado**

> El módulo **Administration** centraliza la gestión de usuarios, roles, empresas, sedes y configuración del inquilino. A nivel de plataforma, **Mantis** administra el ecosistema SaaS completo.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Documentar el funcionamiento administrativo de Maintix, diferenciando claramente la **administración del inquilino** de la **administración de la plataforma SaaS**.

**Estado:** ✅ **Núcleo operativo en producción** · **Sprint 14 ALIGN:** ✅ Cerrado (2026-07-10)

| Estado | Significado |
|--------|-------------|
| ✅ Producción | Implementado y alineado |
| 🟡 Parcial | Gaps documentados |
| 📋 Roadmap | No implementado |

→ Auditoría Sprint 14: [ALIGN · Fase 6](../../alignment/modules/07-admin-audit.md) · Permisos: [07-permissions-matrix.md](../../alignment/modules/07-permissions-matrix.md)

### Matriz de implementación (Sprint 14)

| Sección | Tema | Estado |
|---------|------|--------|
| §1 | Alcance | ✅ |
| §2 | Dos niveles admin | ✅ |
| §3 | Usuarios y roles | ✅ |
| §4 | Gestión usuarios | 🟡 |
| §5 | Empresas (tenants) | ✅ |
| §6 | Sedes | 🟡 |
| §7 | Configuración tenant | ✅ |
| §8 | Onboarding | ✅ |
| §9 | Mantis | ✅ |
| §10 | Seguridad | ✅ |
| API | MAG admin | 🟡 |

**Gaps abiertos (📋):** invitación email E2E · multisede completa · API admin.

---

## 1 · Alcance · ✅

| Incluye | No incluye |
|---------|------------|
| Usuarios | Procesos operativos |
| Roles | Órdenes de trabajo |
| Empresas (tenant) | Inventario |
| Sedes | CRM |
| Configuración | Reportes analíticos |
| Parámetros generales | Facturación del cliente final |

---

## 2 · Dos niveles de administración · ✅

Maintix distingue claramente **dos ámbitos administrativos**:

| Nivel | Responsable | Alcance |
|-------|-------------|---------|
| **Administrador del inquilino** | Empresa cliente | Usuarios, configuración y operación de su organización |
| **Administrador de plataforma (Mantis)** | Operador Maintix | Gestión SaaS completa |

Los administradores de una empresa **nunca pueden acceder** a información de otros inquilinos.

→ [MRG-01 · Intro · Tenant-first](01-intro-filosofia.md) · [MAG-03 · Multi-tenant](/mag/chapters/03-multi-tenant.md)

---

## 3 · Usuarios y roles · ✅

Cada empresa administra **sus propios usuarios**.

### Roles principales

| Rol | Mantenimiento | Inventario |
|-----|-------------|-----------|
| **Superadministrador** | Acceso completo | Acceso completo |
| **Administrador** | Gestión operativa | Gestión operativa |
| **Supervisor** | Coordina, asigna y cambia estados | Coordinación operativa |
| **Técnico** | Órdenes de trabajo | — |
| **Vendedor** | Reporte y seguimiento de incidencias propias | Inventario, ventas y clientes |
| **Usuario — solo consulta** | Consulta general | Consulta general |
| **Solicitante / Reportante** | Reporta y consulta incidencias propias | — |

`tecnico` y `vendedor` son claves independientes. En empresas con ambos módulos, el Técnico no entra a Inventario y el Vendedor no entra a la operación de Mantenimiento, salvo el reporte y seguimiento de sus propias incidencias.

El acceso también considera el área del usuario: un `admin` cuya área contiene **Mantenimiento** no puede acceder al módulo de Inventario. Esta restricción no aplica al `superadmin`, que conserva acceso completo.

### Matriz de permisos (resumen)

| Acción | Superadmin | Admin | Supervisor | Técnico | Vendedor | Usuario | Solicitante |
|--------|------------|-------|------------|---------|----------|---------|-------------|
| Crear catálogos | ✅ | ✅ | ✅ | ❌ | Operación comercial | ❌ | ❌ |
| Editar operación | ✅ | ✅ | ✅ | Solo mantenimiento | Solo inventario | ❌ | Incidencias propias |
| Eliminar registros | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Configuración avanzada | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Gestionar equipo | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |

→ [MRG-02 · Mantenimiento · Roles](02-maintenance.md) · [MRG-05 · Ventas](05-ventas.md)

→ Matriz IAM Sprint 14: [07-permissions-matrix.md](../../alignment/modules/07-permissions-matrix.md)

### Dashboard y navegación por rol

La página de inicio y el menú se generan según el rol y sus permisos. Ocultar una opción no sustituye la autorización: las rutas y consultas aplican el mismo alcance en el servidor.

| Rol | Inicio principal | Alcance operativo |
|-----|------------------|-------------------|
| Solicitante / Reportante | Mis incidencias | Reportes propios y sus cambios de estado |
| Técnico | Mi jornada | OT e incidencias asignadas, agenda, repuestos y activos vinculados |
| Supervisor | Coordinación operativa | Equipo, asignaciones, carga y pendientes |
| Jefe de área | Gestión del área | Cumplimiento, costos, backlog y desempeño |
| Gerente | Resumen ejecutivo | Indicadores autorizados entre módulos |
| Administrador | Administración | Usuarios, configuración, auditoría y seguridad del tenant |

Para el rol `tecnico`, la navegación oficial es: **Inicio · Mis órdenes de trabajo · Mis incidencias · Agenda · Repuestos · Mis activos · Notificaciones · Perfil**. No se muestran compras, ventas, clientes, empresas, usuarios, configuración ni reportes financieros.

---

## 4 · Gestión de usuarios · 🟡

El administrador puede realizar las siguientes operaciones:

- crear usuarios
- invitar mediante correo electrónico (flujo operativo del tenant)
- asignar roles
- cambiar permisos
- restablecer contraseña
- desactivar usuarios
- reactivar usuarios

Toda acción queda registrada para **auditoría** (`TenantActivityLog`).

> **Hoy:** gestión en `/equipo` · nav **Administración → Usuarios y roles** · un usuario activo por empresa por sesión.

---

## 5 · Empresas (Tenants) · ✅

Cada empresa representa un **inquilino completamente aislado**.

| Información | Descripción |
|-------------|-------------|
| Razón social | Identidad jurídica |
| NIT / RUT | Identificación fiscal |
| Sector | Plantilla de incorporación |
| Plan contratado | Inicio · Crecimiento · Escala |
| Módulos activos | Mantenimiento, Inventario, etc. |
| Moneda | Configuración financiera |
| Zona horaria | Operación e informes |
| Logotipo | Identidad visual |
| Estado | Activa · suspendida · en prueba (trial) |

Toda la información pertenece **exclusivamente al tenant**.

→ [MCM-06 · Planes comerciales](/mcm/chapters/06-planes-comerciales.md)

---

## 6 · Sedes · 🟡

Una empresa puede operar desde **múltiples ubicaciones**.

Cada sede permite organizar:

- activos
- inventarios
- usuarios
- reportes
- indicadores

La operación **multisede** se reflejará progresivamente en los módulos funcionales.

> **Hoy:** sede principal en onboarding · activos vinculables a sede · reportes mayormente agregados al tenant.

---

## 7 · Configuración del tenant · ✅

Cada empresa puede personalizar su entorno:

| Área | Configuración |
|------|---------------|
| **Empresa** | Información legal |
| **Apariencia** | Logo e identidad |
| **Moneda** | Moneda principal y secundaria |
| **Zona horaria** | Fecha y hora · jornada laboral (OT) |
| **Campos personalizados** | Mantenimiento — por tipo de activo |
| **Módulos** | Activación según plan contratado |

---

## 8 · Onboarding · ✅

El proceso estándar de incorporación es:

```
Registro
      │
      ▼
Creación del tenant
      │
      ▼
Administrador inicial
      │
      ▼
Sede principal
      │
      ▼
Activación del plan
      │
      ▼
Carga de datos de ejemplo
      │
      ▼
Inicio de operación
```

El contenido inicial depende del **sector** seleccionado (manufactura → Mantenimiento · comercio → Inventario).

→ Ruta self-service: `/onboarding`

---

## 9 · Plataforma Mantis · ✅

La plataforma administrativa de Maintix dispone de capacidades **exclusivas**:

| Función | Descripción |
|---------|-------------|
| **Gestión de tenants** | Empresas registradas |
| **Gestión de planes** | Inicio · Crecimiento · Escala |
| **Suspensión** | Mora o decisión de soporte |
| **Reactivación** | Restablecimiento del servicio |
| **Suplantación (impersonación)** | Soporte técnico autorizado |
| **Configuración global** | Sectores y plantillas |
| **Monitoreo** | Estado general de la plataforma |
| **Facturación SaaS** | Suscripciones y mora del tenant |

Estas funciones **no están disponibles** para los clientes finales.

→ Área: `/platform/` · auditoría: `PlatformAuditLog`

---

## 10 · Seguridad administrativa · ✅

Toda operación administrativa se encuentra protegida mediante:

| Mecanismo | Función |
|-----------|---------|
| **Autenticación JWT** | API e integraciones — [MAG-02](/mag/chapters/02-autenticacion-jwt.md) |
| **Permisos por rol** | Acciones acotadas por perfil |
| **Aislamiento por tenant** | `empresa_id` en contexto de cada request |
| **Auditoría completa** | Registro de actividad por tenant |
| **Registro de eventos** | Logins · impersonación · suspensiones |

Las acciones críticas quedan registradas con **usuario, fecha y empresa**.

---

## 11 · Integración con otros módulos · ✅

```
Administración
        │
        ├────────► Mantenimiento
        ├────────► Inventario
        ├────────► Sales
        ├────────► CRM (roadmap)
        ├────────► Reportes
        └────────► Plataforma Mantis
```

La administración constituye el **punto de control** de toda la plataforma — roles, módulos activos y configuración determinan qué ve y hace cada usuario en MRG-02 a MRG-06.

---

## 12 · Buenas prácticas · ✅

| # | Recomendación |
|---|---------------|
| 1 | Utilizar siempre roles con el **mínimo privilegio** necesario |
| 2 | Desactivar usuarios que ya no pertenezcan a la empresa |
| 3 | Mantener actualizada la información del tenant |
| 4 | Revisar periódicamente permisos y accesos |
| 5 | Registrar todas las sedes reales |
| 6 | Utilizar la auditoría para investigaciones y soporte |

---

## Relación con otros capítulos

| Documento | Relación |
|-----------|----------|
| [MRG-01 · Intro](01-intro-filosofia.md) | Tenant-first |
| [MRG-02 · Mantenimiento](02-maintenance.md) | Roles técnicos |
| [MRG-03 · Inventario](03-inventario.md) | Roles comerciales |
| [MAG-02 · JWT](/mag/chapters/02-autenticacion-jwt.md) | Autenticación |
| [MAG-03 · Multi-tenant](/mag/chapters/03-multi-tenant.md) | Aislamiento de empresas |
| [MCM-06 · Planes](/mcm/chapters/06-planes-comerciales.md) | Planes SaaS |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] Usuarios y roles documentados
- [x] Administración tenant vs plataforma diferenciada
- [x] Sedes y configuración documentadas
- [x] Proceso de onboarding descrito
- [x] Seguridad administrativa documentada
- [x] Alineación nav IAM vs producto (Sprint 14 · Fase 6)
- [ ] Multisede completa en todos los módulos
- [ ] Invitación por email automatizada end-to-end

**Cobertura documental:** ✅ núcleo en producción · multisede avanzada en evolución.

---

## Filosofía del capítulo

La administración no consiste únicamente en crear usuarios. Es el mecanismo mediante el cual cada empresa configura su **propio entorno de trabajo** mientras la plataforma garantiza el **aislamiento entre inquilinos** y la **administración centralizada** del ecosistema SaaS. Maintix separa claramente ambas responsabilidades para ofrecer seguridad, escalabilidad y autonomía.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Módulo Admin/IAM** | ✅ Producción |
| **Sprint 14 ALIGN** | ✅ Cerrado 2026-07-10 |
| **MRG capítulo** | v1.0.1 |
| **Próximo paso** | Fase 7 · MRG-08 Reportes ([ALIGN](../../alignment/)) |

---

→ [MRG-08 · Reportes](08-reportes.md) · [MRG-01 · Intro](01-intro-filosofia.md) · [Índice MRG](/mrg/)
