# RTX-PRIV-ANX-002 · Matriz de Conservación

| Campo | Valor |
|-------|-------|
| **Código** | RTX-PRIV-ANX-002 |
| **Versión** | **0.2.0** |
| **Estado** | 🟡 Borrador de plazos propuestos · validar jurídicamente |
| **Padre** | [RTX-PRIV-001](../RTX-PRIV-001-politica-privacidad.md) |
| **Fecha** | 2026-08-03 |

---

## Propósito

Definir por categoría de dato el plazo de conservación, la base y la acción al vencimiento.

> Los plazos marcados como **propuesta** no son definitivos hasta revisión jurídica / tributaria y decisión de los socios.

---

## Matriz

| Categoría | Ejemplo | Plazo (propuesta) | Base / motivo | Acción al vencimiento |
|-----------|---------|-------------------|---------------|----------------------|
| Cuenta de usuario | Email, nombre, rol | Vida de la cuenta + **30 días** tras baja | Prestación del servicio | Eliminación / anonimización |
| Datos de operación del Cliente | OT, activos, inventarios | Vida del contrato + plazo de exportación de la Orden (sugerido **30 días**) | Encargo / contrato | Exportación + eliminación según Orden |
| Logs técnicos | Access / error | **90 días** | Seguridad / operación | Rotación automática |
| Backups | Instantáneas BD / objetos | Según rotación operativa (piloto: alinear Guía Operativa) | Continuidad | Caducidad programada |
| Soporte | Tickets, correos | **24 meses** desde cierre del ticket | Seguimiento / defensa | Archivo o eliminación |
| Facturación | Facturas, pagos | **[PENDIENTE · obligación tributaria colombiana]** | Deber legal | Conservación legal |
| Marketing (si aplica) | Leads landing | Hasta revocación o **24 meses** de inactividad | Autorización | Supresión |
| Piloto cerrado | Tenant piloto | Según constancia de salida | Contrato piloto | Exportar / eliminar |

---

## Notas

1. La conservación legal tributaria puede prevalecer sobre la eliminación operativa.  
2. Alinear con RTX-LEGAL-002 / Orden (exportación) y con la Guía Operativa.  
3. No declarar «eliminación total» si existen respaldos residuales dentro de la ventana de rotación.

---

## Control de cambios

| Versión | Fecha | Cambio |
|---------|-------|--------|
| **0.1.0** | 2026-08-03 | Plantilla inicial |
| **0.2.0** | 2026-08-03 | Plazos propuestos de trabajo |

---

*RTX-PRIV-ANX-002 · v0.2.0*
