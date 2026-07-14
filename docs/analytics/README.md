# Arquitectura de Inicio y Análisis

## Objetivo

Separar la atención operativa diaria de la inteligencia histórica. Esta frontera evita que el usuario tenga que interpretar gráficos para descubrir el trabajo urgente y permite que los indicadores crezcan sin sobrecargar Inicio.

## Capas de información

| Capa | Pregunta | Ruta principal | Contenido |
|------|----------|----------------|-----------|
| Operación | ¿Qué requiere mi atención hoy? | `/dashboard` | OT abiertas/vencidas, preventivos del día, incidencias, faltantes, activos detenidos, garantías y actividad reciente |
| Inteligencia | ¿Cómo está funcionando la operación? | `/analisis` | KPI, costos, cumplimiento, tendencias y reportes |
| Administración | ¿Cómo se gobierna la plataforma? | Rutas de configuración | Usuarios, roles, seguridad, empresa y campos personalizados |

## Contrato de rutas

- `/dashboard`: Inicio · Centro de Operaciones. No debe incorporar MTBF, MTTR ni gráficos históricos.
- `/analisis`: directorio de áreas analíticas disponibles según módulos y permisos.
- `/analisis/mantenimiento`: indicadores estratégicos de mantenimiento y sus filtros propios.
- `/mantenimiento/analisis-costos`: desglose económico de mano de obra, herramientas, repuestos y servicio externo.
- `/reportes`: reportes y exportaciones operativas.
- Los tableros de Inventario Comercial y Purchasing se integran en la navegación de Inteligencia sin cambiar sus contratos actuales.

## Reglas de diseño

1. Inicio prioriza alertas accionables, listas cortas y enlaces directos al registro que requiere intervención.
2. Análisis admite períodos, comparaciones, KPI, gráficos y exploración histórica.
3. Hoja de Vida permanece dentro del activo como registro oficial; no se reemplaza por un tablero.
4. Cada consulta conserva el aislamiento por empresa y los permisos de módulo existentes.
5. Un nuevo indicador estratégico se agrega a Análisis. Solo llega a Inicio cuando produce una acción concreta y vigente.

## Evolución prevista

- Perfiles de Inicio por rol: técnico, supervisor y administrador.
- Tendencias de confiabilidad e incidencias.
- Análisis transversal de costos, proveedores y activos.
- Alertas configurables por empresa y criticidad.

## Verificación

`tests/test_dashboard_analysis.py` protege la separación de responsabilidades, la navegación, la permanencia de los KPI y las acciones de filtros del panel analítico.
