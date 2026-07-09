# UX · Principios de navegación

Reglas para que cada perfil encuentre lo que necesita **sin pensar en el sistema**.

## MTX-UX-NAV-001 · Tres zonas

| Zona | Contenido | Comportamiento |
|------|-----------|----------------|
| **Sidebar** | Módulos activos del tenant | Persistente, colapsable, icono + texto |
| **Navbar** | Contexto de pantalla + acciones | Título claro, máx. 2 botones filled |
| **Contenido** | Trabajo del usuario | Una tarea principal por vista |

## MTX-UX-NAV-002 · Módulo = verbo operativo

El menú habla en **acciones de negocio**, no en tablas de base de datos.

| ✅ Menú | ❌ Evitar |
|---------|----------|
| Activos | `equipos_tbl` |
| Órdenes de trabajo | CMMS module |
| Inventario | Stock mgmt |
| Ventas | POS subsystem |

## MTX-UX-NAV-003 · Profundidad máxima

```
Módulo → Lista → Detalle → Acción
```

Máximo **4 niveles**. Si se necesita más, dividir en flujo o modal (patrón MDL).

## MTX-UX-NAV-004 · Home por perfil

| Perfil | Landing post-login |
|--------|-------------------|
| Gerente | Dashboard operativo |
| Técnico | Mis OTs / OTs abiertas |
| Vendedor | Ventas del día / Nueva venta |
| Bodeguero | Inventario + alertas stock |
| Administrador | Resumen tenant o wizard pendiente |

Implementación: rol IAM determina redirect (futuro producto).

## MTX-UX-NAV-005 · Una acción primaria

Cada pantalla tiene **un solo CTA principal** visible (MDL: MTX-BTN-001). Secundarias en outline o ghost.

## MTX-UX-NAV-006 · Breadcrumb cuando hay profundidad

Lista → Detalle → Editar: siempre indicar dónde está el usuario.

Formato: `Activos / CPS-001 / Editar`

## MTX-UX-NAV-007 · Configuración separada

Administración, usuarios, IAM y facturación viven bajo **Configuración** — nunca mezclados con OTs o ventas en el mismo nivel del sidebar.

## MTX-UX-NAV-008 · Búsqueda global (roadmap)

Un campo de búsqueda accesible desde navbar: activos, OTs, clientes, productos — resultados agrupados por tipo.

## MTX-UX-NAV-009 · Permisos = ausencia, no error

Si un usuario no tiene módulo, **no mostrar** el ítem del menú. No mostrar enlace que lleva a 403.

## MTX-UX-NAV-010 · Mobile

Técnico y vendedor en campo: priorizar **listas + acción flotante** sobre dashboards densos. Ver MDL responsive.

## Checklist nueva pantalla

- [ ] ¿Perfil principal identificado?
- [ ] ¿Título describe la tarea, no la tecnología?
- [ ] ¿Un solo primary CTA?
- [ ] ¿Vuelta atrás clara?
- [ ] ¿Empty state con siguiente paso?
