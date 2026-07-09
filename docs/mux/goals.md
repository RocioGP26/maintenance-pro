# MUX · User Goals y Anti-Goals

Define **qué quiere** y **qué rechaza** cada perfil. Cambia el diseño más que cualquier wireframe.

---

## MTX-UX-PER-001 · Laura · Gerente

| | |
|---|---|
| **Goal** | **Tomar decisiones** — ver el estado, priorizar, delegar |
| **Anti-Goal** | **No quiere aprender un ERP** — ni curvas de 200 pantallas |
| **Implicación UX** | Dashboard primero, registro mínimo, drill-down opcional |

---

## MTX-UX-PER-002 · Carlos · Técnico

| | |
|---|---|
| **Goal** | **Registrar** — OT, tiempo, repuestos, evidencia |
| **Anti-Goal** | **No quiere llenar formularios** — odia campos que no aplican |
| **Implicación UX** | Formularios cortos, defaults inteligentes, mobile-friendly |

---

## MTX-UX-PER-003 · Valentina · Vendedora

| | |
|---|---|
| **Goal** | **Vender** — cerrar con el cliente presente |
| **Anti-Goal** | **No quiere buscar inventario** en cinco pantallas |
| **Implicación UX** | Stock en línea de venta, cliente autocompletado, un flujo |

---

## MTX-UX-PER-004 · Roberto · Bodeguero

| | |
|---|---|
| **Goal** | **Mover mercancía con trazabilidad** — entradas, salidas, reservas |
| **Anti-Goal** | **No quiere contar inventario dos veces** — sistema ≠ Excel paralelo |
| **Implicación UX** | Un solo registro de verdad, import Excel confiable, conciliación clara |

---

## MTX-UX-PER-005 · Andrea · Administradora

| | |
|---|---|
| **Goal** | **Dejar la empresa operando** — usuarios, roles, módulos |
| **Anti-Goal** | **No quiere ser soporte IT permanente** — self-service claro |
| **Implicación UX** | Wizards, docs inline, roles predefinidos por perfil MUX |

---

## Reservados (stub)

| ID | Goal (anticipado) | Anti-Goal (anticipado) |
|----|-------------------|------------------------|
| PER-006 Auditor | Demostrar cumplimiento | Perder evidencia o trazabilidad |
| PER-007 Proveedor | Responder cotizaciones rápido | Duplicar data en portal y email |
| PER-008 Cliente | Ver estado de pedido/servicio | Llamar por teléfono para saber «dónde está» |

---

## Uso en diseño

En cada PR de UI, tabla:

```
Perfil: MTX-UX-PER-002 (Carlos)
Goal servido: ✅ Registro en 3 clics
Anti-Goal respetado: ✅ Solo 4 campos obligatorios
```

Si un Anti-Goal se viola, rediseñar — no «educar al usuario».
