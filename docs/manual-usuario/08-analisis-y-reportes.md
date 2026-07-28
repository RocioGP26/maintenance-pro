# 08 · Inicio, análisis y reportes

## 1. Inicio · Centro de operaciones

**Ruta:** `/dashboard`

Responde: **¿Qué requiere mi atención hoy?** No es un panel histórico de BI.

| Bloque | Qué te dice |
|--------|-------------|
| OT abiertas | Carga pendiente |
| OT vencidas | Trabajo fuera de fecha |
| Preventivos de hoy | Intervenciones de la jornada |
| Incidencias | Reportes nuevos o abiertos |
| Repuestos bajo mínimo | Riesgo de paro por falta de piezas |
| Activos fuera de servicio | Equipos en mantenimiento o falla |
| Garantías por vencer | Coberturas en los próximos 30 días |
| Actividad reciente | Últimos movimientos para contexto |

**Rutina recomendada (supervisor):** abre Inicio al comenzar el turno → atiende vencidas e incidencias → reparte OT del día → revisa stock crítico.

El **técnico** ve un Inicio centrado en sus OT, prioridades y agenda.

---

## 2. Directorio de inteligencia

**Menú:** `Inteligencia → Análisis` · `/analisis`

Desde aquí eliges el tipo de análisis:

| Vista | Ruta | Contenido |
|-------|------|-----------|
| Mantenimiento | `/analisis/mantenimiento` | Estados, tipos de OT, cumplimiento, MTBF/MTTR |
| Costos | `/mantenimiento/analisis-costos` | Desglose económico por OT |
| Reportes | `/reportes` | Gráficos y exportación |
| Inventario / Purchasing | según módulos | Indicadores comerciales y de compras |

---

## 3. Indicadores clave de mantenimiento

| Indicador | Lectura práctica |
|-----------|------------------|
| Activos por estado | ¿Cuánta planta está operativa? |
| OT por tipo y estado | Balance preventivo vs correctivo |
| Cumplimiento preventivo | Disciplina del plan |
| MTBF | Tiempo medio entre fallas |
| MTTR | Tiempo medio de reparación |
| Costo por activo / OT | Dónde se va el presupuesto |

Filtra por período, ubicación o activo antes de tomar decisiones.

---

## 4. Exportar información

En **Reportes** (`/reportes`) puedes visualizar gráficos y exportar información de OT/activos cuando la opción esté disponible en tu plan.

Usa exportaciones para juntas semanales; el día a día resuélvelo en Inicio y en el listado de OT.

→ Siguiente: [Administración del equipo](09-administracion.md)
