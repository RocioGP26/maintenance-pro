# COM-02 · Servicios Adicionales (Add-ons)

| Campo | Valor |
|-------|-------|
| **Código** | COM-02 |
| **Versión** | **1.4.0** |
| **Alineado a** | [COM-01 v1.4.0](COM-01-planes-licenciamiento.md) |
| **Moneda** | COP |

> Extiende capacidad **sin** forzar upgrade Start → Business → Enterprise.

---

## Almacenamiento (recurrente)

| Complemento | SKU | Precio / mes | Cuándo ofrecerlo |
|-------------|-----|-------------:|------------------|
| **+2 GB** | `ADD-STG-2G` | **100.000** | Uso ≥ 80% del cupo del plan |
| +5 GB | `ADD-STG-5G` | **220.000** | Crecimiento sostenido |
| +10 GB | `ADD-STG-10G` | **400.000** | Alto volumen de archivos |

**Copy sugerido (≥ 80%):**  
*«Estás próximo al límite de almacenamiento. ¿Deseas ampliar tu capacidad? +2 GB por $100.000 / mes.»*

**Producto:** banner en portal cliente (admins con configuración) + CTA a `contacto@roustix.com` · misma lógica en panel plataforma.

### Operación comercial · `ADD-STG-2G`

- Cobro mensual anticipado de **$100.000 COP** mediante factura/pago manual.
- Activación por SuperAdmin cuando el pago esté confirmado.
- Retiro al cierre del periodo mensual pagado; sin prorrateo automático.
- Los archivos existentes nunca se eliminan al retirar capacidad.
- Si el uso supera la cuota base, se bloquean nuevas cargas, pero se mantienen
  disponibles las descargas y eliminaciones.
- Activación y retiro quedan registrados en la auditoría de plataforma.

## Según cotización

| Complemento | SKU |
|-------------|-----|
| Usuarios adicionales (Start y Business) | `ADD-USR-COT` |
| Capacitación adicional | `ADD-TRN-COT` |
| Implementación en sitio | `ADD-ONB-SITE` |
| Integraciones especiales | `ADD-INT-COT` |

| Versión | Cambio |
|---------|--------|
| **1.4.0** | Operación comercial general; retiradas las reglas del piloto |
| **1.3.2** | Énfasis upsell +2 GB al 80% · alineado storage año 1 |
| **1.3.1** | Business |

*COM-02 · v1.4.0 · 2026*
