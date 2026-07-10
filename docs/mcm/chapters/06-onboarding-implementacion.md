# MCM-06-ONBOARD · Implementación y onboarding

**Código:** MCM-06-ONBOARD · Sprint 11.6 · **Entregado**

> La venta no termina con la firma. Termina cuando el cliente **opera con confianza** en Maintix.

**Prerequisitos:** [MCM-04-PLANS](04-planes-saas.md) · [MRG-07 · Administración](/mrg/chapters/07-administracion.md) · [MUX](/mux/)

---

## Objetivo del capítulo

Definir el proceso comercial de implementación y onboarding: expectativas por plan, roles, tiempos orientativos y handoff ventas → éxito del cliente — alineado con MRG-07.

---

## 1 · Filosofía de implementación

| Principio | Significado |
|-----------|-------------|
| **Valor en días, no meses** | Start: operación digitalizada en **menos de una semana** |
| **Un módulo primero** | No cargar todo el catálogo el día 1 |
| **Champion obligatorio** | Alguien interno que empuje la adopción |
| **Datos reales pronto** | Trial con datos de ejemplo → migración guiada |
| **MRG como referencia** | Implementadores usan MRG; comercial alinea expectativas |

**Frase comercial:** *«No implementamos un ERP de seis meses. Acompañamos la primera victoria operativa en días.»*

---

## 2 · Fases del onboarding

```
Contrato / trial
      │
      ▼
Provisioning tenant (Mantis)
      │
      ▼
Configuración base (sedes · roles · sector)
      │
      ▼
Capacitación por perfil MUX
      │
      ▼
Go-live módulo 1
      │
      ▼
Revisión 7–14 días · expansión
```

| Fase | Responsable | Entregable |
|------|-------------|------------|
| **Provisioning** | Mantis / plataforma | Tenant activo · plan · módulos |
| **Kick-off** | Comercial + champion | Objetivo · usuarios · sedes |
| **Configuración** | Admin tenant | Sedes · roles · catálogo inicial |
| **Capacitación** | Onboarding / docs MRG | Usuarios operando flujos clave |
| **Go-live** | Champion | Primera OT / primera venta / primera compra |
| **Revisión** | Customer success | KPIs · plan upgrade si aplica |

---

## 3 · Onboarding por plan

| Plan | Modalidad | Tiempo orientativo | Alcance |
|------|-----------|-------------------|---------|
| **Start** | Self-service + guías MUX/MRG | **3–7 días** | 1 módulo · 1 sede · ≤10 usuarios |
| **Grow** | Guiado (1 sesión) | **1–2 semanas** | 2 módulos · 2 sedes |
| **Scale** | Por sede | **2–4 semanas** | Multisede · consolidado |
| **Enterprise** | Programa a medida | Contrato | SLA · integraciones · CS dedicado |

*Tiempos: expectativa comercial — no SLA contractual salvo Enterprise.*

→ Expectativas por sector: [MCM-03-MARKETS](03-sectores-mercados.md)

---

## 4 · Roles en la implementación

| Rol | Quién | Función |
|-----|-------|---------|
| **Mantis** | Operador plataforma | Crear tenant · plan · soporte L2 |
| **Admin tenant** | Cliente | Usuarios · sedes · configuración |
| **Champion** | Cliente (gerente / jefe área) | Impulsar adopción · validar procesos |
| **Usuarios operativos** | Cliente | Ejecutar OT · ventas · bodega |
| **Comercial Maintix** | Ventas | Expectativas · handoff · upgrade |

→ Detalle funcional: [MRG-07 · Administración](/mrg/chapters/07-administracion.md)

---

## 5 · Checklist comercial pre-go-live

Antes de dar por cerrada la implementación inicial:

- [ ] Módulo de entrada activo y usado (no solo configurado)
- [ ] Al menos **3 usuarios** operando en la primera semana
- [ ] Dashboard revisado con el champion
- [ ] Flujo principal completado (OT cerrada · venta · compra recibida)
- [ ] Fecha de revisión agendada (día 7 o 14)
- [ ] Señales de upgrade documentadas en CRM

---

## 6 · Handoff ventas → éxito

| Campo | Qué transferir |
|-------|----------------|
| **Sector y puerta** | MCM-03 · historia de demo usada |
| **Plan y módulos** | Start/Grow + expansión esperada |
| **DMU** | Quién aprobó · quién usa · quién puede bloquear |
| **Objeciones** | OBJ activas en el ciclo |
| **ICP / OMI** | Score · urgencia · champion |
| **Compromiso** | KPI que el cliente quiere ver en 30 días |

Documento de referencia interno: [appendix/icp-score.md](appendix/icp-score.md) · [appendix/buyer-personas-dmu.md](appendix/buyer-personas-dmu.md)

---

## 7 · Trial 15 días

| Día | Acción recomendada |
|-----|-------------------|
| **0** | Registro · tenant demo o trial · email bienvenida |
| **1–3** | Configuración mínima · primer flujo |
| **7** | Check-in comercial · revisar uso |
| **12** | Propuesta plan · objeciones |
| **15** | Cierre o extensión acordada |

**Mensaje:** el trial no es «probar features». Es **sentir la transformación** (MCM-02) en su operación.

---

## 8 · Errores comunes

| Error | Corrección |
|-------|------------|
| Implementar dos módulos el día 1 en Start | Un módulo · victoria rápida |
| Sin champion | Identificar en calificación (DMU) |
| Capacitación solo al admin | Involucrar técnicos / bodega / ventas (MUX) |
| Prometer integración ERP sin preventa | OBJ-010 · MAG · plan Scale/Enterprise |
| Abandonar post go-live | Revisión día 7–14 obligatoria |

---

**Próximo capítulo:** [MCM-07-DEMO · Guía oficial de demostración](07-demo-comercial.md)

---

*MCM-06-ONBOARD · Maintix Commercial Manual · Sprint 11 · 2026*
