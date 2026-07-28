# 04 · Órdenes de trabajo

La **orden de trabajo (OT)** es el documento operativo de una intervención: quién la hace, sobre qué activo, con qué prioridad, tiempos, repuestos y costos.

**Menú:** `Mantenimiento → Órdenes → Listado` · `/ordenes`

---

## 1. Tipos de OT

| Tipo | Cuándo usarla |
|------|----------------|
| **Preventivo** | Según plan o cronograma, antes de la falla |
| **Correctivo** | Tras falla o deterioro detectado |
| **Emergencia** | Intervención urgente por riesgo o paro crítico |

### Ejecución

| Modo | Descripción |
|------|-------------|
| **Interno** | Técnico de la empresa |
| **Externo** | Proveedor de servicio |

---

## 2. Estados de una OT

| Estado | Significado |
|--------|-------------|
| **Programada** | Fecha futura; aún no inicia |
| **Abierta** | Lista para ejecutar (del día o pendiente inmediato) |
| **En proceso** | Trabajo en curso |
| **Vencida** | Pasó la fecha programada sin cierre |
| **Completado** | Técnico terminó; falta cierre administrativo |
| **Cerrada** | Finalizada; ya no se edita |

**Pendientes:** programada, abierta, en proceso, vencida.  
**Terminales:** completado, cerrada.

### Prioridad

Baja · media · alta · crítica — ordénala según impacto y criticidad del activo.

---

## 3. Crear una OT (supervisor / admin)

1. Ve a **Órdenes → Listado** y pulsa **Nueva** (`/ordenes/nueva`).  
   También puedes crearla desde una **incidencia**, desde **planeación** o desde un **cronograma**.
2. Selecciona el **activo**.
3. Elige **tipo**, **prioridad** y si la ejecución es **interna** o **externa**.
4. Describe el trabajo con claridad (síntoma, alcance, seguridad).
5. Asigna **técnico** o **proveedor de servicio**.
6. Define fecha programada si aplica.
7. Guarda. El estado típico inicial es **programada** o **abierta**.

---

## 4. Ejecutar una OT (técnico)

1. Abre **Mis órdenes de trabajo** o la OT asignada en `/ordenes/<id>/editar`.
2. Pasa el estado a **En proceso** cuando inicies.
3. Registra **jornadas** (tiempos de trabajo). El sistema calcula mano de obra con la tarifa hora vigente al momento de guardar.
4. Si aplica, registra **repuestos** consumidos (descuentan stock técnico).
5. Completa **checklist / procedimiento** si la OT lo exige.
6. Anota observaciones, herramientas u otros costos según el formulario.
7. Solicita finalización → estado **Completado**.

> El técnico **no** hace el cierre definitivo. Eso lo confirma un supervisor o administrador.

---

## 5. Cerrar una OT (supervisor / admin)

1. Revisa que jornadas, repuestos y evidencias estén completos.
2. Verifica costos (mano de obra + repuestos + herramientas + servicio externo).
3. Cambia a **Cerrada**.
4. La OT queda en el historial del activo y alimenta indicadores.

Una vez **cerrada**, no debe editarse. Si hay un error grave, sigue el procedimiento interno de tu empresa (reapertura o corrección documentada).

---

## 6. Costos que acumula la OT

| Componente | Origen |
|------------|--------|
| Mano de obra | Horas de jornada × tarifa del técnico |
| Repuestos | Cantidad × costo unitario al consumir |
| Herramientas | Uso / alquiler / desgaste informado |
| Servicio externo | Costo del proveedor (ejecución externa) |

**Costo total OT** = suma de esos componentes.

---

## 7. Planeación mensual

**Menú:** `Órdenes → Planeación` · `/ordenes/planeacion`

Sirve para programar la carga del mes (horas o actividades preventivas) y generar o revisar OT derivadas del plan.

---

## 8. Procedimientos y automatizaciones

| Opción | Ruta | Uso |
|--------|------|-----|
| Procedimientos | `/maintenance/procedures/` | Checklists y procedimientos ligados a la ejecución |
| Automatizaciones | `/maintenance/automation/` | Reglas que generan o impulsan trabajo sin carga manual |

Úsalos cuando tu operación ya tiene planes estables; no sustituyen la asignación ni el cierre humano.

---

## 9. Proveedores de servicio

**Menú:** `Mantenimiento → Proveedores de servicio` · `/proveedores`

Registra terceros que ejecutan OT externas. Al crear la OT en modo externo, selecciónalos como ejecutores.

→ Siguiente: [Preventivo y calendario](05-preventivo-y-calendario.md)
