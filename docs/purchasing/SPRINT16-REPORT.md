# Sprint 16 · Purchasing

## Objetivo

Convertir las compras directas actuales en un proceso de abastecimiento trazable, sin interrumpir Inventory ni CxP y sin construir contabilidad, tesorería o facturación electrónica.

## Alcance

| Dentro | Fuera |
|---|---|
| Solicitudes y aprobación simple | Flujos multinivel configurables |
| Órdenes de compra | Licitaciones y contratos |
| Recepción total/parcial/rechazo | Logística avanzada y devoluciones |
| Actualización de stock | Contabilidad general |
| CxP operativa y vencimientos | Tesorería y conciliación bancaria |
| Auditoría de transiciones | Firma digital certificada |
| API MAG y documentos MRL | Integraciones fiscales por país |

## Definition of Done · 16.0

- [x] Charter y alcance formalizados.
- [x] Modelo lógico y ownership definidos.
- [x] Estados y transiciones definidos.
- [x] Matriz de permisos compatible con roles actuales.
- [x] Contrato MAG preliminar definido, sin publicar endpoints como operativos.
- [x] Catálogo MRL definido para DOC-006 y Excel de seguimiento.
- [x] Matriz de migración desde `InvCompra` documentada.
- [x] Estrategia de compatibilidad y rollback definida.
- [x] No se modificó el esquema ni se añadió lógica de negocio.

## Decisiones

- `InvProveedor` e `InvProducto` se reutilizan; no se duplican maestros.
- Nuevas entidades usan prefijo `Pur` y tablas `pur_*`.
- `InvCompra` sigue siendo el registro financiero/legado durante 16.1–16.4.
- La creación de CxP ocurre al confirmar recepción con factura, no al aprobar la solicitud.
- La aprobación de 16.1 es de un solo nivel y usa roles existentes.

## Riesgos controlados

| Riesgo | Control |
|---|---|
| Doble incremento de stock | Idempotency key por recepción y movimiento |
| Duplicar CxP | `inv_compra_id` único en OC/recepción migrada |
| Romper tenants actuales | Rutas antiguas permanecen activas hasta 16.5 |
| Confundir aprobación con recepción | Estados y permisos separados |
| Exponer API prematura | OpenAPI marcado `x-roustix-status: planned` hasta implementación |

## Próximo paso

Sprint 16 quedó cerrado: solicitudes, OC, DOC-006, recepciones, stock, CxP,
indicadores, Excel MRL y migración legacy están operativos. La API MAG Purchasing
permanece como contrato estable pendiente de implementación en Sprint 17.

## Cierre · 16.5

- [x] 12/12 compras históricas vinculadas.
- [x] 12 solicitudes, 12 OC y 12 recepciones legacy creadas.
- [x] Stock antes/después: 14.819 unidades, sin variación.
- [x] Segunda ejecución: cero migraciones nuevas.
- [x] Saldos y pagos preservados en `InvCompra`.
- [x] Navegación diferencia Purchasing formal de entradas legacy.
- [x] MRG y MAG alineados con el estado real.

