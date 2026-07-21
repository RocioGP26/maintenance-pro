# MRG-09-WORKFLOWS · Flujos de trabajo

**Código:** MRG-09-WORKFLOWS · Sprint 10.9 · **Entregado** · **v1.0.1** · Sprint 14 ALIGN ✅

> Roustix no se limita a registrar información. **Organiza la operación** mediante procesos completos, donde cada acción genera el siguiente paso del flujo de trabajo.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Documentar los principales **procesos funcionales de extremo a extremo** de Roustix, mostrando cómo interactúan los módulos durante la operación diaria.

Este capítulo conecta **Mantenimiento**, **Inventario**, **Compras**, **Ventas** y **Administración** bajo una misma visión operativa.

**Estado:** 🟡 **Parcial** — Mantenimiento e Inventario en producción · **Sprint 14 ALIGN:** ✅ Cerrado (2026-07-10)

| Estado | Significado |
|--------|-------------|
| ✅ Producción | Flujo implementado y verificado |
| 🟡 Parcial | Existe con limitaciones documentadas |
| 📋 Roadmap | Proceso planificado · no en producto |

→ Auditoría Sprint 14: [ALIGN · Fase 8](../../alignment/modules/09-workflows-audit.md)

### Matriz de implementación (Sprint 14)

| Sección | Tema | Estado |
|---------|------|--------|
| §1 | Filosofía | ✅ |
| §2 | Flujo mantenimiento | 🟡 |
| §3 | Incidencias | ✅ |
| §4 | Abastecimiento | 🟡 |
| §5 | Ventas | ✅ |
| §6 | Ciclo comercial | ✅ |
| §7 | Onboarding | ✅ |
| §8 | IAM | ✅ |
| §9 | Integración módulos | 🟡 |
| §10 | Procesos futuros | ✅ doc |
| §11 | Trazabilidad | 🟡 |
| §12 | Automatización | 🟡 |

**Gaps abiertos (📋):** Purchasing formal · CRM pipeline · repuestos OT preventiva · kardex UI · webhooks.

---

## 1 · Filosofía · ✅

Roustix está diseñado para trabajar mediante **procesos**.

En lugar de aplicaciones aisladas, cada módulo participa en un flujo continuo:

```
Activo
     │
     ▼
Incidencia
     │
     ▼
Orden de Trabajo
     │
     ▼
Consumo de repuestos
     │
     ▼
Indicadores
     │
     ▼
Dashboard
```

El objetivo es **reducir trabajo manual** y mantener **trazabilidad completa**.

→ [MRG-01 · Principios del producto](01-intro-filosofia.md)

---

## 2 · Flujo Mantenimiento · 🟡

> **Hoy en producto:** OT preventivas anuales y planeación mensual; consumo de repuestos al cerrar OT **correctiva** (`/inventario` técnico).

```
Activo registrado
        │
        ▼
Plan preventivo
        │
        ▼
Generación de OT
        │
        ▼
Asignación técnico
        │
        ▼
Trabajo realizado
        │
        ▼
Consumo de repuestos
        │
        ▼
Cierre OT
        │
        ▼
Historial del activo
```

Cada **Orden de Trabajo** incrementa automáticamente el **historial del activo** — base para KPIs técnicos (MTBF, cumplimiento preventivo, costos).

→ [MRG-02 · Mantenimiento](02-maintenance.md)

---

## 3 · Flujo de incidencias · ✅

> **Hoy en producto:** `POST /incidencias/<id>/crear-ot` vincula incidencia y OT; `POST /incidencias/<id>/resolver` cierra sin OT.

```
Usuario detecta problema
        │
        ▼
Registrar incidencia
        │
        ▼
Supervisor revisa
        │
        ├────────► Resuelta sin OT
        │
        ▼
Crear Orden de Trabajo
        │
        ▼
Proceso Mantenimiento
```

**No todas las incidencias generan una OT** — el supervisor decide si basta documentar la resolución o escalar a mantenimiento formal.

---

## 4 · Flujo de abastecimiento · 🟡

```
Producto bajo stock
        │
        ▼
Alerta
        │
        ▼
Compra
        │
        ▼
Entrada mercancía
        │
        ▼
Actualización de stock
```

En versiones futuras este flujo será gestionado por el módulo **Purchasing** (solicitud · OC · recepción parcial).

→ [MRG-04 · Compras](04-compras.md) · [MRG-03 · Inventario](03-inventario.md)

> **Hoy:** alerta en dashboard comercial · registro directo de compra en Inventory → stock + CxP.

---

## 5 · Flujo de ventas · ✅

```
Cliente
      │
      ▼
Venta
      │
      ▼
Salida de inventario
      │
      ▼
Cobro
      │
      ├────► Contado
      │
      └────► Crédito
                    │
                    ▼
                 Abonos
```

El inventario **siempre refleja las ventas confirmadas** — no se vende por encima del stock disponible (salvo configuración futura).

→ [MRG-05 · Ventas](05-ventas.md)

---

## 6 · Flujo completo comercial · ✅

```
Proveedor
      │
      ▼
Compra
      │
      ▼
Inventario
      │
      ▼
Venta
      │
      ▼
Cliente
      │
      ▼
Cobro
```

Este flujo representa el **ciclo básico** de abastecimiento y comercialización — el más frecuente en tenants con módulo Inventory.

---

## 7 · Flujo de incorporación (Onboarding) · ✅

```
Registro
      │
      ▼
Empresa
      │
      ▼
Administrador
      │
      ▼
Módulos
      │
      ▼
Datos ejemplo
      │
      ▼
Operación
```

Durante el **período de prueba** Roustix puede cargar información inicial según el **sector** del cliente (activos demo · productos ejemplo).

→ [MRG-07 · Administración](07-administracion.md) · `/onboarding`

---

## 8 · Flujo administrativo · ✅

```
Crear usuario
        │
        ▼
Asignar rol
        │
        ▼
Asignar módulos
        │
        ▼
Acceso al sistema
```

Los **permisos** determinan qué procesos puede ejecutar cada usuario — Maintenance, Inventory o ambos.

→ [MRG-07 · Roles](07-administracion.md)

---

## 9 · Integración entre módulos · 🟡

| Origen | Destino | Resultado |
|--------|---------|-----------|
| Mantenimiento | Reportes | KPIs técnicos |
| Inventario | Ventas | Salida de stock |
| Compras | Inventario | Entrada de mercancía |
| Administración | Todos | Control de permisos |
| CRM (roadmap) | Ventas | Conversión de oportunidad |

### Tenant mixto (Mantenimiento + Inventario)

| Escenario | Nota |
|-----------|------|
| Repuesto técnico vs producto comercial | Inventarios **separados** — sin transferencia automática |
| Proveedor servicio vs comercial | Entidades distintas |
| Dashboard | Según módulos activos — Mantenimiento y/o comercial |

---

## 10 · Procesos futuros · ✅ doc

Los siguientes flujos se incorporarán en versiones posteriores:

| Flujo | Estado |
|-------|--------|
| CRM → Cotización → Venta | 📋 |
| Compras → Cuentas por pagar (avanzado) | 🟡 CxP · pagos parciales hoy |
| Ventas → Facturación electrónica | 📋 |
| Inventario → Producción | 📋 |
| BI → Dashboards ejecutivos | 📋 |
| Integración externa vía API (MAG) | 🟡 Parcial |
| Webhooks operativos | 📋 |

→ [MPA-05 · Roadmap](/mpa/chapters/05-roadmap-modulos.md) · [MAG-08 · Webhooks](/mag/chapters/08-webhooks.md)

---

## 11 · Trazabilidad · 🟡

Cada proceso conserva su **historial**:

| Objeto | Historial |
|--------|-----------|
| **Activo** | OT · incidencias · repuestos · costos |
| **Producto** | Compras · ventas · movimientos de stock |
| **Venta** | Líneas · cobros · abonos |
| **Usuario** | Auditoría de acceso y acciones |
| **Empresa** | Cambios de configuración · actividad tenant |

La trazabilidad permite conocer **quién** realizó cada acción y **cuándo** ocurrió.

→ `TenantActivityLog` · historial por entidad en MRG-02 y MRG-05

---

## 12 · Automatización · 🟡

Roustix automatiza diversas tareas operativas:

| Automatización | Estado |
|----------------|--------|
| Generación / programación de OT preventivas | ✅ |
| Actualización automática de stock (compra / venta) | ✅ |
| Cálculo de indicadores en dashboard | ✅ |
| Alertas de stock mínimo | ✅ |
| Sincronización estados OT por fecha | ✅ |
| Recordatorios preventivos | 📋 |
| Automatización mediante Webhooks (MAG) | 📋 |
| Flujos CRM → venta | 📋 |

MRG define **qué** debe automatizarse; **MAG** y **MSD** entregan el **cómo** para integradores.

---

## Relación con otros capítulos

| Documento | Relación |
|-----------|----------|
| [MRG-02 · Mantenimiento](02-maintenance.md) | Flujo de mantenimiento |
| [MRG-03 · Inventario](03-inventario.md) | Flujo de inventario |
| [MRG-04 · Compras](04-compras.md) | Abastecimiento |
| [MRG-05 · Ventas](05-ventas.md) | Ventas y cobros |
| [MRG-08 · Reportes](08-reportes.md) | KPIs derivados de los procesos |
| [MAG](/mag/) | Automatización mediante API |
| [MUX · Journeys](/mux/journeys.md) | Recorridos por persona |

---

## Exit Criteria

Este capítulo se considera **implementado** cuando:

- [x] Procesos principales documentados
- [x] Trazabilidad entre módulos descrita
- [x] Flujos Mantenimiento e Inventario documentados
- [x] Procesos comerciales documentados
- [x] Procesos planificados del roadmap identificados
- [x] Flujos core verificados contra código (Sprint 14 · Fase 8)
- [ ] Diagramas operativos validados con implementadores
- [ ] Flujos CRM y Purchasing completos en producto

**Cobertura documental:** parcial — Mantenimiento + Inventario en producción.

---

## Filosofía del capítulo

Los módulos son importantes, pero el **verdadero valor** de Roustix aparece cuando trabajan juntos. Un activo genera mantenimiento, el mantenimiento consume inventario, el inventario requiere compras y toda la operación produce indicadores.

**MRG-09 documenta esa continuidad**, convirtiendo funcionalidades aisladas en **procesos empresariales completos**.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Workflow funcional** | 🟡 Mantenimiento + Inventario + flujos comerciales |
| **Sprint 14 ALIGN** | ✅ Cerrado 2026-07-10 |
| **MRG capítulo** | v1.0.1 |
| **Roadmap** | CRM · Purchasing formal · Finanzas |
| **Próximo paso** | MRG-10 · Buenas prácticas · cierre Sprint 14 |

---

→ [MRG-10 · Buenas prácticas](10-buenas-practicas.md) · [MRG-08 · Reportes](08-reportes.md) · [Índice MRG](/mrg/)
