# MUX · User Journeys

Flujos paso a paso por perfil. Cada flecha es un punto donde **debe aplicarse Ley 2** (retroalimentación).

---

## MTX-UX-PER-002 · Carlos · Técnico

```
Inicia sesión
    ↓
Ve OTs asignadas
    ↓
Abre OT
    ↓
Consulta activo (historial)
    ↓
Registra trabajo / repuestos
    ↓
Adjunta fotos
    ↓
Cierra OT
    ↓
Dashboard del gerente actualizado
```

**Detalle:** [journeys/tecnico.md](journeys/tecnico.md)  
**North Stars:** TTCOT (principal), TTFFI (buscar activo)

---

## MTX-UX-PER-001 · Laura · Gerente

```
Inicia sesión
    ↓
Dashboard operativo
    ↓
Revisa alertas (stock, OT vencidas)
    ↓
Drill-down a detalle
    ↓
Exporta reporte PDF
    ↓
Comparte en reunión
```

**Detalle:** [journeys/gerente.md](journeys/gerente.md)  
**North Stars:** TTFFI, TTFAV

---

## MTX-UX-PER-003 · Valentina · Vendedora

```
Inicia sesión
    ↓
Nueva venta
    ↓
Busca / crea cliente
    ↓
Agrega productos (stock visible)
    ↓
Confirma pago
    ↓
Imprime / envía factura
```

**Detalle:** [journeys/vendedor.md](journeys/vendedor.md)

---

## MTX-UX-PER-004 · Roberto · Bodeguero

```
Inicia sesión
    ↓
Ve alertas stock crítico
    ↓
Registra entrada / salida
    ↓
Reserva repuesto para OT
    ↓
Concilia con conteo físico
```

**Detalle:** [journeys/bodeguero.md](journeys/bodeguero.md)

---

## MTX-UX-PER-005 · Andrea · Administradora

```
Registro empresa
    ↓
Elige sector y módulos
    ↓
Invita usuarios (rol por perfil MUX)
    ↓
Primera acción operativa del equipo
    ↓
Revisa auditoría / plan
```

**Detalle:** [journeys/administrador.md](journeys/administrador.md)  
**North Star:** TTFAV

---

## Reservados (stub journey)

| ID | Journey futuro |
|----|----------------|
| PER-006 | Auditoría → Checklist → Evidencia → Informe cumplimiento |
| PER-007 | Cotización recibida → Responde → OC → Factura |
| PER-008 | Login portal → Estado pedido → Historial → Soporte |

---

## Plantilla nuevo journey

```markdown
## MTX-UX-PER-0XX · Nombre · Rol
Paso 1 ↓ Paso 2 ↓ …
Feedback en cada paso: [toast/modal/estado]
Leyes aplicadas: 1, 2, 4, 5
Goals / Anti-Goals: goals.md
```
