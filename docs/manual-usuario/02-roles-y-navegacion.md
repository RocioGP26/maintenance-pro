# 02 · Roles y navegación

## 1. Roles de la plataforma

| Rol | Qué hace en Mantenimiento |
|-----|---------------------------|
| **Superadministrador** | Acceso total a la empresa, incluida configuración avanzada |
| **Administrador** | Catálogos, usuarios del equipo, OT, activos, reportes |
| **Supervisor** | Planea, asigna OT, cambia estados, crea órdenes e incidencias |
| **Técnico** | Ejecuta OT e incidencias asignadas; consulta activos y repuestos |
| **Vendedor** | Opera Inventario comercial; en Mantenimiento solo sus incidencias |
| **Usuario (solo consulta)** | Lectura de información autorizada |
| **Solicitante / Reportante** | Reporta incidencias y sigue solo las suyas |

Además del rol, el **área** del usuario puede limitar el acceso entre módulos (por ejemplo, un admin de área Mantenimiento no entra a Inventario comercial). El **superadministrador** no tiene esa restricción.

---

## 2. Menú según perfil

### Solicitante

- Mis incidencias  
- Reportar incidencia  
- Mi perfil  

### Técnico

- Inicio  
- Mis órdenes de trabajo  
- Mis incidencias  
- Agenda  
- Repuestos  
- Mis activos  
- Notificaciones  
- Perfil  

### Supervisor, administrador y roles operativos completos

```
Inicio
│
├── Mantenimiento
│   ├── Activos → Listado · Cronogramas · Tipos · Asset Health
│   ├── Órdenes → Listado · Planeación · Procedimientos · Automatizaciones
│   ├── Calendario
│   ├── Repuestos técnicos
│   ├── Proveedores de servicio
│   └── Incidencias
│
├── Inventario comercial   (si el módulo está activo y tienes permiso)
│
├── Inteligencia → Análisis · Costos · Reportes
│
└── Administración → Usuarios · Seguridad · Empresa · Campos · API
```

Si un módulo no está contratado o tu rol no tiene permiso, **esa opción no aparece** en el menú.

---

## 3. Diferencia importante: dos “inventarios”

| Nombre en menú | Para qué sirve |
|----------------|----------------|
| **Repuestos técnicos** (`/inventario`) | Piezas que se consumen en órdenes de trabajo |
| **Inventario comercial** (`/comercial/...`) | Productos para compra/venta (módulo aparte) |

No confundas ambos: el consumo de piezas en una OT ocurre en **Repuestos técnicos**.

---

## 4. Notificaciones

La campana del encabezado muestra alertas relevantes a tu rol:

- **Solicitante:** cambios de estado de *sus* incidencias.  
- **Operativos:** incidencias del área, vencimientos y trabajo pendiente.

Puedes abrir la notificación, marcarla como vista o ir al registro relacionado. Las alertas se actualizan de forma periódica mientras mantienes la sesión abierta.

---

## 5. Mi perfil

En **Mi perfil** (`/mi-perfil`) puedes revisar tus datos de usuario. Los cambios de rol o área los realiza un administrador en **Usuarios y roles**.

→ Siguiente: [Activos](03-activos.md)
