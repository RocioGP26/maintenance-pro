# Sprint 16 · Contratos

## Estados

### Solicitud

```text
borrador → enviada → aprobada → convertida
              └────→ rechazada
borrador/enviada ──→ cancelada
```

### Orden de compra

```text
borrador → emitida → enviada → parcial → recibida → cerrada
     └──────────────→ cancelada
```

### Recepción

```text
borrador → confirmada
        ├→ parcial (resultado de líneas)
        └→ rechazada
```

No se permiten saltos silenciosos. Cada transición valida estado origen, permiso, tenant y precondiciones; luego registra `PurEvento`.

## Permisos 16.0

| Capacidad | Usuario | Técnico/Vendedor | Admin | Superadmin |
|---|---:|---:|---:|---:|
| Consultar | ✅ | ✅ | ✅ | ✅ |
| Crear solicitud propia | ✅ | ✅ | ✅ | ✅ |
| Editar borrador propio | ✅ | ✅ | ✅ | ✅ |
| Enviar solicitud | ✅ | ✅ | ✅ | ✅ |
| Aprobar/rechazar | — | — | ✅ | ✅ |
| Crear/emitir OC | — | — | ✅ | ✅ |
| Registrar recepción | — | ✅ | ✅ | ✅ |
| Confirmar recepción/stock | — | — | ✅ | ✅ |
| Registrar pago CxP | — | ✅ | ✅ | ✅ |
| Cancelar documentos emitidos | — | — | ✅ | ✅ |

16.1 introducirá funciones `can_create_purchase_request`, `can_approve_purchase_request` y `can_view_purchasing`; no se reutilizará ciegamente `can_edit`.

## Contrato MAG preliminar

Base: `/api/v1/purchasing`. Todos los recursos son tenant-scoped y usan paginación, JWT, errores MAG y `Idempotency-Key` en confirmaciones.

| Método | Recurso | Sprint | Estado |
|---|---|---:|---|
| GET/POST | `/requests` | 16.1 | planned |
| GET/PATCH | `/requests/{id}` | 16.1 | planned |
| POST | `/requests/{id}/submit` | 16.1 | planned |
| POST | `/requests/{id}/approve` | 16.1 | planned |
| POST | `/requests/{id}/reject` | 16.1 | planned |
| GET/POST | `/purchase-orders` | 16.2 | planned |
| POST | `/purchase-orders/{id}/issue` | 16.2 | planned |
| GET/POST | `/receipts` | 16.3 | planned |
| POST | `/receipts/{id}/confirm` | 16.3 | planned |
| GET | `/payables` | 16.4 | planned |

Respuesta de transición: recurso actualizado + `event_id`; conflicto de estado devuelve `409 state_conflict`; tenant incorrecto se responde como `404`.

## Contrato MRL

| Artefacto | Código | Motor | Sprint |
|---|---|---|---:|
| Orden de compra | DOC-006 · `MRL-TPL-004` | `BasePdfExporter` | 16.2 |
| Recepción | DOC-006 variante `receipt` | PDF | 16.3 |
| Seguimiento OC | DOC-010 | Excel | 16.4 |
| CxP y vencimientos | DOC-010 | Excel | 16.4 |

El PDF OC incluye empresa, proveedor, entrega, líneas, moneda, impuestos, condiciones, aprobador, estado y numeración; una OC no emitida lleva watermark `BORRADOR`.

