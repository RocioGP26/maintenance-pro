# UX · Mensajes del sistema

Reglas para éxito, advertencia, error y ayuda. IDs **MTX-UX-MSG-***.

## Estructura universal

Todo mensaje operativo sigue:

```
[Qué pasó] + [Qué hacer ahora (si aplica)]
```

Máximo **2 oraciones** en toast/alert. Detalle en modal o enlace «Ver más».

---

## MTX-UX-MSG-SUCCESS · Éxito

**Tono:** Confirmación breve. Sin celebración excesiva.

| Situación | ✅ Copy | ❌ Evitar |
|-----------|---------|----------|
| Guardado | «Cambios guardados» | «¡Excelente! Tu registro fue almacenado» |
| OT creada | «Orden de trabajo #1042 creada» | «Success: 201 Created» |
| Venta | «Venta registrada · Factura #1024» | «Operación completada con éxito» |
| Usuario invitado | «Invitación enviada a maria@empresa.com» | «Email dispatched» |
| Importación | «48 registros importados · 2 con error» | Solo «Importación OK» |

**Duración toast:** 4 s · auto-dismiss · opción deshacer solo si es reversible inmediata.

---

## MTX-UX-MSG-WARNING · Advertencia

**Tono:** Calmo. No alarmista. Indica riesgo operativo, no culpa al usuario.

| Situación | ✅ Copy |
|-----------|---------|
| Stock bajo | «Stock crítico en REF-002 · Quedan 3 unidades» |
| OT vencida | «Preventivo vencido en CPS-001 · Programa mantenimiento» |
| Borrador | «Tienes cambios sin guardar» |
| Trial | «Quedan 5 días de prueba · Ver planes» |

**Componente MDL:** `mtx-alert-warning` · icono opcional · CTA secundario si hay acción.

---

## MTX-UX-MSG-ERROR · Error

**Tono:** Claro, sin culpar. Nunca stack trace al usuario final.

| Tipo | ✅ Copy | Detalle técnico |
|------|---------|-----------------|
| Validación | «Revisa el código del activo · Formato: SECTOR-NUM» | Log servidor |
| Permiso | «No tienes acceso a este módulo · Contacta al administrador» | 403 log |
| Red | «No pudimos conectar · Revisa tu internet e intenta de nuevo» | Retry |
| Conflicto | «Este código ya existe · Usa otro o edita el activo existente» | — |
| Sistema | «Algo salió mal · Intenta de nuevo o contacta soporte» | Sentry |

**Reglas:**

1. Decir **qué campo** o **qué acción** falló
2. Ofrecer **una** salida (corregir, reintentar, contactar)
3. Código de error interno solo en modo admin o soporte

---

## MTX-UX-MSG-HELP · Ayuda contextual

**Tono:** Docente, una idea por párrafo.

| Ubicación | Contenido |
|-----------|-----------|
| `mtx-form-hint` | Formato esperado, ejemplo |
| Tooltip | Una frase, max 120 caracteres |
| Empty state | Qué es esta pantalla + CTA primary |
| Panel ayuda | 3 bullets max + enlace a docs |

**Ejemplo empty state (OTs):**

```
Sin órdenes abiertas
Cuando registres una OT aparecerá aquí por prioridad.
[Nueva OT]
```

---

## MTX-UX-MSG-CONFIRM · Confirmación destructiva

Patrón MTX-PAT-007 (MDL).

```
Título: ¿Eliminar activo CPS-001?
Cuerpo: Esta acción no se puede deshacer. Se conservará el historial de OTs.
Primary (danger): Eliminar
Secondary: Cancelar
```

---

## Matriz semántica → MDL

| Tipo | Clase MDL | Color token |
|------|-----------|-------------|
| Éxito | `mtx-alert-success` / toast verde | `--mdl-success` |
| Advertencia | `mtx-alert-warning` | `--mdl-warning` |
| Error | `mtx-alert-danger` / input `is-error` | `--mdl-danger` |
| Info | `mtx-alert-info` | `--mdl-primary` |

---

## Checklist copy antes de merge

- [ ] ¿Usuario entiende qué pasó sin conocer el código?
- [ ] ¿Hay siguiente paso accionable?
- [ ] ¿Menos de 120 caracteres en toast?
- [ ] ¿Alineado con voz.md?
- [ ] ¿Probado con perfil principal (personas.md)?
