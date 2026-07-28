# 09 · Administración del equipo

Disponible para **Administrador** y **Superadministrador** (y opciones avanzadas según permiso).

---

## 1. Usuarios y roles

**Menú:** `Administración → Usuarios y roles` · `/equipo`

Puedes:

- crear usuarios,
- asignar **rol** y **área**,
- definir **tarifa hora** (para costo de mano de obra en OT),
- restablecer acceso / gestionar estado activo,
- desactivar usuarios que ya no operan.

### Recomendaciones

| Situación | Rol sugerido |
|-----------|--------------|
| Reporta fallas desde planta | Solicitante |
| Ejecuta OT en campo | Técnico |
| Asigna y cierra OT | Supervisor |
| Configura catálogos y equipo | Administrador |
| Acceso total del tenant | Superadministrador |

Un usuario activo por empresa por sesión: no compartas credenciales.

---

## 2. Configuración de empresa

**Menú:** `Administración → Configuración de empresa` · `/configuracion/empresa`

Revisa razón social, NIT, sector, moneda, zona horaria, logo y módulos activos. Los cambios de módulos afectan el menú de todos los usuarios.

---

## 3. Campos personalizados

**Menú:** `Administración → Campos personalizados` · `/configuracion/campos`

Extiende fichas (por sector o categoría) sin pedir desarrollo. Úsalos con moderación: demasiados campos bajan la calidad del dato.

---

## 4. Seguridad y sesiones

**Menú:** `Administración → Seguridad` · `/administracion/seguridad`

Gestiona políticas de sesión y revisa accesos según lo que permita tu plan. Pide a los usuarios cerrar sesión en equipos compartidos.

---

## 5. Integraciones (API)

**Menú:** `Administración → Credenciales API` · `/administracion/integraciones/credenciales`

Solo **Superadmin** o **Admin** de área TI/TIC/Sistemas. Las claves son secretas: no las pegues en chats ni repositorios públicos.

Documentación de integración: portal MAG / MSD de Roustix.

---

## 6. Mi perfil (todos los roles)

Cualquier usuario puede abrir **Mi perfil** (`/mi-perfil`) para datos personales. Los cambios de rol los hace un administrador.

→ Siguiente: [Preguntas frecuentes](10-faq.md)
