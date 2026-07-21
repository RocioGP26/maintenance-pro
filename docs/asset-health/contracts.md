# Contrato de cálculo · Asset Health v1

## Fórmula

```text
Health = Estado × 30%
       + Mantenimiento × 25%
       + Confiabilidad × 20%
       + Condición medida × 25%
```

| Factor | Señales principales |
|---|---|
| Estado operativo | Operativo, en mantenimiento o en falla |
| Mantenimiento | OT vencidas, abiertas/programadas y pendientes de cierre |
| Confiabilidad | Correctivos de los últimos 90 días e incidencias abiertas |
| Condición medida | Última lectura, rangos configurados, anomalía y antigüedad |

## Bandas

| Puntaje | Banda |
|---:|---|
| 85–100 | Saludable |
| 70–84 | En observación |
| 50–69 | En riesgo |
| 0–49 | Crítico |

Con confianza menor de 30%, la banda contractual es `Sin datos`.

## Confianza

La confianza es la suma de pesos con información observable. Estado,
mantenimiento y confiabilidad aportan 75%. Condición aporta el 25% restante
solo cuando existen medidores evaluables o anomalías registradas.

Un activo puede mostrar puntaje alto con confianza 75%; esto significa que no
hay señales adversas en la operación registrada, pero falta telemetría de
condición para un diagnóstico completo.

