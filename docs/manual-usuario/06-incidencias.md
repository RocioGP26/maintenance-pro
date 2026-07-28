# 06 · Incidencias

Una **incidencia** es el reporte de una falla, anomalía o solicitud de intervención. No siempre genera una OT: el supervisor decide si se resuelve en sitio o se escala.

**Reportar:** `/incidencia` · **Listado:** `/incidencias`

---

## 1. Reportar (solicitante u operativo)

1. Abre **Reportar incidencia** (o el acceso equivalente en tu menú).
2. Indica:
   - Área responsable
   - Prioridad
   - Descripción clara del problema
   - Activo afectado (si lo conoces)
   - Si el equipo está detenido
3. Envía el reporte.

Recibirás notificaciones cuando el estado de *tu* incidencia cambie (asignación, resolución, cierre, etc.).

---

## 2. Atender (supervisor / técnico autorizado)

1. Abre **Incidencias** o la notificación de la campana.
2. Revisa prioridad, activo y descripción.
3. Actualiza el estado según el avance (recibido, asignado, en atención…).
4. Elige un camino:

### A. Resolver sin OT

Si el problema se corrige sin orden formal:

1. Documenta la solución.
2. Usa la acción de **resolver**.
3. Cierra cuando corresponda.

### B. Crear OT desde la incidencia

1. En la ficha (`/incidencias/<id>`) usa **Crear orden de trabajo**.
2. Completa la OT vinculada.
3. Sigue el flujo de ejecución y cierre de OT.
4. La incidencia queda relacionada con esa intervención.

---

## 3. Estados habituales

El ciclo típico va de **reportado** → **recibido** → **asignado** → **en atención** → **resuelto** / **cerrado**. También puede **cancelarse** o quedar pendiente de OT, repuesto o usuario según el caso.

Mantén el estado al día: alimenta la campana del reportante y el panel de Inicio.

---

## 4. Notificaciones por área

Al crear o reasignar una incidencia, Roustix avisa a usuarios que:

- pertenecen a la misma empresa,
- tienen el **área** responsable (o alias equivalentes),
- tienen rol autorizado para gestionar incidencias,
- están activos.

No se envía un aviso masivo a toda la empresa.

Para el **solicitante**, la campana se limita a sus propios tickets.

---

## 5. Buenas prácticas

- Describe el síntoma, no solo “no funciona”.
- Indica si hay riesgo de seguridad o paro de línea.
- No abras OT duplicadas: primero busca incidencias abiertas del mismo activo.
- Cierra o cancela tickets obsoletos para no ensuciar el backlog.

→ Siguiente: [Repuestos técnicos](07-repuestos.md)
