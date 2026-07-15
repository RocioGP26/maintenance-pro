# MRG-02-MAINT · Mantenimiento

**Código:** MRG-02-MAINT · Sprint 10.2 · **Entregado**

> El módulo **Mantenimiento** (CMMS) gestiona activos, órdenes de trabajo, mantenimiento preventivo, repuestos técnicos e incidencias — el núcleo operativo para plantas, flotas y equipos críticos.

---

## Objetivo del capítulo

Documentar el funcionamiento funcional del módulo Mantenimiento: entidades, roles, estados, flujos, costos e indicadores — y su relación con otros módulos de Maintix.

**Clave de módulo:** `mantenimiento` · **Estado producto:** 🟡 Parcial · **Sprint 14 ALIGN:** ✅ Cerrado (2026-07-10)

| Estado | Significado |
|--------|-------------|
| ✅ Producción | Implementado y alineado con este manual |
| 🟡 Parcial | Implementado · gaps menores documentados |
| 📋 Roadmap | Documentado · no implementado |
| ❌ No implementado | Ausente en código |

→ Auditoría Sprint 14: [ALIGN · Fase 1](../../alignment/modules/02-maintenance-audit.md)

### Matriz de implementación (post Sprint 14)

| Sección | Tema | Estado |
|---------|------|--------|
| §1 | Alcance | ✅ |
| §2 | Roles y permisos | ✅ |
| §3 | Entidades | ✅ |
| §4 | Activos | 🟡 |
| §5 | Historial del activo | 🟡 |
| §6 | Órdenes de trabajo | 🟡 |
| §7 | Mantenimiento preventivo | ✅ |
| §8 | Inventario técnico (repuestos) | ✅ |
| §9 | Incidencias | 🟡 |
| §10 | Dashboard | ✅ |
| §11 | Indicadores / reportes | 🟡 |
| API | MAG `/api/v1/maintenance/*` | 🟡 |

**Gaps abiertos (📋):** jerarquía activo padre/hijo · baja formal de activo · estado OT «En espera» · export Excel OT/activos · CRUD API assets/OT · evidencia fotográfica incidencias.

---

## 1 · Alcance del módulo · ✅

| Incluye | No incluye (hoy) |
|---------|------------------|
| Activos y jerarquía | Inventario comercial (→ MRG-03) |
| Órdenes de trabajo | Compras de mercancía para reventa |
| Mantenimiento preventivo | CRM |
| Repuestos técnicos | Contabilidad formal (→ Finance · roadmap) |
| Incidencias | BI avanzado |
| Proveedores de **servicio** | |

---

## 2 · Roles del módulo · ✅

Quién participa en la operación de Mantenimiento — base para permisos en [MRG-07 · Administración](07-administracion.md):

| Rol | Función |
|-----|---------|
| **Administrador** | Configura activos, planes preventivos, técnicos y campos personalizados |
| **Supervisor** | Planea OT, asigna técnicos o proveedores, supervisa cumplimiento |
| **Técnico** | Ejecuta OT, registra jornadas, repuestos y cierre operativo |
| **Solicitante** | Reporta incidencias y solicita intervención (rol Usuario o equivalente) |
| **Proveedor externo** | Ejecuta OT contratadas (ejecución externa vía proveedor de servicio) |

### Correspondencia con roles Maintix

| Rol MRG | Rol plataforma | Notas |
|---------|----------------|-------|
| Administrador | Admin · Superadmin | Configuración y catálogos |
| Supervisor | Admin · Técnico senior | Campo supervisor en OT |
| Técnico | Técnico | Edición de OT asignadas |
| Solicitante | Usuario | Incidencias · lectura |
| Proveedor externo | — (tercero) | Referenciado en OT externa, sin login propio hoy |

---

## 3 · Entidades principales · ✅

| Entidad | Descripción funcional |
|---------|----------------------|
| **Activo** | Equipo, máquina o instalación con estado operativo, ubicación y criticidad |
| **Tipo de activo** | Categoría según sector (bomba, compresor, vehículo…) |
| **Campo personalizado** | Atributos extendidos por sector y categoría |
| **Ubicación** | Dónde está físicamente el activo (planta, línea, bodega) |
| **Criticidad** | Prioridad operativa (baja · media · alta · crítica) |
| **Orden de trabajo (OT)** | Trabajo correctivo, preventivo o de emergencia sobre un activo |
| **Técnico** | Recurso interno que ejecuta OT |
| **Proveedor de servicio** | Tercero que ejecuta OT externa |
| **Repuesto** | Pieza del inventario **técnico** consumible en OT |
| **Plan preventivo** | Programa de actividades periódicas por activo |
| **Incidencia** | Reporte de falla o anomalía, convertible en OT |

---

## 4 · Activos · 🟡

### Estados operativos

| Estado | Significado |
|--------|-------------|
| Operativo | En servicio normal |
| En mantenimiento | Intervención programada o en curso |
| En falla | Detenido por avería |

### Ciclo de vida del activo

```
Registro
      │
      ▼
Operación
      │
      ▼
Preventivos
      │
      ▼
Correctivos
      │
      ▼
Historial
      │
      ▼
Retiro / Baja
```

| Fase | Descripción |
|------|-------------|
| **Registro** | Alta con tipo, campos del sector, ubicación y criticidad |
| **Operación** | Servicio normal; monitoreo de estado y horas |
| **Preventivos** | Planes y OT programadas según frecuencia |
| **Correctivos** | OT por falla, incidencia o emergencia |
| **Historial** | Acumulación de OT, costos e intervenciones |
| **Retiro / Baja** | Fin de vida útil — desactivación o baja lógica del activo |

> **Hoy en producto:** estados operativos en ficha de activo; **retiro/baja** como práctica operativa (política del tenant) — formalización de baja definitiva en 📋 roadmap. **Jerarquía padre/hijo:** modelo en BD · UI en 📋 roadmap.

### Criticidad y activos críticos

| Nivel | Uso |
|-------|-----|
| Baja | Impacto limitado en la operación |
| Media | Impacto moderado |
| Alta | Impacto significativo en producción |
| Crítica | Parada mayor si falla |

Los activos con criticidad **Alta** o **Crítica** (o marcados como críticos) pueden generar:

- reglas especiales de mantenimiento preventivo
- alertas prioritarias en dashboard
- priorización de órdenes de trabajo e incidencias

La criticidad explica **por qué** algunos equipos reciben atención preferente — no es solo un campo descriptivo.

### Jerarquía

Los activos pueden organizarse **padre/hijo** (línea → subequipo) para reportes y planeación.

---

## 5 · Historial del activo · 🟡

Cada activo mantiene un **historial único** que registra:

- órdenes de trabajo (correctivas, preventivas, emergencia)
- incidencias vinculadas
- preventivos ejecutados y cumplimiento
- repuestos utilizados por OT
- cambios de ubicación y estado operativo
- costos acumulados (mano de obra · repuestos · servicios externos)

Este historial constituye la **trazabilidad operativa** del activo — funcionalidad central de cualquier CMMS y base para indicadores como MTBF y costo por equipo.

> **Hoy en producto:** ficha de activo muestra últimas OT e incidencias vinculadas. Costos agregados por activo y cambios de ubicación en 📋 roadmap.

→ Workflow completo en [MRG-09 · Workflows](09-workflows.md)

---

## 6 · Órdenes de trabajo · 🟡

### Tipos

| Tipo | Origen |
|------|--------|
| Correctiva | Falla detectada o incidencia |
| Preventiva | Plan programado |
| Emergencia | Parada crítica |

### Ciclo de vida

Modelo funcional completo de una OT en Maintix:

```
Programada
     │
Asignada
     │
En proceso
     │
En espera
     │
Completada
     │
Cerrada
```

| Estado | Significado |
|--------|-------------|
| **Programada** | Fecha futura; aún no iniciada |
| **Asignada** | Técnico o proveedor designado; pendiente de inicio |
| **En proceso** | Trabajo en curso; jornadas registradas |
| **En espera** | Pausada — repuestos, aprobación o proveedor pendiente |
| **Completada** | Trabajo terminado; pendiente de cierre administrativo |
| **Cerrada** | OT finalizada y archivada |

Estados transversales:

| Estado | Cuándo |
|--------|--------|
| **Abierta** | OT del día o vencida sin iniciar — lista para ejecutar |
| **Vencida** | Fecha programada superada sin cierre |

> **Hoy en producto:** `programada` · `abierta` · `en_proceso` · `vencida` · `completado` · `cerrada`. **Asignada** se refleja al designar técnico/proveedor en OT abierta. **En espera** — roadmap explícito; hoy se gestiona operativamente dentro de `en_proceso` con observaciones.

### Contenido de una OT

- Activo objetivo
- Descripción del trabajo
- Técnico interno o proveedor externo asignado
- Supervisor (opcional)
- **Jornadas** — sesiones de trabajo con tiempos
- **Repuestos consumidos** — descuenta stock técnico
- **Costos registrados** (ver abajo)
- Observaciones, autorización y cierre

### Costos registrados

Cada OT puede acumular costos que alimentan indicadores y, en el futuro, el módulo **Finance**:

| Componente | Origen |
|------------|--------|
| **Mano de obra** | Jornadas · tiempo registrado por técnico |
| **Repuestos** | Líneas de consumo × costo unitario del repuesto |
| **Servicios externos** | Costo estimado / real de OT con proveedor |
| **Costos adicionales** | Otros conceptos en costo real vs estimado |

La tarifa hora se configura en **Administración → Usuarios y roles**. Al guardar
una jornada, Maintix conserva la tarifa aplicada en ese momento y calcula
`duración en horas × tarifa hora`; los cambios futuros de tarifa no modifican
el costo histórico de la jornada.

Los costos por activo se agregan en el **historial** y conectan Maintenance con reportes (MRG-08) y finanzas (roadmap).

---

## 7 · Mantenimiento preventivo · ✅

| Concepto | Función |
|----------|---------|
| **Plan preventivo** | Actividad + frecuencia por activo |
| **Planeación mensual** | Metas de horas o actividades por mes |
| **Calendario** | Vista temporal de OT programadas |
| **Cumplimiento** | KPI en dashboard (% preventivos a tiempo) |

El sistema **genera y programa OT preventivas** a partir de planes activos y sincroniza estados según fechas.

---

## 8 · Inventario técnico (repuestos) · ✅

Distinto del **inventario comercial** (MRG-03):

| Aspecto | Repuesto técnico |
|---------|------------------|
| Uso | Consumo en OT de Maintenance |
| Alerta | Bajo stock mínimo |
| Unidad | Piezas, filtros, consumibles |
| Costo | Costo unitario → línea en OT |
| Proveedor | Reposición manual hoy |

---

## 9 · Incidencias · 🟡

Flujo:

1. **Solicitante** reporta incidencia (área, prioridad, equipo detenido)
2. **Supervisor** revisa y asigna
3. Resolución documentada
4. Opcional: **crear OT** vinculada desde la incidencia

La prioridad de la incidencia puede interactuar con la **criticidad del activo** para ordenar la respuesta.

> **Hoy en producto:** reporte · enrutamiento al área responsable · notificación individual a coordinadores/técnicos autorizados · listado · resolución · crear OT desde incidencia. Evidencia fotográfica permanece en 📋 roadmap.

### Notificaciones por área

Al registrar o reasignar una incidencia, Maintix crea una entrega individual para cada usuario que cumpla simultáneamente estas reglas:

- pertenece a la misma empresa de la incidencia;
- su área coincide con el área responsable (incluyendo alias normalizados como TIC/Sistemas);
- tiene un rol autorizado para gestionar incidencias;
- está activo y no está bloqueado.

El modal muestra una sola vez cada entrega. Cerrarlo registra que ya fue mostrado, pero no elimina el pendiente de la campana. **Ver incidencia** marca lectura y acceso; **Marcar como vista** registra únicamente la lectura. La combinación incidencia + usuario es única y cada transición conserva su fecha para auditoría.

La interfaz consulta pendientes mediante polling cada 45 segundos; no depende de WebSockets y nunca distribuye una alerta a toda la empresa.

Para el rol **Solicitante/Reportante**, la campana se limita a sus propios tickets pendientes. Las alertas de vencimientos, trabajos programados y OT en proceso quedan reservadas al personal operativo.

---

## 10 · Inicio · Centro de Operaciones · ✅

Inicio es el panel operativo diario. Su pregunta rectora es **«¿Qué requiere mi atención hoy?»** y no contiene indicadores históricos de BI.

```
Inicio · Centro de Operaciones
│
├── OT abiertas
├── OT vencidas
├── Preventivos de hoy
├── Incidencias nuevas y abiertas
├── Repuestos bajo mínimo
├── Activos fuera de servicio
├── Garantías por vencer
└── Actividad reciente
```

| Bloque | Qué responde |
|--------|--------------|
| **OT abiertas** | Carga de trabajo pendiente |
| **OT vencidas** | OT fuera de fecha programada |
| **Preventivos de hoy** | Intervenciones que deben ejecutarse durante la jornada |
| **Incidencias** | Reportes nuevos y casos aún sin cerrar |
| **Repuestos bajo mínimo** | Riesgo de paro por falta de piezas |
| **Activos fuera de servicio** | Equipos en mantenimiento o falla que requieren seguimiento |
| **Garantías** | Coberturas que vencen en los próximos 30 días |
| **Actividad reciente** | Últimas OT creadas o actualizadas para recuperar contexto |

Los KPI estratégicos de planta se consultan en **Análisis → Mantenimiento**.

---

## 11 · Indicadores (Mantenimiento) · 🟡

La ruta `/analisis/mantenimiento` conserva el panel estratégico con filtros por período, sector, ubicación y activo. La ruta `/analisis` funciona como directorio de inteligencia para mantenimiento, costos, reportes, inventario comercial y Purchasing.

| KPI | Descripción |
|-----|-------------|
| Activos por estado | Operativo vs mantenimiento vs falla |
| OT por tipo y estado | Correctivas · preventivas · vencidas |
| Cumplimiento preventivo | % OT preventivas en fecha |
| MTBF / MTTR | Tiempo entre fallas · tiempo de reparación |
| Repuestos bajo mínimo | Alertas de reposición |
| Costo por activo / OT | Mano de obra + repuestos + herramientas + servicio externo, cuando aplique |

### Costos de la orden de trabajo

Cada OT conserva un desglose económico común para el análisis de costos y la hoja de vida del activo:

`Costo total OT = mano de obra + repuestos + herramientas + servicio externo`

- **Mano de obra:** horas de las jornadas × tarifa histórica del técnico.
- **Repuestos:** cantidad consumida × costo unitario fijado al registrar el consumo.
- **Herramientas:** suma del uso, alquiler o desgaste informado en cada jornada de la OT.
- **Servicio externo:** costo real del proveedor, únicamente cuando la ejecución es externa.

En mantenimientos distintos al correctivo, el modal de jornada presenta el costo de herramientas, calcula la MDO con `duración × tarifa hora` y muestra el total de la jornada como `herramientas + MDO`. Ambos valores calculados son de solo lectura.

Cuando una OT es ejecutada por un proveedor externo, la MDO de la jornada es editable para registrar el valor informado por el proveedor; el total continúa calculándose automáticamente. En la ejecución interna la MDO permanece derivada de la tarifa del usuario técnico.

En las OT correctivas, el modal presenta herramientas, repuestos y MDO. El costo de repuestos se obtiene de las líneas asociadas a la intervención y el total de jornada se calcula como `herramientas + repuestos + MDO`.

La tarifa del técnico y el costo unitario del repuesto se guardan como snapshots para que cambios posteriores en usuarios o inventario no modifiquen el costo histórico del activo.

→ Detalle en [MRG-08 · Reportes](08-reportes.md)

---

## Relación con otros capítulos

| Capítulo | Relación |
|----------|----------|
| MRG-07 | Roles · permisos · configuración |
| MRG-08 | Dashboard · KPIs · exportaciones |
| MRG-09 | Workflow activo → OT → repuesto → costo → KPI |
| MRG-01 | Modularidad · Mantenimiento en producción |
| MAG | Contrato `/api/v1/maintenance/*` · 🟡 GET assets/work-orders |
| MUX | Persona PER-003 Técnico · journeys operativos |

---

## Exit Criteria

Este capítulo se considera **alineado (Sprint 14)** cuando:

- [x] Alcance y roles del módulo documentados
- [x] Ciclo de vida del activo y OT descritos
- [x] Historial · costos · criticidad · dashboard conceptuales
- [x] Alineación UI/copy/menús vs producto (Sprint 14 · Fase 1)
- [x] Matriz de permisos MRG §2 ↔ plataforma
- [x] API MAG v1 lectura (`assets` · `work-orders`)
- [ ] Validación con implementadores y soporte
- [ ] CRUD API Maintenance · exportaciones Excel OT/activos

**Cobertura documental:** ✅ entregada · **Implementación:** 🟡 Parcial (gaps en matriz §4–§6 · API).

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Módulo producto** | 🟡 Parcial |
| **Sprint 14 ALIGN** | ✅ Cerrado 2026-07-10 |
| **Cobertura documental** | ✅ v1.0.2 |
| **API MAG** | 🟡 GET v1 · CRUD 📋 |
| **MRG capítulo** | v1.0.2 |
| **Próximo paso** | Fase 2 · MRG-03 Inventario ([ALIGN](../../alignment/)) |

---

→ [MRG-03 · Inventario](03-inventario.md) · [MRG-07 · Administración](07-administracion.md) · [MRG-01 · Intro](01-intro-filosofia.md) · [Índice MRG](/mrg/)
