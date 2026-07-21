# MRG-10-BEST · Buenas prácticas

**Código:** MRG-10-BEST · Sprint 10.10 · **Entregado**

> Implementar Roustix correctamente no es solo «dar acceso». Es **configurar tenant, módulos, datos maestros y procesos** alineados al negocio del cliente — y **adoptarlo** en la operación diaria.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Recopilar buenas prácticas para implementadores, consultores y administradores de tenant — cierre del **Roustix Reference Guide v1.0**.

---

## 1 · Antes de empezar

| # | Práctica |
|---|----------|
| 1 | Confirmar **módulos contratados** y sector correcto |
| 2 | Definir **roles** antes de invitar al equipo |
| 3 | Acordar nomenclatura de activos o SKUs con el cliente |
| 4 | Revisar MCM para expectativas comerciales vs alcance MRG |
| 5 | No prometer CRM o Compras unificado si aún están en roadmap |

---

## 2 · Mantenimiento

| # | Práctica |
|---|----------|
| 1 | Clasificar **criticidad** real de activos — no todo es crítico |
| 2 | Completar **tipos de activo** y campos personalizados al inicio |
| 3 | Establecer **planes preventivos** antes de acumular OT correctivas |
| 4 | Cerrar OT con **jornadas y repuestos** — el historial es el valor |
| 5 | Convertir incidencias recurrentes en preventivos |
| 6 | Revisar dashboard semanal: OT vencidas y repuestos bajo mínimo |

→ [MRG-02 · Mantenimiento](02-maintenance.md)

---

## 3 · Inventario

| # | Práctica |
|---|----------|
| 1 | Definir **stock mínimo** por SKU relevante |
| 2 | Usar import Excel para carga inicial masiva |
| 3 | Registrar **compras** antes de vender — stock confiable |
| 4 | Disciplina en **CxP** — pagos registrados en fecha |
| 5 | Capacitar en POS y ventas a crédito + abonos |
| 6 | No mezclar repuestos técnicos con productos comerciales |

→ [MRG-03 · Inventario](03-inventario.md) · [MRG-05 · Ventas](05-ventas.md)

---

## 4 · Administración

| # | Práctica |
|---|----------|
| 1 | Mínimo un **Admin** y un backup |
| 2 | Principio de **menor privilegio** en roles |
| 3 | Revisar config empresa: moneda, zona horaria, jornada |
| 4 | Tras onboarding, **reemplazar datos demo** por datos reales |
| 5 | Documentar internamente quién es admin plataforma vs tenant |

→ [MRG-07 · Administración](07-administracion.md)

---

## 5 · Multi-módulo

| # | Práctica |
|---|----------|
| 1 | Acordar qué inventario usa cada operación |
| 2 | Capacitar perfiles distintos (técnico vs vendedor) |
| 3 | No duplicar maestros (dos proveedores para el mismo tercero) |
| 4 | Usar [MRG-09 · Workflows](09-workflows.md) como guía de capacitación |

---

## 6 · Integración (MAG / MSD)

| # | Práctica |
|---|----------|
| 1 | Leer MRG primero — entender negocio antes de API |
| 2 | Usar contrato MAG v1 — no endpoints legacy indefinidamente |
| 3 | Respetar tenant en JWT — nunca hardcodear empresa_id |
| 4 | Validar en sandbox MSD antes de producción |

---

## 7 · Documentación y capacitación

MRG es base para:

| Derivado | Uso |
|----------|-----|
| Manual de usuario | Por rol (MUX personas) |
| Material comercial | Complemento MCM con casos reales |
| Runbooks soporte | MRG-09 workflows |
| Casos QA | Exit criteria por capítulo |

---

## 8 · Adopción del sistema

Una implementación exitosa no depende únicamente de la configuración inicial. También requiere que los usuarios **incorporen Roustix como parte de su operación diaria**.

| Recomendación | Beneficio |
|---------------|-----------|
| Capacitar por rol (técnico, vendedor, administrador) | Reduce errores operativos |
| Definir responsables funcionales por módulo | Facilita el soporte interno |
| Revisar indicadores semanalmente | Detecta desviaciones a tiempo |
| Actualizar datos maestros periódicamente | Mantiene la calidad de la información |
| Documentar procedimientos internos | Facilita la continuidad operativa |

---

## 9 · Errores frecuentes

| Error | Consecuencia | Corrección |
|-------|--------------|------------|
| Saltar preventivos | Solo correctivas reactivas | Planificar desde día 1 |
| Stock sin compras | Ventas inconsistentes | Registrar entradas |
| Roles mal asignados | Usuarios bloqueados o sobre-privilegiados | Matriz MRG-07 |
| Confundir inventarios | Stock «fantasma» | Separar repuesto vs producto |
| Prometer CRM | Expectativa incumplida | Roadmap MPA-05 |
| No revisar KPIs | Operación a ciegas | Dashboard semanal MRG-08 |

---

## 10 · Evolución continua

Roustix está diseñado para **crecer junto con la organización**.

Una implementación típica evoluciona en etapas:

```
Configuración inicial
        │
        ▼
Capacitación
        │
        ▼
Operación diaria
        │
        ▼
Indicadores
        │
        ▼
Optimización
        │
        ▼
Nuevos módulos
```

Cada nueva implementación debe buscar primero la **estabilidad operativa** antes de incorporar funcionalidades adicionales.

---

## Exit Criteria · MRG v1.0

**MRG v1.0** se considera **completado** cuando:

- [x] Los diez capítulos funcionales están documentados
- [x] Todos los módulos en producción cuentan con guía funcional
- [x] Los módulos roadmap están documentados como visión futura
- [x] Existen referencias cruzadas con MPA, MAG, MSD, MCM, MUX y MRL
- [x] El catálogo `/mrg/` está actualizado
- [x] Se publica la versión **MRG v1.0.0**

---

## Filosofía del capítulo

Roustix entrega valor cuando la **operación del cliente** se refleja fielmente en la plataforma. Las buenas prácticas de MRG-10 convierten documentación en **resultado medible**.

---

## Resultado · Sprint 10

Con MRG v1.0, la documentación funcional de Roustix alcanza el mismo nivel de soluciones empresariales consolidadas.

| Suite | Estado | Alcance |
|-------|--------|---------|
| **MPA v1.0** | ✅ | Arquitectura de plataforma |
| **MAG v1.0** | ✅ | API y contrato REST |
| **MSD v1.0** | ✅ | Ecosistema para desarrolladores |
| **MRG v1.0** | ✅ | Guía funcional del producto |
| **MCM** | 🟡 | Comercial y posicionamiento |
| **MUX** | 🟡 | UX, diseño y experiencia |
| **MRL** | 🟡 | Estándares de reportes y documentos |

Roustix dispone de un **ecosistema documental integral**: arquitectura, integración, experiencia del desarrollador y funcionamiento del producto.

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **MRG** | ✅ v1.0.0 |
| **Capítulos** | 10 / 10 |
| **Cobertura funcional** | Mantenimiento · Inventario · Compras · Ventas · CRM · Administración · Reportes · Workflows |
| **Audiencia** | Clientes · Implementadores · Soporte · QA · Comercial |
| **Siguiente suite** | MCM v1.0 (Comercial) o MRL v1.0 (Reportes) |

---

→ [MRG-01 · Intro](01-intro-filosofia.md) · [Índice MRG](/mrg/) · [Roustix Docs](/docs/)
