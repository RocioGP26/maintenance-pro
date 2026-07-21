# Sprint 20 · Disparadores y automatizaciones configurables

**Estado:** Implementado ✅  
**Módulo propietario:** Maintenance

Sprint 20 convierte las lecturas confiables de Sprint 19 en decisiones
operativas gobernadas. Una regla puede detectar el cruce de un umbral, crear un
aviso interno o generar una OT sin duplicados y conservar la evaluación completa.

## Capacidades

- reglas tenant-safe asociadas a un medidor;
- operadores `>`, `≥`, `<` y `≤`;
- ejecución solo al cruzar el umbral o en cada coincidencia;
- ventana de enfriamiento configurable;
- acciones `notify` y `create_work_order`;
- destinatarios por rol y técnico asignado;
- evaluación y acción idempotentes por regla + lectura;
- historial de éxitos, omisiones y fallos;
- activación y desactivación sin eliminar historia.

## Límites

No se ejecutan expresiones arbitrarias, scripts, webhooks, SMS, correo, ingesta
IoT ni reglas entre módulos. Estos límites reducen el riesgo y mantienen el motor
determinista. Las integraciones externas continúan en Sprint 22.

## Documentos

- [Charter y Definition of Done](SPRINT20-REPORT.md)
- [Arquitectura](architecture.md)
- [Contratos y seguridad](contracts.md)
