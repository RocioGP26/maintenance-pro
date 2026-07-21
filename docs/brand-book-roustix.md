# Brand Book — Roustix v1.0

> **Versión actual:** el Brand Book visual v2.0 vive en [`docs/brandbook/index.html`](brandbook/index.html).  
> **MDL** (componentes, tokens, patrones) es un proyecto independiente en [`docs/mdl/`](mdl/README.md) · catálogo en `/mdl/`.  
> **MUX** (Roustix User Experience Guide) en [`docs/mux/`](mux/README.md) · guía en `/mux/`.  
> Este archivo (v1.0) queda como referencia textual; el manual oficial se construye por sprints en HTML.

**Manual de Marca oficial**

Documento fundacional que define la esencia de Roustix y sirve como guía para diseño, desarrollo y comunicación. Toda decisión visual, de producto o de mensaje debe poder justificarse con este manual.

| Metadato | Valor |
|----------|-------|
| Versión | 1.0 |
| Fecha | Julio 2026 |
| Estado | Oficial |
| Audiencia | Equipo interno, diseño, desarrollo, marketing y partners |
| Fuente de verdad técnica | `static/css/app.css`, `app/branding.py` |

---

## Tabla de contenidos

1. [Historia de Roustix](#1-historia-de-roustix)
2. [Misión](#2-misión)
3. [Visión](#3-visión)
4. [Valores](#4-valores)
5. [Público objetivo](#5-público-objetivo)
6. [Personalidad de la marca](#6-personalidad-de-la-marca)
7. [Voz y tono de comunicación](#7-voz-y-tono-de-comunicación)
8. [Paleta de colores](#8-paleta-de-colores)
9. [Tipografía](#9-tipografía)
10. [Uso del logotipo](#10-uso-del-logotipo)
11. [Iconografía](#11-iconografía)
12. [Slogan](#12-slogan)
13. [Principios de diseño](#13-principios-de-diseño)
14. [Identidad visual](#14-identidad-visual)
15. [Casos de uso](#15-casos-de-uso)

---

## 1. Historia de Roustix

Roustix nace de una observación simple pero recurrente en plantas, talleres, flotas y comercios de Latinoamérica: **las operaciones críticas se gestionan con planillas, WhatsApp y memoria**, mientras que el software de mantenimiento e inventario parece hecho solo para corporaciones con equipos de TI.

El proyecto comenzó como una respuesta práctica a ese vacío: una plataforma web que uniera **mantenimiento industrial (CMMS)** e **inventario comercial** en un solo producto, sin imponer complejidad innecesaria. En lugar de duplicar el producto por industria, Roustix adoptó desde el inicio una arquitectura **multi-sector y modular**: la misma base de código se adapta a manufactura, logística, comercio, salud, minería, alimentos, construcción y educación mediante plantillas sectoriales y campos personalizados.

Roustix representa la convicción de que **una empresa pequeña o mediana merece las mismas herramientas de control operativo que una grande**, con onboarding guiado, datos aislados por empresa, métricas como MTBF y MTTR, y la libertad de activar solo los módulos que necesita.

Hoy, Roustix es más que un CMMS: es el sistema nervioso de la operación diaria — activos, órdenes de trabajo, repuestos, proveedores, ventas y stock — pensado para equipos que trabajan en planta, no en una oficina de proyectos.

---

## 2. Misión

**Dar a equipos de operaciones, mantenimiento y comercio la visibilidad y el control que necesitan para mantener sus activos y su negocio en marcha, con software claro, modular y accesible.**

Traducimos la misión en producto cuando:

- Un técnico puede registrar una OT en minutos, no en horas.
- Un gerente ve disponibilidad de planta sin pedir un reporte a nadie.
- Una tienda gestiona inventario comercial sin depender de hojas de cálculo.
- Cada empresa opera con sus propios datos, sectores y reglas, sin fricción.

---

## 3. Visión

**Ser la plataforma de referencia en Latinoamérica para la gestión operativa de PYMEs industriales y comerciales: donde mantenimiento e inventario conviven en un solo lugar, adaptados a cada sector, sin barreras de entrada.**

A cinco años, queremos que decir «lo tenemos en Roustix» signifique lo mismo que decir «tenemos control de la operación»: confianza, trazabilidad y decisiones basadas en datos reales.

---

## 4. Valores

### Claridad operativa
Priorizamos interfaces y mensajes que cualquier persona de planta entienda al primer vistazo. La complejidad técnica vive en el sistema, no en la pantalla.

### Modularidad con propósito
No vendemos funciones de relleno. Cada módulo — mantenimiento, inventario comercial — debe resolver un problema real y poder activarse de forma independiente.

### Adaptabilidad sectorial
Un montacargas no se gestiona igual que un producto de tienda. Respetamos las diferencias de cada industria sin fragmentar el producto.

### Confiabilidad y aislamiento
Los datos de cada empresa son sagrados. Seguridad, trazabilidad y uptime no son extras: son la base del contrato con el cliente.

### Accesibilidad honesta
Prueba gratuita, precios transparentes, sin contratos forzosos. Crecemos cuando el cliente ve valor, no cuando queda atrapado.

### Mejora continua
Escuchamos a quienes usan el sistema en el día a día — técnicos, jefes de mantenimiento, dueños de negocio — y priorizamos lo que reduce fricción real.

---

## 5. Público objetivo

### Perfil principal — Operaciones en PYME

| Segmento | Descripción | Necesidad clave |
|----------|-------------|-----------------|
| **Jefe de mantenimiento / planta** | Responsable de disponibilidad de equipos y cumplimiento preventivo | OTs, calendario, KPIs, repuestos |
| **Técnico de mantenimiento** | Ejecuta correctivos y preventivos en campo | Registro rápido, historial de activos, asignaciones |
| **Gerente general / operaciones** | Visión consolidada sin micromanagement | Dashboard, reportes, alertas |
| **Dueño o administrador de comercio** | Control de stock, ventas y cuentas por cobrar | Inventario comercial, POS, bajo stock |
| **Coordinador de flota / logística** | Activos móviles con campos específicos (placa, SOAT, km) | Plantillas sectoriales, campos custom |

### Sectores prioritarios

Manufactura · Logística · Comercio · Salud · Minería · Alimentos · Construcción · Educación · Industrial general

### Geografía y contexto

- **Mercado inicial:** Colombia (Bogotá como base operativa).
- **Idioma:** Español (Latinoamérica).
- **Tamaño de empresa:** PYMEs con 5–200 usuarios operativos; no el segmento enterprise tradicional con implementaciones de meses.

### Anti-persona (a quién no apuntamos)

- Grandes corporaciones que requieren ERP monolítico y consultoría de 12 meses.
- Equipos que buscan solo un chat interno o un CRM genérico.
- Organizaciones que no valoran el registro disciplinado de activos y operaciones.

---

## 6. Personalidad de la marca

Roustix es el colega experimentado del área de planta: **sabe del tema, habla claro y no presume**.

| Atributo | Somos | No somos |
|----------|-------|----------|
| **Confiable** | Precisos, consistentes, predecibles | Fríos o burocráticos |
| **Prácticos** | Orientados a la acción y al resultado | Teóricos o académicos |
| **Cercanos** | Humanos, directos, sin jerga innecesaria | Informales en exceso o condescendientes |
| **Profesionales** | Serios con la operación, pulidos en lo visual | Corporativos rígidos estilo consultora |
| **Modernos** | Software actual, limpio, eficiente | Startup ruidosa ni gimmick tecnológico |
| **Empoderadores** | Devolvemos control al cliente | Vendemos miedo o caos operativo |

**Arquetipo principal:** El **Guardián** (protege la continuidad operativa) con rasgos del **Creador** (herramientas que se adaptan al oficio de cada cliente).

---

## 7. Voz y tono de comunicación

### Voz (constante)

- **Directa:** Oraciones cortas. Verbos en imperativo cuando conviene («Registra la OT», «Consulta el stock»).
- **En español latinoamericano neutro:** Evitar regionalismos extremos; «ustedes» y vocabulario industrial comprensible en toda la región.
- **Orientada al beneficio:** Decir qué gana el usuario, no solo qué hace el botón.
- **Técnicamente honesta:** Nombrar MTBF, OT, CMMS cuando aporta credibilidad; explicar cuando el público es mixto.

### Tono (variable según contexto)

| Contexto | Tono | Ejemplo |
|----------|------|---------|
| Landing / marketing | Entusiasta, claro, sin hype vacío | «Empieza gratis 14 días · sin tarjeta» |
| UI operativa | Neutro, instructivo | «No hay órdenes abiertas para este activo» |
| Alertas y errores | Calmo, accionable | «Stock crítico en REF-002. Revisa el inventario.» |
| Soporte | Empático, resolutivo | «Entendemos la urgencia. Revisemos el acceso a tu cuenta.» |
| Documentación técnica | Preciso, estructurado | «El campo `criticidad` determina prioridad en el dashboard.» |

### Palabras que usamos

Operación · Activo · Orden de trabajo · Disponibilidad · Preventivo · Inventario · Control · Planta · Equipo · Módulo · Sector

### Palabras que evitamos

Revolutionary · Disruptivo · Synergy · Solución integral (sin contexto) · Líder del mercado (sin respaldo) · Fácil (sin demostrar por qué)

### Tratamiento del nombre

- **Roustix** — siempre con M mayúscula; nunca «ROUSTIX» en prosa (sí en logos o badges técnicos si aplica).
- No abreviar a «MTX» en comunicación externa salvo espacio muy limitado (icono de app).
- En código interno pueden coexistir alias históricos durante migraciones; en UI y marketing prevalece **Roustix**.

---

## 8. Paleta de colores

La paleta transmite **confianza industrial, precisión y calma**. El azul profundo ancla la seriedad; el acento activa la interacción; el fondo claro reduce fatiga visual en jornadas largas.

### Colores corporativos

| Nombre | Hex | Variable CSS | Uso |
|--------|-----|--------------|-----|
| **Primario** | `#042C53` | `--primario` | Títulos, encabezados, hover de botones primarios, énfasis editorial |
| **Acento** | `#185FA5` | `--acento` | Botones, enlaces, navegación activa, series principales en gráficos |
| **Claro** | `#378ADD` | `--claro` | Iconos sobre fondos oscuros, acentos secundarios, gradientes |
| **Fondo** | `#E6F1FB` | `--fondo` | Fondo de aplicación, bloques suaves, estados vacíos |
| **Sidebar** | `#1A2332` | `--sidebar-bg` | Barra lateral, zonas de navegación persistente |
| **Texto** | `#444441` | `--texto` | Cuerpo, etiquetas principales |
| **Secundario** | `#888780` | `--secundario` | Metadatos, hints, texto de apoyo |

### Colores semánticos (estado operativo)

No forman parte del logotipo; se reservan para **significado funcional** (disponibilidad, alertas, errores).

| Estado | Hex | Variable CSS |
|--------|-----|--------------|
| Éxito / Operativo | `#38A169` | `--success-green` |
| Advertencia / Mantenimiento | `#ED8936` | `--warning-orange` |
| Peligro / Falla | `#E53E3E` | `--danger-red` |

### Proporciones recomendadas

- **60%** fondos claros (`#E6F1FB`, blanco en tarjetas)
- **25%** acento y primario (UI, titulares)
- **10%** sidebar y zonas oscuras
- **5%** semánticos (solo donde comunican estado)

### Reglas de uso

1. Usar **variables CSS** en código; no hardcodear hex en plantillas nuevas.
2. No introducir azules legacy ajenos a la paleta (p. ej. `#3182CE`, `#2563EB` en producto; la landing comercial se alineará progresivamente).
3. Texto sobre fondo oscuro: **blanco** o `#E6F1FB` para subtítulos.
4. Contraste mínimo WCAG AA en textos de cuerpo.

### Gradientes oficiales

**Auth / Onboarding / Hero oscuro:**

```
sidebar-bg (#1A2332) → primario (#042C53) → fondo (#E6F1FB)
```

**Dashboard (sutil):**

```
rgba(55, 138, 221, 0.14) + rgba(24, 95, 165, 0.08) sobre --fondo
```

---

## 9. Tipografía

### Familia principal — Inter

[Inter](https://fonts.google.com/specimen/Inter) es la tipografía de Roustix: legible en pantallas industriales, neutral y profesional.

| Uso | Peso | Tamaño / estilo |
|-----|------|-----------------|
| Cuerpo de UI | 400 (Regular) | Base ~13px (`--app-root-font-size: 81.25%` sobre 16px) |
| Subtítulos, labels | 500 (Medium) | Escala modular de la UI |
| Títulos de página, KPIs | 600 (Semibold) | `--primario` o `--texto` |
| Tagline / eyebrow | 500 | Mayúsculas, `letter-spacing: 0.14em` — clase `.app-tagline` |

### Jerarquía tipográfica

```
H1 — page-title, landing hero     → Semibold, primario
H2 — secciones                    → Semibold, primario o texto
H3 — tarjetas, módulos            → Medium/Semibold
Body — párrafos, tablas           → Regular, texto
Caption — metadatos, hints        → Regular, secundario
Tagline — CMMS — INDUSTRIAL       → Medium, uppercase, secundario
```

### Fallbacks

```css
font-family: "Inter", system-ui, -apple-system, sans-serif;
```

### Reglas

- No mezclar más de **una familia** en producto (Inter únicamente).
- Evitar italics para énfasis; preferir peso o color `--acento`.
- En exportaciones PDF/Excel, mantener Inter o sustituir por Arial/Helvetica solo si Inter no está embebida.

---

## 10. Uso del logotipo

### Composición

El logotipo de Roustix combina **isotipo + wordmark** (archivo de referencia: `static/img/roustix-logo.svg`).

El favicon oficial utiliza el isotipo en formato cuadrado y se encuentra en
`static/img/roustix-favicon.svg`.

- **Isotipo:** símbolo reconocible a tamaños pequeños (favicon, sidebar colapsado).
- **Wordmark:** «Roustix» en Inter Semibold, alineado ópticamente con el isotipo.
- **Tagline opcional:** «Toda la operación. Una sola plataforma.» debajo o junto al wordmark en contextos institucionales.

### Zona de protección

Mantener un espacio libre equivalente a **la altura de la «M»** del wordmark en todos los lados del logo.

### Tamaños mínimos

| Contexto | Altura mínima |
|----------|---------------|
| UI compacta (sidebar, favicon) | 24 px |
| Auth / onboarding | 36–48 px |
| Landing / impresos | 48 px+ |

### Variantes permitidas

| Variante | Fondo | Uso |
|----------|-------|-----|
| Color sobre blanco | `#FFFFFF` | Default en app, documentos, landing |
| Color sobre panel blanco | Panel con `border-radius: 0.5rem`, sombra suave | Sidebar, login — clase `.brand-logo-panel` |
| Blanco / monocromo | Fondos `--primario` o `--sidebar-bg` | Hero oscuro, piezas de marketing |

### Usos incorrectos

- Estirar, rotar o inclinar el logo.
- Cambiar colores del isotipo fuera de la paleta.
- Colocar sobre fondos con poco contraste.
- Añadir sombras, contornos o efectos no aprobados.
- Sustituir el wordmark por tipografías decorativas.

### Coexistencia con logo de cliente

En el panel de empresa, el **logo del tenant** puede mostrarse junto al de Roustix. Roustix permanece en sidebar/footer; el logo del cliente en cabecera de empresa o informes exportados según configuración.

---

## 11. Iconografía

### Librería oficial

**Bootstrap Icons** (`bi-*`) — consistente, open source, legible a 16–24 px.

Carga vía CDN en plantillas (`_cdn_assets.html`). No mezclar con Font Awesome u otras librerías en la misma vista.

### Estilo

- **Trazo:** outline (default de Bootstrap Icons).
- **Color:** `--acento` en acciones primarias; `--secundario` en decorativos; blanco sobre fondos oscuros.
- **Tamaño:** 1rem–1.25rem en UI; 1.5–2rem en tarjetas de características.

### Iconos por dominio

| Dominio | Icono referencia | Código |
|---------|------------------|--------|
| Mantenimiento / OT | Llave ajustable | `bi-wrench-adjustable` |
| Activos / industrial | Engranajes | `bi-gear-wide-connected` |
| Inventario comercial | Carrito | `bi-cart3` |
| Proveedores | Tienda / escudo | `bi-shop` / `bi-shield-check` |
| Reportes / KPIs | Gráfico | `bi-bar-chart-line` |
| Alertas | Campana | `bi-bell` |
| Calendario / preventivo | Calendario | `bi-calendar-check` |
| Logística | Camión | `bi-truck` |
| Salud | Pulso | `bi-heart-pulse` |

### Iconos en KPI y estado

Alinear color del icono con el **estado semántico** (verde / naranja / rojo), no con el acento corporativo, cuando representen disponibilidad o salud de activos.

---

## 12. Slogan

### Slogan principal

> **Tu operación, bajo control.**

Frase corta, memorable y alineada con la promesa de producto: visibilidad sobre activos, OTs, inventario y métricas en un solo lugar.

### Tagline técnica

> **Toda la operación. Una sola plataforma.**

Usar debajo del logo o en metadata cuando se necesite categorizar el producto (SEO, fichas técnicas, app stores). Clase CSS: `.app-tagline`.

### Propuesta de valor extendida (no es slogan)

> Mantenimiento industrial e inventario comercial en una sola plataforma.

Válida para hero de landing, pitch decks y descripciones largas — no para firma de email o favicon.

### Mensajes alternativos aprobados (campañas)

- «Activa solo lo que necesitas.»
- «Diseñado para planta, no para PowerPoint.»
- «14 días gratis · sin tarjeta · sin contratos forzosos.»

---

## 13. Principios de diseño

### 1. Operación primero
Cada pantalla debe responder: **¿qué acción necesita el usuario ahora?** El dashboard destaca lo urgente; el detalle profundiza bajo demanda.

### 2. Densidad informacional controlada
Usuarios expertos prefieren ver más datos con menos scroll. La escala tipográfica compacta (81.25%) es intencional; no inflar tamaños sin motivo.

### 3. Consistencia sobre creatividad
Reutilizar componentes: `.dash-card`, `.kpi-card`, `.btn-primary`, `.app-tagline`. La novedad va en resolver problemas, no en reinventar botones.

### 4. Estado visible
Color semántico siempre que algo tenga estado operativo (operativo, mantenimiento, falla). No depender solo del texto.

### 5. Modularidad visible
Si el cliente no tiene inventario comercial, no mostramos nav de inventario. El producto debe sentirse hecho a medida.

### 6. Accesibilidad práctica
Contraste, labels en formularios, feedback en acciones destructivas. No es opcional en entornos industriales con diversidad de usuarios.

### 7. Mobile-aware, desktop-first
La operación crítica ocurre en escritorio; móvil debe ser usable para consultas y registros rápidos, no paridad pixel-perfect en v1.

### 8. Marca en segundo plano, cliente en primer plano
Roustix identifica la plataforma; el nombre de la empresa del cliente es el protagonista en su workspace.

---

## 14. Identidad visual

### Look & feel general

Roustix se ve **limpio, industrial y confiable**: fondos claros azulados, tarjetas blancas con sombra suave, sidebar oscuro anclado, acentos azules para acción. Evitamos el exceso de gradientes, glassmorphism o ilustraciones stock genéricas.

### Componentes distintivos

| Elemento | Descripción |
|--------|-------------|
| **Sidebar fija** | 280px, `--sidebar-bg`, logo en panel blanco |
| **Tarjetas dashboard** | Blanco, `--card-shadow`, cabecera con gradiente sutil `--dash-card-head-bg` |
| **KPI cards** | Borde superior de color según variante (primary / warning / success / neutral) |
| **Píldoras de filtro** | `.dash-pill-group` — filtros temporales y de sector |
| **Login / onboarding** | Split layout: hero oscuro con gradiente + formulario en zona clara |
| **Landing** | Fondo blanco, acentos amplios, mockups de producto reales (no fotos de stock) |

### Sombras y bordes

```css
--card-shadow: 0 1px 2px rgba(4, 44, 83, 0.05), 0 4px 14px rgba(4, 44, 83, 0.08);
--border-soft: rgba(4, 44, 83, 0.1);
```

### Gráficos (Chart.js)

| Serie | Color |
|-------|-------|
| Principal | `#185FA5` |
| Secundaria | `#378ADD` |
| Terciaria | `#042C53` |
| Fondo / vacío | `#E6F1FB` |
| Operativo | `#38A169` |
| Mantenimiento | `#ED8936` |
| Falla | `#E53E3E` |
| Neutro | `#888780` |

### Fotografía e ilustración

- Preferir **capturas reales del producto** o fotografía de planta auténtica (equipos, talleres, almacenes).
- Tratamiento: ligeramente desaturado; overlay `--primario` al 80% en heroes si hay texto encima.
- Evitar: gente señalando laptops sonriendo, iconos 3D genéricos, clipart.

### Motion

- Transiciones UI: 150–200 ms, ease-out.
- Sin animaciones decorativas en flujos operativos críticos (crear OT, cerrar incidencia).
- Loading: spinners discretos en `--acento`.

---

## 15. Casos de uso

### A. Aplicación web (producto)

| Superficie | Aplicación de marca |
|------------|---------------------|
| Sidebar | Logo en panel blanco, nav con item activo en `--acento` |
| Dashboard | KPI cards, gráficos con paleta oficial, títulos en `--primario` |
| Formularios | Labels `--texto`, hints `--secundario`, CTAs `btn-primary` |
| Login / onboarding | Gradiente corporativo, tagline `.app-tagline` |
| Emails transaccionales | Logo + slogan + tipografía Inter (pendiente plantilla) |

**Referencia técnica:** `static/css/app.css`, `templates/base.html`

### B. Landing y marketing web

| Elemento | Directriz |
|----------|-----------|
| Hero | Propuesta de valor + CTA «Empieza gratis» |
| Secciones | Eyebrow en mayúsculas espaciadas (como `.app-tagline`) |
| Precios | Destacar plan popular con `--acento`; honestidad en límites |
| Footer | © Roustix · Bogotá, Colombia |

**Referencia:** `templates/landing/index.html`, `static/css/landing.css` (alineación de acentos en curso)

### C. Documentación y soporte

- Títulos en `#042C53`, links en `#185FA5`.
- Screenshots con marco de navegador o dispositivo neutro.
- Mantener nombre **Roustix** en títulos de ayuda.

### D. Presentaciones comerciales

- Slide de apertura: logo + slogan + tagline.
- Paleta restrictiva: blanco, primario, acento.
- Una métrica por slide; evitar párrafos densos.

### E. Redes sociales

| Formato | Contenido sugerido |
|---------|-------------------|
| LinkedIn | Casos de uso sectoriales, tips de mantenimiento, KPIs |
| Instagram / Facebook | Cultura operativa, behind-the-scenes de planta |
| WhatsApp / ventas | Tono cercano; CTA a prueba gratuita |

Plantillas: logo en esquina inferior derecha, margen de protección, fondo `--fondo` o blanco.

### F. Merchandising y eventos (futuro)

- Camisetas: isotipo en pecho, wordmark en espalda.
- Stickers: isotipo solo, mínimo 3 cm.
- Stand feria industrial: hero oscuro `--sidebar-bg`, demo en vivo del producto.

### G. Código y repositorio

Constantes en `app/branding.py`:

```python
APP_NAME = "Roustix"           # objetivo de marca
APP_TAGLINE = "Toda la operación. Una sola plataforma."
APP_LOGO_PATH = "img/roustix-logo.svg"
```

Variables CSS en `:root` de `app.css` — **no duplicar** en módulos salvo excepción documentada.

---

## Apéndice A — Checklist para entregables nuevos

- [ ] ¿Usa la paleta via variables CSS?
- [ ] ¿Tipografía Inter con pesos correctos?
- [ ] ¿Botones primarios con `btn-primary` / `--acento`?
- [ ] ¿Estados operativos con colores semánticos?
- [ ] ¿Iconos Bootstrap Icons únicamente?
- [ ] ¿Copy alineado con voz Roustix (directo, sin hype)?
- [ ] ¿Logo con zona de protección y tamaño mínimo?
- [ ] ¿Nombre «Roustix» escrito correctamente?

---

## Apéndice B — Relación con otros documentos

| Documento | Alcance |
|-----------|---------|
| **Este Brand Book** | Estrategia de marca, voz, identidad completa |
| `docs/marca-roustix.md` | Guía técnica rápida para CSS/plantillas |
| `docs/arquitectura-sectores.md` | Arquitectura de producto multi-sector |

---

## Control de versiones

| Versión | Fecha | Cambios |
|---------|-------|---------|
| 1.0 | Julio 2026 | Publicación inicial — 15 secciones oficiales |

---

*Roustix — Tu operación, bajo control.*
