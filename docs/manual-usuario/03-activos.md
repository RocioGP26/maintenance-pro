# 03 · Activos

Los **activos** son equipos, máquinas o instalaciones que mantienes. Toda la operación (OT, preventivos, costos e historial) gira alrededor de ellos.

**Menú:** `Mantenimiento → Activos → Listado` · ruta `/activos`

---

## 1. Estados del activo

| Estado | Significado |
|--------|-------------|
| **Operativo** | En servicio normal |
| **En mantenimiento** | Intervención programada o en curso |
| **En falla** | Detenido por avería |

### Criticidad

| Nivel | Uso típico |
|-------|------------|
| Baja | Impacto limitado |
| Media | Impacto moderado |
| Alta | Impacto significativo en producción |
| Crítica | Parada mayor si falla |

---

## 2. Crear un activo

1. Ve a **Activos → Listado**.
2. Pulsa **Nuevo** (`/activos/nuevo`).
3. Completa al menos:
   - Nombre / código
   - **Tipo de activo** (debe existir antes; ver §4)
   - Ubicación
   - Criticidad
   - Estado inicial (normalmente **Operativo**)
4. Completa campos del sector o **campos personalizados** si tu empresa los usa.
5. Guarda.

Luego puedes abrir la ficha para editar, ver hoja de vida, ficha técnica y cronogramas.

---

## 3. Consultar y editar

1. En el listado, busca por nombre, código, ubicación o estado.
2. Abre el activo.
3. Usa **Editar** para corregir datos maestros.
4. Revisa el **historial** (OT e intervenciones) antes de tomar decisiones de reposición o baja operativa.

> La baja formal definitiva puede gestionarse según la política de tu empresa; sigue el procedimiento interno acordado con tu administrador.

---

## 4. Tipos de activo

**Menú:** `Activos → Tipos` · `/activos/tipos`

Los tipos agrupan equipos similares (bomba, compresor, vehículo, HVAC, etc.) y condicionan campos y planes.

1. Crea el tipo con un nombre claro.
2. Asocia activos nuevos a ese tipo.
3. Evita duplicar tipos con nombres casi iguales; complica reportes y filtros.

---

## 5. Cronogramas del activo

Desde la ficha del activo o **Activos → Cronogramas** puedes definir o revisar la programación preventiva ligada al equipo.

→ Detalle operativo: [Preventivo y calendario](05-preventivo-y-calendario.md)

---

## 6. Asset Health

**Menú:** `Activos → Asset Health` · `/maintenance/asset-health/`

Vista de salud / condición de activos para priorizar intervención. Úsala junto con criticidad y OT abiertas, no como único criterio.

---

## 7. Buenas prácticas

- Codifica activos de forma estable (no renombres códigos a menudo).
- Mantén la ubicación actualizada al mover equipos.
- Marca **En falla** apenas confirmes paro; facilita prioridad en Inicio.
- Revisa garantías próximas a vencer desde el panel de Inicio.

→ Siguiente: [Órdenes de trabajo](04-ordenes-de-trabajo.md)
