# Arquitectura · Asset Health

## Componentes

| Componente | Responsabilidad |
|---|---|
| `asset_health.service` | Cálculo determinista, bandas, portafolio y snapshots |
| `AssetHealthSnapshot` | Historial auditable por empresa y activo |
| `asset_health.routes` | Portafolio, detalle y actualización autorizada |
| Hooks operativos | Recalcular tras lectura, automatización, OT o incidencia |

## Principios

1. **Explicable:** cada factor conserva puntaje, peso y evidencia.
2. **Datos faltantes visibles:** no se inventa condición; se aplica neutral y baja confianza.
3. **Tenant-safe:** toda consulta y snapshot incluye `empresa_id`.
4. **Sin duplicación:** si el diagnóstico no cambia, se reutiliza el último snapshot.
5. **Transaccional:** el snapshot se confirma o revierte junto con el evento operativo.

## Seguridad

- Administrador y supervisor: portafolio completo y actualización.
- Técnico: solo activos asignados, bajo su responsabilidad o vinculados a sus OT.
- Reportante: sin acceso al diagnóstico técnico interno.

