# MDL · Patrones

**El corazón del MDL.** Los patrones describen **flujos completos**, no piezas aisladas.

Un patrón combina componentes `MTX-*`, copy, estados y reglas de negocio.

## Registro de patrones

| ID | Patrón | Componentes clave |
|----|--------|-------------------|
| MTX-PAT-001 | Registrar OT | Form, Select activo, Primary btn, Toast |
| MTX-PAT-002 | Buscar Activo | Input búsqueda, Table, Empty state |
| MTX-PAT-003 | Crear Venta | Form multi-sección, Table líneas, Modal confirm |
| MTX-PAT-004 | Crear Cliente | Form, Modal o página, Success alert |
| MTX-PAT-005 | Importar Excel | Upload zone, Progress loader, Result table |
| MTX-PAT-006 | Eliminar Registro | Danger btn, Modal confirm, Alert success |
| MTX-PAT-007 | Confirmar Acción | Modal, Primary + Ghost btn |

---

## MTX-PAT-001 · Registrar OT

```
Seleccionar activo → Describir falla → Asignar prioridad → Guardar
```

| Paso | UI |
|------|-----|
| 1 | `MTX-SEL-001` o búsqueda de activo |
| 2 | `MTX-INP-002` descripción |
| 3 | `MTX-BDG-001` prioridad visual |
| 4 | `MTX-BTN-001` Guardar OT |

**Primary:** un solo botón "Crear OT" al final.  
**Empty:** si no hay activos, `MTX-EMP-001` con CTA a crear activo.

---

## MTX-PAT-002 · Buscar Activo

```
Input búsqueda → Resultados en tabla → Detalle / acción
```

- Debounce 300ms en búsqueda (no motion token — lógica)
- Sin resultados: empty state con sugerencia de filtros
- Tabla: `MTX-TBL-001` con máximo 50 filas visibles + paginación

---

## MTX-PAT-005 · Importar Excel

```
Seleccionar archivo → Validar → Preview → Confirmar importación
```

| Fase | Feedback |
|------|----------|
| Upload | `MTX-LDR-001` |
| Error fila | `MTX-ALT-001` warning + tabla errores |
| Éxito | Alert success + link a registros creados |

---

## MTX-PAT-007 · Confirmar Acción

Patrón transversal para cualquier acción irreversible o crítica.

```
Trigger → Modal MTX-MDL-001 → Primary confirma / Ghost cancela
```

- Título en imperativo: "¿Eliminar activo CPS-001?"
- Cuerpo: consecuencia en una línea
- Destructivo: `MTX-BTN-005` en lugar de primary

---

## Cómo documentar un patrón nuevo

1. Asignar ID `MTX-PAT-NNN`
2. Diagrama de flujo (pasos)
3. Tabla componentes por paso
4. Estados de error y empty
5. Ejemplo Jinja de referencia
6. Entrada en este archivo + `changelog.md`
