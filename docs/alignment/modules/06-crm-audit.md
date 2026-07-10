# Fase 5 · Auditoría MRG-06 · CRM

**Sprint 14.17–14.20** · **Estado:** ✅ **Fase 5 cerrada** (2026-07-10)  
**MRG:** [MRG-06-CRM](/mrg/chapters/06-crm.md)  
**Última revisión:** 2026-07-10

---

## 1 · Resumen ejecutivo

| Pregunta | Respuesta |
|----------|-----------|
| ¿Qué existe? | Maestro `InvCliente` — CRUD, baja lógica, vínculo ventas POS |
| ¿Qué hace? | Base comercial pre-CRM dentro de inventario comercial |
| ¿Qué falta? | Pipeline · oportunidades · contactos múltiples · actividades · cotizaciones · módulo CRM · API |
| ¿Qué sobra? | — |
| ¿Qué difiere del MRG? | MRG describe CRM objetivo; producto = maestro clientes (coherente §2) |

**Estado módulo:** 🟡 **Pre-CRM** (maestro clientes) · **Sprint 14 Fase 5:** ✅ **Cerrado** (alineación doc + nav)

---

## 2 · MRG §1–§2 · Alcance y estado actual

| Capacidad MRG | Implementación | Estado |
|---------------|----------------|--------|
| Clientes / cuentas | `InvCliente` | ✅ |
| Contactos múltiples | campos únicos en ficha | 📋 |
| Historial comercial | ventas vinculadas (sin UI ficha) | 🟡 |
| Saldo pendiente | agregable desde ventas crédito | 🟡 |
| Oportunidades | — | 📋 |
| Pipeline | — | 📋 |
| Actividades | — | 📋 |
| Cotizaciones | — | 📋 |

---

## 3 · MRG §3–§6 · Entidades y pipeline

| Entidad MRG | Estado |
|-------------|--------|
| Cuenta (Cliente) | ✅ `InvCliente` |
| Contacto | 📋 |
| Oportunidad | 📋 |
| Actividad | 📋 |
| Cotización | 📋 |
| Pipeline | 📋 doc |

---

## 4 · Maestro de clientes · Detalle operativo

| Función | Ruta | Estado |
|---------|------|--------|
| Listado | `/comercial/clientes` | ✅ |
| Alta / edición | `/clientes/nuevo` · `/editar` | ✅ |
| Baja lógica | inactivar/activar | ✅ |
| Búsqueda | nombre · documento · tel · email | ✅ |
| Campos MRG | nombre · documento · tel · email · dirección · notas | ✅ |
| Alta desde POS | `?next=` ventas | ✅ |
| Obligatorio crédito | validación en `registrar_venta` | ✅ |
| Ficha con historial ventas | — | 📋 |

---

## 5 · Integraciones

| Módulo | Relación | Estado |
|--------|----------|--------|
| MRG-05 Ventas | cliente en POS · cartera | ✅ |
| MRG-03 Inventario | mismo tenant comercial | ✅ |
| MRG-08 Reportes | KPIs ventas (no pipeline CRM) | 🟡 |
| API MAG `/crm/*` | — | 📋 |

---

## 6 · Menús y copy

| Elemento | Objetivo | Estado |
|----------|----------|--------|
| Nav | Clientes bajo submenú Ventas | ✅ |
| Copy listado | Base CRM pre-módulo | ✅ |
| Etiqueta sidebar | Ventas (incl. clientes) | ✅ |

---

## 7 · API MAG

| Endpoint | Estado |
|----------|--------|
| `/api/v1/crm/accounts` | 📋 |
| `/api/v1/crm/contacts` | 📋 |
| `/api/v1/crm/opportunities` | 📋 |

---

## 8 · Checklist Fase 5 · ✅ Cerrada

| # | Área | Estado |
|---|------|--------|
| 1 | Maestro clientes | ✅ |
| 2 | Nav alineado MRG-05/06 | ✅ |
| 3 | Copy pre-CRM | ✅ |
| 4 | Integración ventas | ✅ |
| 5 | Pipeline / oportunidades | 📋 |
| 6 | MRG badges | ✅ |
| 7 | API | 📋 |

---

## 9 · Rutas verificadas

```
/comercial/clientes · /clientes/nuevo · /clientes/<id>/editar · /clientes/<id>/estado
```

---

## 10 · Gaps abiertos (📋)

- Módulo CRM standalone
- Contactos múltiples por cuenta
- Pipeline configurable
- Oportunidades → venta
- Actividades y agenda
- Ficha cliente con historial
- API MAG crm

---

## 11 · Próximos pasos

1. ~~**Cerrar MRG-06 Fase 5**~~ — ✅ 2026-07-10
2. **Fase 6** — MRG-07 Admin/IAM ([checklist](../checklist.md#fase-6--mrg-07--administración-e-iam))

---

→ [Checklist maestro](../checklist.md) · [Matriz de estado](../status-matrix.md)
