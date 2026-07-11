# Sprint 16 · Arquitectura Purchasing

## Ownership

```text
Inventory                         Purchasing
InvProducto <-------------------- PurSolicitudLinea
InvProveedor <------------------- PurOrdenCompra
stock <--- PurRecepcionLinea <--- PurRecepcion <--- PurOrdenCompra
InvCompra / CxP <---------------- recepción facturada
```

Purchasing referencia maestros de Inventory; nunca mantiene copias de nombre, stock o proveedor como fuente principal. Se permiten snapshots documentales en la OC para preservar historia.

## Modelo lógico

| Modelo | Tabla | Campos principales |
|---|---|---|
| `PurSolicitud` | `pur_solicitudes` | id, empresa_id, numero, solicitante_id, estado, prioridad, justificacion, requerida_para, timestamps |
| `PurSolicitudLinea` | `pur_solicitud_lineas` | solicitud_id, producto_id, descripcion_libre, cantidad, unidad, costo_estimado |
| `PurOrdenCompra` | `pur_ordenes` | empresa_id, numero, solicitud_id, proveedor_id, estado, moneda, subtotal, iva, total, fechas, condiciones |
| `PurOrdenLinea` | `pur_orden_lineas` | orden_id, solicitud_linea_id, producto_id, descripcion_snapshot, cantidad_ordenada, precio, impuestos |
| `PurRecepcion` | `pur_recepciones` | empresa_id, numero, orden_id, estado, recibido_por_id, fecha, factura, idempotency_key |
| `PurRecepcionLinea` | `pur_recepcion_lineas` | recepcion_id, orden_linea_id, cantidad_recibida, cantidad_rechazada, motivo_rechazo |
| `PurEvento` | `pur_eventos` | empresa_id, entidad, entidad_id, evento, actor_id, estado_anterior, estado_nuevo, payload, created_at |

## Reglas de integridad

- Todas las FK cruzadas deben comprobar el mismo `empresa_id` en servicio, además de la FK SQL.
- Una línea usa `producto_id` o `descripcion_libre`; al menos uno es obligatorio.
- La cantidad acumulada recibida no supera la ordenada.
- Una recepción confirmada es inmutable; la corrección usa evento compensatorio.
- `idempotency_key` es única por tenant.
- Totales se recalculan en servidor; nunca se confían al cliente.
- Numeración: `SC-YYYY-NNNN`, `OC-YYYY-NNNN`, `RC-YYYY-NNNN` por tenant.

## Límites de servicio

```text
app/purchasing/
├── models.py       # entidades Pur* (o registro en models durante transición)
├── service.py      # comandos y transiciones
├── queries.py      # consultas tenant-safe
├── permissions.py  # capacidades Purchasing
├── routes.py       # UI
├── api.py          # adaptador MAG
├── audit.py        # PurEvento
└── mrl_exports.py  # adaptadores DOC-006 / Excel
```

Los cambios de stock siguen pasando por un servicio Inventory; Purchasing no ejecutará `producto.stock +=` directamente.

