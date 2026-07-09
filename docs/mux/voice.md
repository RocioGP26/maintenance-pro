# UX · Voz de la plataforma

La **voz de marca** vive en el Brand Book (marketing, landing).  
La **voz de plataforma** vive aquí — lo que lee el gerente a las 7am y el técnico a las 11pm.

## Diferencia clave

| Contexto | Documento | Tono |
|----------|-----------|------|
| Landing, email marketing | Brand Book | Entusiasta, claro, sin hype |
| Pantallas operativas | **UX (este doc)** | Neutro, instructivo, accionable |
| Alertas y errores | messaging.md | Calmo, con siguiente paso |

## Principios de voz en producto

### 1. Hablar como operación, no como software

| ✅ | ❌ |
|----|-----|
| «Orden de trabajo creada» | «Registro insertado correctamente» |
| «Stock bajo en REF-002» | «Warning: threshold exceeded» |
| «Activo operativo» | «Status OK» |

### 2. Oraciones cortas. Verbo primero.

- «Registra la OT»
- «Consulta el inventario»
- «Invita a tu equipo»

### 3. Beneficio cuando hay espacio

Subtítulos y empty states pueden explicar **por qué** importa:

> «Cuando registres órdenes de trabajo, verás aquí las abiertas por prioridad.»

### 4. Español latinoamericano neutro

- «Ustedes» en onboarding; «tú» evitable en UI formal
- Sin regionalismos extremos (ché, vos, parce en producto)
- OT, activo, inventario — vocabulario industrial compartido

### 5. Honestidad técnica selectiva

Usar MTBF, MTTR, CMMS cuando el perfil lo espera (gerente). Para técnico: «Tiempo entre fallas» la primera vez, sigla después.

## Palabras Maintix (producto)

**Usar:** operación · activo · orden de trabajo · disponibilidad · inventario · planta · módulo · sede · cliente · stock

**Evitar en UI:** revolucionario · disruptivo · synergy · líder del mercado · fácil (sin demostrar)

## Tratamiento del nombre

- **Maintix** en prosa UI (M mayúscula)
- **MAINTIX** solo en logos, emails header, PDF
- No «MTX» en copy de usuario

## Tono por perfil (resumen)

| Perfil | Tono |
|--------|------|
| Gerente | Ejecutivo, datos primero |
| Técnico | Imperativo, mínimo texto |
| Vendedor | Ágil, confirmaciones breves |
| Bodeguero | Factual, cantidades exactas |
| Administrador | Estructurado, paso a paso |

## Microcopy recurrente

| Elemento | Regla |
|----------|-------|
| Botón guardar | «Guardar» / «Guardar cambios» — no «Submit» |
| Cancelar | «Cancelar» — nunca «Abort» |
| Eliminar | Verbo + objeto: «Eliminar activo» |
| Placeholder | Ejemplo real: «CPS-001», no «Ingrese valor» |
| Fecha vacía | «Sin fecha» — no «null» o «—» solo |

## Relación con MDL

Los textos viven en plantillas Jinja y archivos i18n (futuro). Los componentes `mtx-*` muestran el copy; no lo inventan.

Ver [messaging.md](messaging.md) para plantillas de éxito, error y ayuda.
