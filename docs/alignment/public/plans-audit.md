# Auditoría · Planes

**Actualización:** 2026-07-29 · **Estado:** ✅ Alineado para piloto

**Rutas:** `/#precios` · catálogo BD · `app/platform_config_service.py` · `app/models.py`

**Referencia:** [MCM-04 · Planes SaaS](/mcm/chapters/04-planes-saas.md)

## Oferta oficial

| Plan comercial | Clave técnica | Precio mensual | Landing | Estado |
|----------------|---------------|---------------:|---------|--------|
| **Start** | `basico` | $1.000.000 COP | Visible con precio | ✅ |
| **Business** | `grow` *(legacy estable)* | $1.500.000 COP | Visible con precio | ✅ |
| **Enterprise** | `enterprise` | Desde $2.500.000 interno | Contactar | ✅ |
| Scale *(legacy)* | `profesional` | $580.000 COP | Oculto | ✅ No ofertar |

## Operación del piloto

- Trial de **15 días**, sin tarjeta.
- Facturación y confirmación de pago manual desde SuperAdmin.
- Asignación o cambio manual entre Start, Business y Enterprise con auditoría.
- La pasarela de pago está diferida a postpiloto y no bloquea la operación actual.

## Fuentes vigentes

- Oferta y precios: `PLANES_SEED` + COM-01.
- Claves compatibles: `PlanTipo` y `CatalogoPlan`.
- Landing y onboarding consumen el catálogo de plataforma.

## Checklist

- [x] Start · Business · Enterprise en superficies comerciales.
- [x] Trial 15 días.
- [x] Precios reales de Start y Business.
- [x] Enterprise con CTA de contacto.
- [x] Scale oculto y marcado como legacy.
- [x] Business conserva `grow` para compatibilidad.
