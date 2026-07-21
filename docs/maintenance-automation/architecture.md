# Sprint 20 · Arquitectura

```text
MeterReading ──► MaintenanceAutomationRule
                         │
                         ▼
              MaintenanceAutomationExecution
                    ├── WorkOrder
                    └── MaintenanceAutomationNotification
```

| Entidad | Responsabilidad |
|---|---|
| `MaintenanceAutomationRule` | Condición, control de cruce/enfriamiento y acción versionada como snapshot |
| `MaintenanceAutomationExecution` | Resultado único de evaluar una regla contra una lectura |
| `MaintenanceAutomationNotification` | Entrega individual al usuario autorizado |
| `MaintenanceAutomationEvent` | Auditoría del ciclo de vida y resultado de la acción |

La evaluación ocurre dentro de la transacción de la lectura. La restricción
única `rule_id + reading_id` protege reintentos. La ejecución guarda snapshots
de condición y acción para que cambios futuros no reinterpreten la historia.

El modo `crossing_only` compara con la lectura cronológicamente anterior. Si la
condición ya era verdadera, registra `no_threshold_crossing` y no repite la
acción. El enfriamiento se evalúa sobre la última ejecución exitosa.
