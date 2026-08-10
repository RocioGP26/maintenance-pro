# RTX-DOC-000 · Control de Versiones Documentales

| Campo | Valor |
|-------|-------|
| **Código** | RTX-DOC-000 |
| **Suite** | LEG · Sistema Documental Legal de Roustix |
| **Versión del sistema** | **1.2.2** |
| **Fecha** | 2026-08-09 |
| **Estado** | ✅ Activo (gobierno interno) |
| **Responsable de mantenimiento** | Socios Roustix · revisión jurídica externa |

---

## 1 · Propósito

Este documento es el **índice maestro** del paquete legal. Define códigos, versiones, estados, dependencias y reglas de cambio. Ningún documento legal se publica, firma o enlaza desde el producto sin estar registrado aquí.

---

## 2 · Catálogo vigente

| Código | Título | Ver. | Estado | Público | Firma |
|--------|--------|-----:|--------|:------:|:-----:|
| RTX-LEGAL-001 | Términos y Condiciones | 0.3.0 | Borrador | Futuro | Aceptación click-wrap |
| RTX-LEGAL-002 | Contrato SaaS | 0.1.0 | Borrador | No | Firma representante |
| RTX-PRIV-001 | Política de Privacidad | 0.2.0 | Borrador | Futuro | Aceptación / aviso |
| RTX-PRIV-ANX-001 | Lista de Subencargados | 0.2.0 | Borrador operativo | Anexo PRIV | — |
| RTX-PRIV-ANX-002 | Matriz de Conservación | 0.2.0 | Borrador plazos | Anexo PRIV | — |
| RTX-PRIV-ANX-003 | Flujos Internacionales | 0.2.0 | Borrador flujos | Anexo PRIV | — |
| RTX-SLA-001 | Acuerdo de Nivel de Servicio | 0.1.0 | Borrador | Solo anexo contractual | Firma si se anexa |
| RTX-SUP-001 | Política de Soporte | 0.2.0 | Borrador | Referencia cliente | Referenciado |

**Estados permitidos:** `Esqueleto` · `Borrador` · `Revisión jurídica` · `Aprobado` · `Vigente` · `Obsoleto`

---

## 3 · Reglas de no duplicación

1. **Precios y cupos** → solo en COM-01 / COM-02 / orden firmada.  
2. **Cómo pedir ayuda** → solo en RTX-SUP-001.  
3. **Uptime y tiempos objetivo de respuesta** → solo en RTX-SLA-001 (cuando se anexe).  
4. **Tratamiento de datos** → solo en RTX-PRIV-001 y anexos.  
5. **Uso de la plataforma por cualquier usuario** → RTX-LEGAL-001.  
6. **Relación comercial empresa-cliente** → RTX-LEGAL-002.

Si un tema aparece en dos documentos, el de propósito específico prevalece; el otro solo referencia el código.

---

## 4 · Jerarquía contractual

```
RTX-LEGAL-002 (Contrato SaaS)
  ├── Orden comercial / Acta de Servicio (SAA-ACT-001 o equivalente)
  ├── RTX-PRIV-001 (+ anexos)
  ├── RTX-SUP-001 (referencia operativa)
  ├── RTX-SLA-001 (solo si se anexa expresamente)
  └── Addenda firmadas
```

Para usuarios finales sin firma comercial: **RTX-LEGAL-001** + **RTX-PRIV-001**.

---

## 5 · Versionado

Formato: `MAJOR.MINOR.PATCH`

| Tipo de cambio | Impacto |
|----------------|---------|
| Cambio de derechos, obligaciones, jurisdicción, responsabilidad | **MAJOR** |
| Nueva sección, plan, canal o anexo material | **MINOR** |
| Corrección editorial / tipografía | **PATCH** |

Al subir a **Vigente**, se registra fecha de vigencia y se archiva la versión anterior.

---

## 6 · Placeholders prohibidos en versión Vigente

Ningún documento en estado **Vigente** puede contener:

- `[PENDIENTE]` / `________________`
- Identidad jurídica incompleta del prestador
- Objetivos SLA presentados como compromiso sin confirmación operativa
- Datos personales de socios en repositorio Git (usar almacenamiento privado)

---

## 7 · Historial del sistema

| Ver. sistema | Fecha | Cambio |
|--------------|-------|--------|
| **1.0.0** | 2026-08-03 | Creación del Sistema Documental Legal · paquete inicial RTX-* |
| **1.1.0** | 2026-08-03 | LEGAL-001 v0.2 y PRIV-001 v0.2 (borradores completos desde PIL-*) |
| **1.2.0** | 2026-08-03 | ANX-001/003 infra real · rutas públicas `/terminos` y `/privacidad` |
| **1.2.1** | 2026-08-03 | LEGAL-001 v0.3 (Alcance, mantenimiento, actualizaciones, datos, ley) |
| **1.2.2** | 2026-08-09 | Canal corporativo aprobado, piloto archivado y paquete comercial general enlazado |

---

## 8 · Contacto documental

| Tema | Canal |
|------|-------|
| Solicitudes de cambio documental | Socios Roustix |
| Revisión jurídica | Asesoría externa (por designar) |
| Publicación en producto | Tras estado **Vigente** + gate go-live |

---

*RTX-DOC-000 · v1.2.2 · 2026-08-09*
