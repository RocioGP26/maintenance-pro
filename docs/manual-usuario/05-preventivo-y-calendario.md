# 05 · Preventivo y calendario

El mantenimiento **preventivo** reduce fallas programando intervenciones antes de que el activo se detenga.

---

## 1. Conceptos

| Concepto | Función |
|----------|---------|
| **Plan / cronograma** | Actividad + frecuencia asociada a un activo |
| **Planeación mensual** | Metas y OT del mes |
| **Calendario** | Vista temporal de lo programado |
| **Cumplimiento** | % de preventivos hechos a tiempo (en Análisis) |

---

## 2. Definir un plan en el activo

1. Abre el activo en **Activos → Listado**.
2. Entra a su **cronograma** (`/activos/<id>/cronograma`) o usa **Activos → Cronogramas**.
3. Define la actividad, frecuencia y responsables según el formulario.
4. Guarda y verifica que quede activo.

Prioriza primero los activos de criticidad **alta** y **crítica**.

---

## 3. Generar y seguir OT preventivas

1. Desde el cronograma, la **planeación mensual** (`/ordenes/planeacion`) o las **automatizaciones**, genera las OT del período.
2. Revisa que cada OT tenga activo, fecha y técnico o proveedor.
3. Sigue la ejecución igual que cualquier OT ([Órdenes de trabajo](04-ordenes-de-trabajo.md)).
4. Cierra a tiempo para no acumular **vencidas**.

---

## 4. Calendario

**Menú:** `Mantenimiento → Calendario` · `/calendario`

1. Abre el calendario para ver OT programadas en el período.
2. Identifica días sobrecargados y reasigna si hace falta.
3. Cruza con Inicio: **Preventivos de hoy**.

---

## 5. Medir cumplimiento

En **Inteligencia → Análisis → Mantenimiento** consulta el cumplimiento preventivo y el volumen de OT por tipo.

Si el % baja de forma sostenida:

- hay más correctivos de los previstos,
- falta capacidad (técnicos),
- o los planes están mal dimensionados.

Ajusta frecuencia, recursos o criticidad con el administrador.

→ Siguiente: [Incidencias](06-incidencias.md)
