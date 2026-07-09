# MTX-UX-COPY · Guía de copy en producto

Toda la plataforma habla con **una sola voz**. Este documento es la fuente para textos dentro de la UI.

Complementa [voice.md](voice.md) (tono) y [messaging.md](messaging.md) (alertas).

---

## Reglas generales

1. **Verbos en imperativo** en botones: «Guardar», «Crear», «Eliminar»
2. **Oraciones completas** en empty states y errores
3. **Nunca** jerga técnica HTTP/SQL al usuario final
4. **Maintix** con M mayúscula · no «MAINTIX» en prosa UI
5. Español latinoamericano neutro

---

## Botones

| ✅ Correcto | ❌ Incorrecto |
|-------------|---------------|
| Guardar cambios | Aceptar |
| Crear orden de trabajo | Enviar |
| Eliminar activo | OK |
| Cancelar | Abort |
| Exportar reporte | Submit |
| Invitar usuario | Confirm |

---

## Empty states

| ✅ Correcto | ❌ Incorrecto |
|-------------|---------------|
| No hay órdenes abiertas. | Sin datos. |
| No encontramos resultados. | Error. |
| Aún no hay activos registrados. | Lista vacía. |
| Cuando registres una OT, aparecerá aquí. | N/A |

**Plantilla:** [Qué es esta pantalla] + [Qué hacer] + CTA

---

## Errores de validación

| ✅ Correcto | ❌ Incorrecto |
|-------------|---------------|
| Revisa el código del activo. Formato: SECTOR-NUM | Campo inválido |
| Este correo ya está registrado. | Duplicate entry |
| Stock insuficiente en REF-002. | Error 422 |
| Completa los campos marcados en rojo. | Validation failed |

---

## Éxito

| ✅ Correcto | ❌ Incorrecto |
|-------------|---------------|
| Cambios guardados | Operación exitosa |
| Orden de trabajo #1042 creada | Success! |
| Invitación enviada a maria@empresa.com | Email dispatched |
| 48 registros importados | Import OK |

---

## Confirmaciones

| ✅ Correcto | ❌ Incorrecto |
|-------------|---------------|
| ¿Eliminar activo CPS-001? | ¿Está seguro? |
| Esta acción no se puede deshacer. | Warning |
| ¿Cerrar esta orden de trabajo? | Confirm action |

---

## Placeholders

| ✅ Correcto | ❌ Incorrecto |
|-------------|---------------|
| CPS-001 | Ingrese valor |
| maria@empresa.com | Email |
| Buscar activo o código… | Search… |

---

## Labels y campos

| ✅ Correcto | ❌ Incorrecto |
|-------------|---------------|
| Código de activo | asset_code |
| Orden de trabajo | OT ID |
| Stock disponible | qty |

---

## Estados operativos

| Estado | Copy UI |
|--------|---------|
| Operativo | Operativo |
| En mantenimiento | En mantenimiento |
| Falla | Falla |
| Stock crítico | Stock crítico |

Usar badges MDL · no inventar sinónimos por módulo.

---

## Checklist copy (PR)

- [ ] Botones revisados contra tabla
- [ ] Empty states con CTA
- [ ] Errores accionables (DEC-003)
- [ ] Sin «Error» genérico solo
- [ ] Alineado con MTX-UX-COPY

Ver también: Brand Book voz (MBB) para marketing · MUX voice para producto.
