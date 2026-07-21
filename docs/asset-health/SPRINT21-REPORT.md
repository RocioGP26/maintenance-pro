# Sprint 21 · Asset Health avanzado

**Estado:** Finalizado ✅  
**Fecha:** 2026-07-21  
**Módulo propietario:** Maintenance

## Objetivo

Calcular y explicar la salud de cada activo usando estado operativo,
mantenimiento, confiabilidad y condición medida, indicando además la confianza
del diagnóstico según la cobertura real de datos.

## Flujo

```text
Activo + OT + incidencias + lecturas
                  ↓
        Cuatro factores ponderados
                  ↓
 Puntaje + banda + confianza + razones
                  ↓
 Dashboard · detalle · campana · historial
```

## Definition of Done

- [x] Puntaje determinista de 0–100 por activo.
- [x] Factores y pesos visibles para el usuario.
- [x] La ausencia de medidores reduce confianza y usa un valor neutral explícito.
- [x] Las lecturas fuera de rango afectan condición.
- [x] OT vencidas, correctivos e incidencias abiertas afectan el diagnóstico.
- [x] Existen bandas y razones accionables.
- [x] Existe portafolio con búsqueda y filtros.
- [x] Existe detalle con desglose e historial.
- [x] Técnicos solo consultan activos relacionados.
- [x] Supervisores y administradores pueden actualizar snapshots.
- [x] La campana presenta activos en riesgo según el último snapshot.
- [x] Lecturas y cambios de estado generan snapshots sin duplicar valores iguales.
- [x] Dashboard reemplaza el gráfico simple de estados por Asset Health real.
- [x] Existen migración, pruebas tenant-safe y documentación oficial.

## Fuera de alcance

- Modelos predictivos o aprendizaje automático.
- Diagnóstico automático de causa raíz.
- Ingesta IoT continua.
- Recomendaciones generativas.
- API pública y webhooks; pertenecen a Sprint 22.

