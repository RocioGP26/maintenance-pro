# MTX-UX-DEC · Decision Matrix

Matriz de decisiones UX. Cuando existan **dos formas de construir una pantalla**, este documento resuelve la discusión.

**Regla:** Si la situación coincide con una fila, la decisión es obligatoria — no negociable en code review.

---

## Matriz principal

| ID | Situación | Decisión | Ley / MDL |
|----|-----------|----------|-----------|
| DEC-001 | Más de **8 campos** visibles | Dividir en pasos (wizard o secciones) | Ley 4 |
| DEC-002 | Acción **irreversible** (eliminar, anular) | Modal de confirmación + consecuencia en texto | `MTX-PAT-007` |
| DEC-003 | **Error del usuario** (validación) | Explicar qué falló + sugerir solución concreta | Ley 4 · [copy.md](copy.md) |
| DEC-004 | Proceso **> 30 s** (import, export, batch) | Barra o indicador de progreso + cancelable si aplica | Ley 2 |
| DEC-005 | **Sin información** (lista vacía, sin resultados) | Empty State + CTA · nunca pantalla en blanco | Ley 1 · `MTX-EMP-001` |
| DEC-006 | **Dos acciones primarias** compitiendo | Una primary, resto secondary/ghost | Ley 5 |
| DEC-007 | Formulario **> 3 pantallas** de scroll en mobile | Considerar wizard o reducir campos | DEC-001 |
| DEC-008 | Dato crítico sin contexto (KPI suelto) | Label + fecha actualización + enlace a detalle | TTFFI |
| DEC-009 | Permiso insuficiente | Ocultar acción · no mostrar botón que lleva a 403 | NAV-009 |
| DEC-010 | Destructiva en tabla (eliminar fila) | Confirmación · danger button · no undo silencioso | DEC-002 |
| DEC-011 | Búsqueda sin resultados | «No encontramos…» + sugerir filtros · no «Error» | [copy.md](copy.md) |
| DEC-012 | Cambios sin guardar al navegar | Aviso blocking · Ley 3 | Ley 3 |
| DEC-013 | Más de **5 ítems** en menú contextual | Simplificar o agrupar | NAV-003 |
| DEC-014 | Tabla **> 7 columnas** en mobile | Scroll horizontal + columnas prioritarias fijas | MDL responsive |
| DEC-015 | Adjunto obligatorio (evidencia OT) | Indicar antes de cerrar · no fallar al final | Ley 4 |

---

## Árbol rápido (code review)

```
¿Pantalla sin datos?
  → Sí → Empty State + CTA (DEC-005)

¿Elimina o anula?
  → Sí → Confirmación (DEC-002)

¿> 8 campos?
  → Sí → Pasos (DEC-001)

¿Error de validación?
  → Explicar + sugerir (DEC-003)

¿Acción completada?
  → Feedback visible (Ley 2)
```

---

## Cuándo escalar

Si ninguna fila aplica y hay empate entre dos diseños:

1. Consultar **Goals** del perfil principal ([goals.md](goals.md))
2. Medir impacto en [measure.md](measure.md) (TTFAV / TTCOT / TTFFI)
3. Registrar decisión en MADR si es arquitectura persistente

---

## Registro de excepciones

Una excepción a DEC-* requiere:

- Issue/PR con etiqueta `ux-exception`
- Ley o DEC incumplida
- Justificación + plan para corregir
- Aprobación en review

Sin registro → no merge.
