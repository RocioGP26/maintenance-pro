# RTX-SLA-001 · Acuerdo de Nivel de Servicio (SLA)

| Campo | Valor |
|-------|-------|
| **Código** | RTX-SLA-001 |
| **Versión** | **0.1.0** |
| **Estado** | 🟡 Borrador · **no es compromiso** hasta anexarse y confirmarse operativamente |
| **Fecha** | 2026-08-03 |
| **Aplica cuando** | El Contrato / Orden lo anexa expresamente (típicamente Business con add-on, Enterprise, o SLA cotizado) |
| **Complementa** | [RTX-LEGAL-002](RTX-LEGAL-002-contrato-saas.md) · [RTX-SUP-001](RTX-SUP-001-politica-soporte.md) |

> **Importante:** Los porcentajes y tiempos de este documento son **objetivos de servicio** propuestos.  
> **No deben presentarse ni firmarse como compromisos** hasta que Roustix confirme que su infraestructura y operación pueden cumplirlos de forma consistente.  
> Sin anexo expreso a RTX-LEGAL-002, este documento **no genera** derechos ni créditos.

---

## 1 · Objeto

Definir objetivos de disponibilidad, ventanas de soporte reforzado, prioridades de incidente, mantenimiento programado y exclusiones, cuando el Cliente tenga este SLA anexado.

---

## 2 · Disponibilidad

### 2.1 Objetivo mensual propuesto

| Nivel | Objetivo de disponibilidad mensual | Uso sugerido |
|-------|-----------------------------------:|--------------|
| **Estándar contractual** | **99,5 %** | Primera etapa comercial / Business+ |
| **Reforzado** | **99,9 %** | Solo tras validación operativa y cotización Enterprise |

**Cálculo sugerido:**

```
Disponibilidad (%) = (Minutos del mes − Minutos de Indisponibilidad Atribuible) / Minutos del mes × 100
```

- Mes = mes calendario en zona horaria de Colombia.  
- **Indisponibilidad Atribuible:** imposibilidad general de autenticarse o usar funciones críticas del tenant por causa imputable al Prestador, excluidas las causas del §6.

### 2.2 Créditos de servicio `[OPCIONAL · PENDIENTE DE DECISIÓN COMERCIAL]`

| Disponibilidad medida | Crédito sugerido sobre la mensualidad del mes afectado |
|----------------------:|--------------------------------------------------------:|
| &lt; objetivo y ≥ 99,0 % | 5 % |
| &lt; 99,0 % y ≥ 95,0 % | 10 % |
| &lt; 95,0 % | 15 % |

Reglas propuestas (no vigentes hasta aprobación):

1. El crédito es el **único remedio** por incumplimiento de disponibilidad, salvo dolo.  
2. Tope mensual de créditos: 15 % de la mensualidad del mes.  
3. El Cliente debe solicitar el crédito dentro de los 30 días siguientes al mes afectado.  
4. No hay reembolso en efectivo; el crédito se aplica a facturas futuras.

---

## 3 · Horarios de soporte (bajo SLA)

Salvo pacto distinto en la Orden:

| Concepto | Valor |
|----------|-------|
| Días | Lunes a viernes |
| Horario | 8:00 a. m. – 5:00 p. m. (Colombia) |
| Canales | Los de RTX-SUP-001 + canal dedicado si Enterprise |
| P1 fuera de horario | `[PENDIENTE · ¿pager / best-effort / no cubierto?]` |

---

## 4 · Prioridad de incidentes · tiempos objetivo

Estos tiempos son **objetivos de respuesta** (primer contacto humano cualificado), no de resolución, salvo que la Orden diga lo contrario.

| Prioridad | Ejemplo | Tiempo objetivo de respuesta |
|-----------|---------|------------------------------|
| **Crítica (P1)** | Plataforma caída / tenant inaccesible | **1 hora** (en horario cubierto) |
| **Alta (P2)** | Función principal afectada | **4 horas** hábiles |
| **Media (P3)** | Error parcial con workaround | **8 horas** hábiles |
| **Baja (P4)** | Consulta o mejora | **1 día hábil** |

**Respuesta** ≠ **resolución**. La resolución depende de la causa, reproducibilidad y complejidad.

---

## 5 · Mantenimiento programado

1. El Prestador podrá realizar mantenimientos programados en ventanas de bajo uso.  
2. Ventana preferente propuesta: **domingos 00:00–06:00** (Colombia) u otra comunicada.  
3. Se procurará notificación previa con al menos **48 horas** cuando sea razonablemente posible.  
4. El mantenimiento programado notificado **no** cuenta como Indisponibilidad Atribuible.  
5. Mantenimientos de emergencia por seguridad pueden ejecutarse sin preaviso completo; se informará tan pronto como sea viable.

---

## 6 · Exclusiones

No cuentan como Indisponibilidad Atribuible ni generan crédito:

- Fallas de Internet, DNS o equipos del Cliente  
- Navegadores no soportados o software del Cliente  
- Uso indebido, configuración errónea o acciones de Usuarios del Cliente  
- Problemas derivados de terceros fuera del control razonable del Prestador (p. ej. proveedor cloud en incidente general, siempre que el Prestador mitigue)  
- Fuerza mayor  
- Suspensión legítima por mora, seguridad o uso ilícito  
- Características en beta / preview expresamente marcadas  
- Periodos en que el Cliente no coopere para diagnosticar  

---

## 7 · Medición y reportes

| Elemento | Estado |
|----------|--------|
| Fuente de medición | `[PENDIENTE · monitoreo propio / proveedor]` |
| Reporte al Cliente | Bajo demanda o mensual para Enterprise |
| Discrepancias | Se resuelven con logs y evidencias de ambas partes |

---

## 8 · Relación con otros documentos

| Documento | Relación |
|-----------|----------|
| RTX-LEGAL-002 | Este SLA solo obliga si se anexa |
| RTX-SUP-001 | Define canales y alcance; el SLA añade objetivos de tiempo/disponibilidad |
| COM-01 | Enterprise «SLA según contrato» = este documento u otro pactado |

---

## 9 · Activación

Este SLA queda activado únicamente cuando:

1. La Orden o el Contrato marcan «SLA anexado: Sí», y  
2. Ambas partes firman o aceptan esta versión, y  
3. El Prestador ha marcado internamente los objetivos como **operativamente confirmados**.

Hasta entonces, los valores son **propuesta interna**.

---

## 10 · Control de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| **0.1.0** | 2026-08-03 | Borrador inicial con objetivos no vinculantes |

---

*RTX-SLA-001 · v0.1.0 · Borrador no vinculante · 2026-08-03*
