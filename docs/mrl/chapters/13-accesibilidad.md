# MRL-13-A11Y · Accesibilidad

**Código:** MRL-13-A11Y · Complemento Sprint 7

> Reportes impresos y PDFs compartidos deben ser **legibles y comprensibles** fuera del contexto digital — incluida impresión en escala de grises.

Alineado con [MUX accesibilidad](/mux/) y MRL-07 colores.

---

## 1 · Principio

No depender solo del color en pantalla. Un gerente puede imprimir en blanco y negro, faxear un escaneo o proyectar en sala con poco contraste.

**MRL + accesibilidad = información clara en cualquier medio.**

---

## 2 · Reglas obligatorias

| # | Regla | En la práctica |
|---|-------|----------------|
| 1 | **Contraste adecuado para impresión** | Texto cuerpo `#444441` sobre blanco · cabecera tabla `#042C53` con texto blanco |
| 2 | **No depender solo del color** | Estado crítico = texto «Crítico» + icono/color · no solo rojo |
| 3 | **Tipografía mínima legible** | Cuerpo ≥ 9pt · metadata ≥ 8pt · títulos ≥ 11pt |
| 4 | **Gráficos comprensibles en escala de grises** | Patrones o etiquetas en barras · no solo color de serie |
| 5 | **Tablas con encabezado repetido** | Header row en salto de página |
| 6 | **Orden de lectura lógico** | Header → KPI → contenido → footer; sin saltos confusos |

---

## 3 · Contraste · referencia

| Elemento | Ratio mínimo | Notas |
|----------|--------------|-------|
| Texto cuerpo | 4.5:1 | WCAG AA |
| Texto grande (≥14pt bold) | 3:1 | Títulos MRL |
| Cabecera tabla | 7:1+ | Azul oscuro + blanco |

Probar export PDF en escala de grises antes de release de plantilla.

---

## 4 · Color semántico + texto

| Estado | Color MRL-07 | Texto obligatorio |
|--------|--------------|-------------------|
| OK | Verde | «Operativo» / «Disponible» |
| Crítico | Rojo | «Crítico» / «Vencido» |
| Advertencia | Ámbar | «Advertencia» / «Próximo» |
| Info | Azul | Etiqueta descriptiva |

En tablas: columna «Estado» con palabra, no solo celda coloreada.

---

## 5 · Gráficos

- Barras: etiqueta de valor encima o al lado
- Líneas: marcadores en puntos clave si &lt; 12 puntos
- Pie/donut: máx. 5 segmentos + leyenda con **nombre**, no solo color
- Prohibido: 3D, degradados que pierdan forma en B/N (MRL-08)

---

## 6 · Impresión y contexto LatAm

| Contexto | Consideración |
|----------|---------------|
| Impresora láser oficina | Márgenes MRL-03 · no fondos oscuros en cuerpo |
| Escaneo / WhatsApp | Contraste alto · fuentes sans-serif |
| Archivo legal | Metadata MRL-11 completa |
| Proyección | Evitar texto &lt; 9pt en gráficos |

---

## 7 · Checklist plantilla (PR)

- [ ] ¿Legible en escala de grises?
- [ ] ¿Estados con texto, no solo color?
- [ ] ¿Tipografía ≥ mínimos?
- [ ] ¿Gráficos con etiquetas?
- [ ] ¿Contraste cabecera tabla OK?

---

→ [Índice MRL](/mrl/) · [MUX A11Y](/mux/)

---

*MRL-13-A11Y · Roustix Report Language · 2026*
