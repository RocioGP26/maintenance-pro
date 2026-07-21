# Sprint 20 · Contratos y seguridad

## Estados de ejecución

| Estado | Significado |
|---|---|
| `succeeded` | Condición válida y acción completada |
| `skipped` | No coincidió, no hubo cruce o existe enfriamiento activo |
| `failed` | La condición coincidió, pero la acción no pudo completarse |

## Acciones permitidas

- `notify`: aviso interno para administradores y/o supervisores.
- `create_work_order`: OT correctiva, preventiva o de emergencia, con técnico opcional.

No existe acción que ejecute código, SQL, URLs o plantillas libres.

## Permisos

| Acción | Técnico | Supervisor | Administrador |
|---|:---:|:---:|:---:|
| Configurar regla | — | ✅ | ✅ |
| Activar/desactivar | — | ✅ | ✅ |
| Consultar ejecuciones | — | ✅ | ✅ |
| Recibir aviso propio | ✅ | ✅ | ✅ |
| Marcar aviso como leído | ✅ propio | ✅ propio | ✅ propio |

Toda consulta y mutación valida `empresa_id`. Los avisos se filtran además por
`user_id`; una URL conocida no concede acceso a otra entrega.
