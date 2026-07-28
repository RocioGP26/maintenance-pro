# 01 · Primeros pasos

## 1. Acceder a Roustix

1. Abre el navegador e ingresa a la URL de tu empresa (o a la plataforma Roustix).
2. En **Iniciar sesión** (`/login`) escribe tu **usuario** y **contraseña**.
3. Si en tu organización hay usuarios con el mismo nombre en distintas empresas, completa también el **identificador de empresa** (slug) cuando el sistema lo pida.
4. Pulsa **Entrar**.

Tras un inicio correcto llegas a **Inicio** (`/dashboard`), el centro de operaciones del día.

> **Seguridad:** después de varios intentos fallidos el acceso se limita temporalmente. Si olvidaste la contraseña, usa **¿Olvidaste tu contraseña?** (`/recuperar-contrasena`).

---

## 2. Recuperar o restablecer contraseña

1. En el login, abre **¿Olvidaste tu contraseña?**
2. Indica el correo registrado (y el slug de empresa si aplica).
3. Revisa tu bandeja y abre el enlace del mensaje.
4. En **Restablecer contraseña** define una nueva clave que cumpla la política de seguridad.
5. Vuelve a iniciar sesión.

---

## 3. Primera vez: cuenta empresarial (onboarding)

Si tu empresa aún no está en Roustix:

1. Desde el login elige **Crear cuenta empresarial** (`/onboarding`).
2. Completa el asistente: datos de empresa, sector, sedes, plan y módulos.
3. Verifica el correo en `/onboarding/verificar-correo` cuando se solicite.
4. Inicia sesión y configura activos, usuarios y planes preventivos.

---

## 4. Qué verás al entrar

| Elemento | Función |
|----------|---------|
| **Barra lateral** | Menú según tu rol y módulos activos |
| **Inicio** | Pendientes del día: OT, incidencias, stock mínimo, activos fuera de servicio |
| **Campana** | Alertas y notificaciones |
| **Perfil** | Tu usuario, cerrar sesión |

El técnico ve un panel enfocado en **sus** órdenes y agenda. El solicitante ve sobre todo **sus incidencias**. Administradores y supervisores ven la operación completa del módulo.

---

## 5. Cerrar sesión

En el pie del menú lateral (o desde tu menú de usuario) elige **Cerrar sesión**.

---

## 6. Checklist de arranque (administrador)

Antes de operar en producción conviene:

1. Revisar datos de la empresa en **Administración → Configuración de empresa**.
2. Crear usuarios y roles en **Administración → Usuarios y roles**.
3. Registrar **tipos de activo** y luego los **activos**.
4. Cargar **repuestos técnicos** con stock mínimo.
5. Definir **planes preventivos** o cronogramas en los activos críticos.
6. Probar el flujo: incidencia → OT → ejecución → cierre.

→ Siguiente: [Roles y navegación](02-roles-y-navegacion.md)
