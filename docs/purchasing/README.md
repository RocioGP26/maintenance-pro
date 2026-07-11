# Sprint 16 · Maintix Purchasing

**Estado:** Sprint 16.0–16.5 ✅ · Purchasing operativo
**Módulo:** `purchasing` · **Prefijo técnico:** `Pur` · **MRG:** MRG-04-PUR

Purchasing formaliza el proceso que hoy comienza directamente en `InvCompra`: necesidad interna → aprobación → orden de compra → recepción → cuenta por pagar.

## Principios

1. Tenant-first: toda entidad contiene `empresa_id`.
2. Inventory conserva la propiedad del producto y el stock.
3. Purchasing conserva la propiedad del proceso de abastecimiento.
4. CxP actual continúa operando durante toda la migración.
5. Una recepción confirmada es la única que puede aumentar stock.
6. Toda transición relevante deja auditoría.
7. PDF y Excel se generan exclusivamente mediante MRL.

## Sub-sprints

| Sprint | Entrega | Estado |
|---|---|---|
| 16.0 | Diseño, contrato y matriz de migración | ✅ |
| 16.1 | Solicitudes y aprobación simple | ✅ |
| 16.2 | Órdenes de compra y DOC-006 PDF | ✅ |
| 16.3 | Recepciones totales, parciales y rechazo | ✅ |
| 16.4 | CxP, indicadores y Excel MRL | ✅ |
| 16.5 | Migración, alineación y cierre | ✅ |

## Documentos

- [Charter y alcance](SPRINT16-REPORT.md)
- [Arquitectura y modelos](architecture.md)
- [Contratos: estados, permisos, MAG y MRL](contracts.md)
- [Matriz de migración](migration.md)

