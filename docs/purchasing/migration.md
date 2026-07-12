# Sprint 16 · Migración desde compras actuales

## Matriz

| Actual | Destino | Estrategia |
|---|---|---|
| `InvProveedor` | Se mantiene | Referencia directa desde `PurOrdenCompra` |
| `InvProducto` | Se mantiene | Referencia desde líneas; Inventory conserva stock |
| `InvCompra` | `PurOrdenCompra` + `PurRecepcion` opcionales | Backfill en 16.5, sin borrar origen |
| `InvCompraLinea` | `PurOrdenLinea` + `PurRecepcionLinea` | Cantidad histórica se considera recibida |
| `InvCompraPago` | Se mantiene | CxP continúa vinculada a `InvCompra` |
| `/comercial/compras` | Vista legacy | Convive hasta paridad y redirección 16.5 |
| Registro directo de entrada | Fast path controlado | Se mantiene temporalmente con evento `legacy_direct_receipt` |

## Fases

1. **16.1:** tablas de solicitudes; cero cambios sobre `InvCompra`.
2. **16.2:** OC nuevas; todavía pueden coexistir compras directas.
3. **16.3:** recepción crea movimiento de stock y puede materializar `InvCompra`.
4. **16.4:** CxP lee `InvCompra`; se agregan enlaces a OC/recepción.
5. **16.5:** backfill histórico, navegación unificada y decisión sobre fast path.

## Backfill propuesto

- Por cada `InvCompra` sin vínculo, crear OC histórica en estado `cerrada`.
- Crear una recepción histórica `confirmada` por el total de sus líneas.
- Guardar `legacy_inv_compra_id` único para idempotencia.
- No volver a ejecutar movimientos de stock durante backfill.
- Conservar fechas, monedas, impuestos, pagos y números originales.
- Registrar evento `legacy_migrated`, actor `Sistema · Maintix`.

## Compatibilidad y rollback

- Migraciones solo aditivas hasta cerrar 16.5.
- Ninguna columna actual se elimina o cambia de semántica.
- Feature flag por tenant: `purchasing_formal`.
- Desactivar el flag revierte navegación, no datos.
- El script de backfill admite `--dry-run`, lotes y reanudación.
- Reconciliación obligatoria: compras, líneas, totales, stock no mutado y saldo CxP.

## Criterios de aceptación 16.5

- Conteos y totales legacy = nuevos vínculos.
- Cero movimiento duplicado de stock.
- Cero CxP duplicada.
- Todas las entidades tienen tenant correcto.
- Rutas antiguas redirigen o explican el siguiente paso según MUX.

