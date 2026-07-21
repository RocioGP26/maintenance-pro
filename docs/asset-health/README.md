# Asset Health · Sprint 21

Sprint 21 convierte señales operativas dispersas en un diagnóstico explicable
por activo. No reemplaza el criterio técnico ni predice fallas mediante IA.

El resultado representa la salud actual del activo, no un informe limitado a
90 días. Esa ventana móvil se usa únicamente en el factor de confiabilidad para
contabilizar correctivos recientes; el estado operativo es actual, mantenimiento
considera las OT pendientes, la condición usa la lectura vigente y las
incidencias abiertas permanecen activas hasta su resolución.

## Documentos

- [Informe y Definition of Done](SPRINT21-REPORT.md)
- [Arquitectura](architecture.md)
- [Contrato de cálculo](contracts.md)

## Resultado

Cada activo obtiene:

- puntaje de `0–100`;
- banda Saludable, En observación, En riesgo, Crítico o Sin datos;
- confianza de datos;
- cuatro factores con peso y evidencia;
- razones accionables;
- snapshots históricos sin duplicados cuando no cambia el diagnóstico.
