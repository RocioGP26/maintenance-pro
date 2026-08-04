# RTX-SUP-001 · Política de Soporte Roustix

| Campo | Valor |
|-------|-------|
| **Código** | RTX-SUP-001 |
| **Versión** | **0.1.0** |
| **Estado** | 🟡 Borrador |
| **Fecha** | 2026-08-03 |
| **Pregunta que responde** | ¿Cómo obtiene ayuda un cliente de Roustix? |
| **Referenciado por** | [RTX-LEGAL-002](RTX-LEGAL-002-contrato-saas.md) · [COM-01](../com/COM-01-planes-licenciamiento.md) |
| **No sustituye** | [RTX-SLA-001](RTX-SLA-001-acuerdo-nivel-servicio.md) (compromisos de nivel) |

---

## 1 · Propósito

Definir canales, horarios, tipos de solicitud, inclusiones, exclusiones y escalamiento del soporte de Roustix. Esta política es **operativa**: describe el servicio de ayuda. Los objetivos de disponibilidad y tiempos de respuesta contractuales solo aplican si el Cliente tiene anexado RTX-SLA-001.

---

## 2 · Canales por plan

| Plan | Canal principal | Canal secundario | Notas |
|------|-----------------|------------------|-------|
| **Start** | Correo | — | Un hilo por incidente / consulta |
| **Business** | Chat (cuando esté habilitado) | Correo | Misma cola de soporte |
| **Enterprise** | Canal dedicado (según Orden) | Correo / chat | Puede incluir CS o contacto nombrado |
| **Add-on** `ADD-SUP-PRI` | Priorización en cola | Según plan base | No crea por sí solo un SLA de uptime |

| Canal | Identificador |
|-------|---------------|
| Correo temporal (piloto) | `soporte.roustix@hotmail.com` |
| Correo objetivo | `soporte@roustix.com` `[PENDIENTE · DNS / buzón]` |
| Chat | Dentro de la Plataforma (Business+) `[cuando exista]` |
| Portal de soporte | `[Futuro]` |

No se presta soporte por redes sociales ni canales no listados.

---

## 3 · Horarios

| Concepto | Valor |
|----------|-------|
| Días | Lunes a viernes |
| Horario | **8:00 a. m. – 5:00 p. m.** (hora de Colombia, UTC−5) |
| Excluidos | Sábados, domingos y festivos colombianos |
| Fuera de horario | Las solicitudes se registran y atienden el siguiente día hábil |

Enterprise o SLA anexado pueden pactar ventanas distintas en la Orden.

---

## 4 · Tipos de solicitudes

| Tipo | Descripción | Ejemplo |
|------|-------------|---------|
| **Incidente** | Error o degradación del servicio | No carga un módulo; error 500 recurrente |
| **Consulta** | Duda sobre uso | Cómo crear una OT |
| **Configuración** | Ayuda a parametrizar lo incluido en el plan | Roles, sedes, catálogos |
| **Capacitación** | Orientación breve o sesión pactada | Recorrido de un módulo |
| **Mejora** | Sugerencia de producto | Nueva columna en un reporte |

Las mejoras no tienen plazo de implementación; se evalúan en el roadmap.

---

## 5 · Lo que incluye

Según el plan y la Orden:

- Ayuda funcional sobre módulos contratados  
- Diagnóstico y corrección de errores atribuibles a la Plataforma  
- Orientación básica de configuración dentro del alcance  
- Información sobre estado de incidentes conocidos  
- Guía para exportar datos o usar funciones documentadas  
- Onboarding inicial remoto conforme a la Orden  

---

## 6 · Lo que no incluye

Salvo cotización y aceptación expresa (COM-02 / servicios profesionales):

- Desarrollo a medida o personalizaciones de un único Cliente  
- Cambios de producto solicitados por un solo tenant  
- Administración de la infraestructura, red o dispositivos del Cliente  
- Soporte sobre equipos, VPN, firewalls o ISP del Cliente  
- Recuperación de datos borrados por Usuarios del Cliente fuera de la política de respaldos  
- Capacitación masiva o en sitio no contratada  
- Integraciones API/webhooks no contratadas  
- Asesoría legal, contable o de compliance del Cliente  

---

## 7 · Información mínima para abrir una solicitud

Para agilizar la atención, el Cliente debe indicar:

1. Razón social / tenant  
2. Usuario afectado  
3. Descripción del problema y pasos para reproducirlo  
4. Fecha y hora aproximada  
5. Capturas o mensajes de error (sin contraseñas)  
6. Impacto (¿bloquea la operación?)  

---

## 8 · Escalamiento interno

```
Nivel 1 · Soporte funcional
        ↓ (no resuelto / sospecha de defecto)
Nivel 2 · Operación / plataforma
        ↓ (defecto de producto o cambio de código)
Desarrollo · Ingeniería
```

| Nivel | Responsabilidad |
|-------|-----------------|
| **1** | Clasificar, guiar, resolver consultas y configuraciones conocidas |
| **2** | Diagnosticar infraestructura, logs, tenants, integraciones |
| **Desarrollo** | Corregir defectos o evaluar cambios de producto |

El Cliente no elige el nivel; el Prestador escala según el diagnóstico.

---

## 9 · Severidad operativa (clasificación interna)

Esta tabla **clasifica** solicitudes. No constituye compromiso de tiempo salvo que RTX-SLA-001 esté anexado.

| Severidad | Ejemplo | Tratamiento típico |
|-----------|---------|-------------------|
| **P1 · Crítica** | Plataforma inaccesible para el tenant | Máxima prioridad en horario hábil |
| **P2 · Alta** | Función principal afectada sin workaround | Prioridad alta |
| **P3 · Media** | Error parcial con workaround | Cola estándar |
| **P4 · Baja** | Consulta, mejora, cosmético | Cola estándar / backlog |

---

## 10 · Relación con planes comerciales

| Plan | Soporte incluido (COM-01) | Política aplicable |
|------|---------------------------|--------------------|
| Start | Email | Esta política |
| Business | Chat (+ correo) | Esta política |
| Enterprise | Dedicado + SLA según contrato | Esta política + RTX-SLA-001 si se anexa |

---

## 11 · Cambios

Roustix podrá actualizar esta política. Los cambios materiales se comunicarán a clientes activos con preaviso razonable o en la renovación. La versión aplicable será la referenciada en el Contrato / Orden o la publicada como Vigente.

---

## 12 · Control de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| **0.1.0** | 2026-08-03 | Creación del borrador inicial |

---

*RTX-SUP-001 · v0.1.0 · Borrador · 2026-08-03*
