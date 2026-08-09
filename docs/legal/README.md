# LEG · Sistema Documental Legal de Roustix

**Suite:** LEG · Legal & Compliance  
**Versión del sistema:** **v1.2.0**  
**Control maestro:** [RTX-DOC-000](RTX-DOC-000-control-versiones.md)  
**Estado:** 🟡 Borrador interno · sujeto a revisión jurídica colombiana

> Paquete documental oficial para la etapa comercial de Roustix.  
> Cada documento tiene un propósito específico; no se repite información entre ellos.

---

## Árbol oficial

```
RTX-DOC-000 · Control de Versiones Documentales
├── RTX-LEGAL-001 · Términos y Condiciones
├── RTX-LEGAL-002 · Contrato SaaS
├── RTX-PRIV-001  · Política de Privacidad
│   ├── RTX-PRIV-ANX-001 · Lista de Subencargados
│   ├── RTX-PRIV-ANX-002 · Matriz de Conservación
│   └── RTX-PRIV-ANX-003 · Registro de Flujos Internacionales
├── RTX-SLA-001   · Acuerdo de Nivel de Servicio
└── RTX-SUP-001   · Política de Soporte
```

## Quién acepta / firma qué

| Documento | Audiencia | Momento |
|-----------|-----------|---------|
| **RTX-LEGAL-001** | Todos los usuarios | Aceptación al registrarse / usar la plataforma |
| **RTX-LEGAL-002** | Empresa cliente (representante autorizado) | Firma comercial (post-piloto o venta directa) |
| **RTX-PRIV-001** | Titulares / usuarios / clientes | Publicación + aceptación en flujos de datos |
| **RTX-SLA-001** | Solo si el contrato lo anexa | Business+/Enterprise o SLA cotizado |
| **RTX-SUP-001** | Clientes con servicio activo | Referenciado por contrato y plan |

## Separación de responsabilidades

| Documento | Regula | No regula |
|-----------|--------|-----------|
| LEGAL-001 | Reglas de uso de la plataforma | Precio, plan, facturación comercial |
| LEGAL-002 | Relación comercial Cliente ↔ Prestador | Detalle operativo de tickets (→ SUP) ni métricas SLA (→ SLA) |
| PRIV-001 | Tratamiento de datos personales | Condiciones comerciales |
| SLA-001 | Disponibilidad y objetivos de respuesta *cuando se anexa* | Soporte cotidiano sin compromiso de nivel |
| SUP-001 | Cómo pedir ayuda y qué incluye el soporte | Compromisos de uptime / créditos |

## Fuentes comerciales (no duplicar)

Los precios, cupos y add-ons viven en **COM**, no en los textos legales:

- [COM-01 · Planes](../com/COM-01-planes-licenciamiento.md)
- [COM-02 · Add-ons](../com/COM-02-servicios-adicionales.md)
- [COM-03 · Piloto](../com/COM-03-programa-piloto-fundadores.md)

El Contrato SaaS y el Acta de Servicio **referencian** COM; no copian tarifas salvo en la orden firmada.

## Relación con el paquete piloto (PIL- / SAA-)

| Código piloto | Rol | Relación con LEG |
|---------------|-----|------------------|
| PIL-LEG-001 | Términos del piloto | Temporal · no sustituye LEGAL-001 en producción |
| PIL-LEG-002 | Paquete privacidad piloto | Base de PRIV-001 |
| PIL-LEG-003 | Acuerdo de transmisión (DPA) | Complemento de PRIV / anexo contractual |
| SAA-LEG-001 | Borrador contrato SaaS | Superado por **RTX-LEGAL-002** |
| SAA-ACT-001 | Acta de plan | Orden / carátula operativa del contrato |
| PIL-GUI-001 | Guía operativa | Alimenta SUP-001 y objetivos técnicos |

Plantillas DOCX: `docs/production-readiness/templates/`.

## Orden de elaboración (v1.1)

1. ✅ **RTX-LEGAL-002** — Contrato SaaS (borrador)  
2. ✅ **RTX-SUP-001** — Política de Soporte (borrador)  
3. ✅ **RTX-SLA-001** — SLA (borrador no vinculante)  
4. ✅ **RTX-LEGAL-001** — Términos (borrador v0.3)  
5. ✅ **RTX-PRIV-001** — Privacidad Partes A/B/C (borrador v0.2)  
6. 🟡 **Anexos PRIV** — ANX-001/003 con stack prod; regiones cloud por validar en consolas  
7. ✅ **Rutas públicas** — `/terminos` · `/privacidad` muestran «próximamente» mientras sean borrador  
8. ✅ **SuperAdmin** — `/platform/legal` descarga PDF de todo el catálogo LEG

## Antes de publicar o firmar

- [ ] Identidad jurídica del prestador (sociedad o personas naturales definitivas)
- [ ] NIT / domicilio / canal de titulares
- [ ] Revisión jurídica colombiana
- [ ] Validación tributaria / facturación
- [ ] Confirmación operativa de objetivos SLA (infraestructura)
- [x] Correo corporativo definitivo (`contacto@roustix.com`)

## Índice de archivos

| Código | Archivo | Estado |
|--------|---------|--------|
| RTX-DOC-000 | [RTX-DOC-000-control-versiones.md](RTX-DOC-000-control-versiones.md) | ✅ v1.2.0 |
| RTX-LEGAL-001 | [RTX-LEGAL-001-terminos-condiciones.md](RTX-LEGAL-001-terminos-condiciones.md) | 🟡 Borrador v0.3 · `/terminos` |
| RTX-LEGAL-002 | [RTX-LEGAL-002-contrato-saas.md](RTX-LEGAL-002-contrato-saas.md) | 🟡 Borrador |
| RTX-PRIV-001 | [RTX-PRIV-001-politica-privacidad.md](RTX-PRIV-001-politica-privacidad.md) | 🟡 Borrador v0.2 · `/privacidad` |
| RTX-PRIV-ANX-001 | [anexos/RTX-PRIV-ANX-001-subencargados.md](anexos/RTX-PRIV-ANX-001-subencargados.md) | 🟡 Borrador operativo |
| RTX-PRIV-ANX-002 | [anexos/RTX-PRIV-ANX-002-matriz-conservacion.md](anexos/RTX-PRIV-ANX-002-matriz-conservacion.md) | 🟡 Borrador plazos |
| RTX-PRIV-ANX-003 | [anexos/RTX-PRIV-ANX-003-flujos-internacionales.md](anexos/RTX-PRIV-ANX-003-flujos-internacionales.md) | 🟡 Borrador flujos |
| RTX-SLA-001 | [RTX-SLA-001-acuerdo-nivel-servicio.md](RTX-SLA-001-acuerdo-nivel-servicio.md) | 🟡 Borrador |
| RTX-SUP-001 | [RTX-SUP-001-politica-soporte.md](RTX-SUP-001-politica-soporte.md) | 🟡 Borrador |

---

*LEG · Sistema Documental Legal Roustix · v1.2.0 · 2026-08-03*
