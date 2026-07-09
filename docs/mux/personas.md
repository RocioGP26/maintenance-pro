# MUX · Perfiles de usuario

Maintix se diseña para personas con nombre, edad y frustraciones — no para «usuario genérico».

## Activos (v1.1)

| ID | Avatar | Nombre | Perfil | Ficha |
|----|--------|--------|--------|-------|
| MTX-UX-PER-001 | 👩‍💼 | Laura | Gerente · 42 años | [ficha](personas/MTX-UX-PER-001-gerente.md) |
| MTX-UX-PER-002 | 👨‍🔧 | Carlos | Técnico · 35 años | [ficha](personas/MTX-UX-PER-002-tecnico.md) |
| MTX-UX-PER-003 | 👩‍💻 | Valentina | Vendedora · 28 años | [ficha](personas/MTX-UX-PER-003-vendedor.md) |
| MTX-UX-PER-004 | 👨‍🏭 | Roberto | Bodeguero · 45 años | [ficha](personas/MTX-UX-PER-004-bodeguero.md) |
| MTX-UX-PER-005 | 👩‍💻 | Andrea | Administradora · 38 años | [ficha](personas/MTX-UX-PER-005-administrador.md) |

## Reservados (código asignado, ficha stub)

| ID | Avatar | Nombre placeholder | Perfil | Ficha |
|----|--------|-------------------|--------|-------|
| MTX-UX-PER-006 | 📋 | *(por definir)* | **Auditor** | [reservado](personas/MTX-UX-PER-006-auditor.md) |
| MTX-UX-PER-007 | 🚚 | *(por definir)* | **Proveedor** | [reservado](personas/MTX-UX-PER-007-proveedor.md) |
| MTX-UX-PER-008 | 🤝 | *(por definir)* | **Cliente** | [reservado](personas/MTX-UX-PER-008-cliente.md) |

### Por qué reservar 006–008

| ID | Futuro módulo |
|----|---------------|
| 006 Auditor | ISO 9001/14001/45001, auditorías, checklists, cumplimiento |
| 007 Proveedor | Portal proveedor, cotizaciones, compras, facturación |
| 008 Cliente | CRM, portal cliente, autoservicio |

> **Regla:** No implementar UI para estos perfiles hasta ficha completa + journey. El ID ya está en el registro.

## User Journey por perfil

Ver [journeys.md](journeys.md) y carpeta `journeys/`.

## Goals y Anti-Goals

Ver [goals.md](goals.md) — cambia decisiones de diseño.

## Matriz de necesidades

| Necesidad | Laura | Carlos | Valentina | Roberto | Andrea |
|-----------|:-----:|:------:|:---------:|:-------:|:------:|
| Dashboard | ●●● | ○ | ○ | ○ | ●● |
| OT | ○ | ●●● | ○ | ● | ○ |
| Ventas | ○ | ○ | ●●● | ● | ○ |
| Inventario | ○ | ● | ●● | ●●● | ○ |
| Config | ○ | ○ | ○ | ○ | ●●● |

## Regla de diseño

Antes de merge, responder:

1. ¿Quién es la persona? (nombre + ID)
2. ¿Cuál es su **Goal** y su **Anti-Goal**?
3. ¿El journey tiene retroalimentación en cada paso? (Ley 2)
