# MPA-06-INT · Integraciones

**Código:** MPA-06-INT · Sprint 6.6

> Roustix no vive aislado. La plataforma debe **hablar** con las herramientas que las empresas latinoamericanas ya usan.

---

## 1 · Estrategia de integración

| Nivel | Enfoque |
|-------|---------|
| **Hoy** | Export/import archivos, PDF, correo transaccional |
| **Próximo** | API REST estable, webhooks |
| **Largo plazo** | Conectores ERP, Power BI, WhatsApp Business API |

**Principio:** integración = **evento o archivo con contrato claro**, no pantalla custom por cliente.

---

## 2 · Estado por canal

| Integración | Estado | Uso actual |
|-------------|--------|------------|
| **Correo** | 🟡 Parcial | Notificaciones, invitaciones equipo (evolución a plantillas MDL email) |
| **Excel** | ✅ Inventory | Import/export productos, movimientos |
| **PDF** | ✅ Ambos módulos | Reportes ReportLab — ver MRL (06) |
| **WhatsApp** | 📋 Planificado | Alertas OT, avisos stock (LatAm crítico) |
| **API REST** | 🟢 Sprint 22 | 22.0–22.5 ✅ completo |
| **Webhooks** | 🟢 Sprint 22 | Outbox, HMAC, reintentos, docs de integradores ✅ |
| **ERP** | 📋 Planificado | Siigo, Alegra, SAP B1 — por demanda sector |
| **Power BI** | 📋 Planificado | Export datasets / API Analytics |

---

## 3 · Excel

**Módulo:** Inventory  
**Patrón:** upload → validación → preview → commit transaccional

Casos de uso:

- Carga masiva de productos
- Actualización de precios y stock
- Export para análisis externo

**Regla MUX:** nunca perder datos del usuario en import fallido — mostrar errores por fila.

---

## 4 · PDF

**Motor:** ReportLab  
**Estándar visual:** MRL (06) — header, tablas, KPIs, firma

Reportes actuales incluyen órdenes de trabajo, inventario y listados operativos.

---

## 5 · API

| API | Audiencia | Auth |
|-----|-----------|------|
| Tenancy API | Integraciones por empresa | JWT |
| Admin API | Automatización interna | Token admin |
| API pública (Sprint 22) | Integraciones por empresa | API key con scopes; OAuth futuro |

Documentación de contratos → **[MAG-04 Recursos](/mag/chapters/04-recursos.md)** · [MAG (07)](/mag/) · **SDK (08)**.

---

## 6 · Webhooks (diseño futuro)

```
Roustix evento → POST https://cliente.com/hook
  Headers: X-Roustix-Signature
  Body: { event, tenant_id, payload, timestamp }
```

Eventos candidatos:

- `work_order.created` / `completed`
- `inventory.below_minimum`
- `purchase.received`
- `user.invited`

---

## 7 · ERP y contabilidad

Roustix **no reemplaza** el ERP en fase inicial. La integración exporta:

- Movimientos de compra/venta
- Referencias de activos y depreciación (futuro Finance)

Prioridad por mercado: Colombia y Venezuela primero (MCM-10-GTM).

---

## Siguiente

→ [MPA-07-SEC · Seguridad](07-seguridad.md) · [MAG · API Guide](/mag/)
