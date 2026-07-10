# MKT-05 · Landing Page y sitio web

**Código:** MKT-05 · Sprint 12.5 · **Entregado**

> El sitio web de Maintix no existe para explicar todo el producto. Existe para convertir visitantes en trials, demostraciones y oportunidades comerciales.

**Toda la operación. Una sola plataforma.**

**Prerequisitos:** [MKT-01 · Identidad y mensajes](01-identidad-mensajes-marca.md) · [MKT-02 · Elevator Pitch](02-elevator-pitch-guiones.md) · [MKT-04 · Presentación comercial](04-presentacion-comercial.md) · [MCM-01](/mcm/chapters/01-intro-filosofia-comercial.md)

**Referencia diseño:** [MDL](/mdl/) · [MUX](/mux/)

---

## Objetivo del capítulo

Definir la **estructura oficial del sitio web** de Maintix: arquitectura de la landing principal, mensajes por sección, CTAs, principios de conversión y criterios para futuras páginas comerciales.

Este documento sirve como referencia para:

| Equipo | Uso |
|--------|-----|
| **Diseño (MDL)** | Componentes · tokens · layout |
| **UX (MUX)** | Recorridos · jerarquía · copy |
| **Marketing** | Mensajes · SEO · conversión |
| **Desarrollo web** | Secciones · rutas · CTAs |
| **Partners** | Co-branding · landings futuras |

**Implementación actual:** `templates/landing/` · `static/css/landing.css` — alinear a esta guía.

---

## 1 · Filosofía

El visitante debe comprender **tres ideas en menos de un minuto**:

| # | Idea |
|---|------|
| 1 | ¿Qué problema resuelve Maintix? |
| 2 | ¿Cómo lo resuelve? |
| 3 | ¿Cómo empezar hoy? |

**Regla:** si una sección no ayuda a responder alguna de estas preguntas, probablemente **no debería estar** en la landing.

→ [MKT-01 · Arquitectura del mensaje](01-identidad-mensajes-marca.md#11--arquitectura-del-mensaje)

---

## 2 · Objetivos del sitio

| Objetivo | Prioridad |
|----------|-----------|
| Generar pruebas gratuitas | ⭐⭐⭐⭐⭐ |
| Solicitar demostraciones | ⭐⭐⭐⭐ |
| Explicar el producto | ⭐⭐⭐⭐ |
| Construir confianza | ⭐⭐⭐⭐ |
| Posicionar la marca | ⭐⭐⭐ |

---

## 3 · Flujo esperado

```
Visitante
    ↓
Problema
    ↓
Maintix
    ↓
Beneficios
    ↓
Sectores
    ↓
Planes
    ↓
Confianza
    ↓
Trial
```

Cada sección de la home debe seguir este orden narrativo.

---

## 4 · Arquitectura del sitio

### Páginas principales

| Página | Estado | URL sugerida |
|--------|--------|--------------|
| **Inicio** | Obligatoria | `/` |
| **Producto** | Obligatoria | `/producto` |
| **Mantenimiento** | Obligatoria | `/mantenimiento` |
| **Inventario** | Obligatoria | `/inventario` |
| **Planes** | Obligatoria | `/planes` |
| **Demo** | Obligatoria | `/demo` |
| **Casos de éxito** | Próximo sprint | `/casos` |
| **Recursos / Blog** | Roadmap | `/recursos` |
| **Partners** | Roadmap | `/partners` |
| **Contacto** | Obligatoria | `/contacto` |

### Roadmap del sitio

| Fase | Alcance |
|------|---------|
| **v1** | Landing principal + módulos + planes + demo |
| **v2** | Casos de éxito + blog + recursos |
| **v3** | Landing por sector |
| **v4** | Centro de partners |
| **v5** | Centro de documentación pública |

---

## 5 · Landing principal · Secciones

### 5.1 · Hero

Debe comunicar el valor **inmediatamente**.

| Elemento | Copy oficial |
|----------|--------------|
| **Título** | Organiza, controla y haz crecer tu operación desde un solo lugar. |
| **Subtítulo** | Maintix es una plataforma SaaS modular para empresas que ya crecieron más allá de Excel. |
| **CTA primario** | Probar gratis 15 días |
| **CTA secundario** | Solicitar demostración |

→ [MKT-01 · Mensajes aprobados](01-identidad-mensajes-marca.md#8--mensajes-aprobados) · [MKT-02 · §3](02-elevator-pitch-guiones.md#3--elevator-pitch-30-segundos)

---

### 5.2 · Problema

**Título:** *Tu operación no debería depender de Excel.*

Mostrar situaciones reales:

- Hojas duplicadas
- WhatsApp como sistema operativo
- OT en papel
- Diferencias de inventario
- Información dispersa

**Mensaje:**

> Cuando cada área tiene una versión distinta de la información, las decisiones llegan tarde.

---

### 5.3 · La solución

**Título:** *Una sola plataforma para toda la operación.*

Explicar el concepto **EMP**. Mostrar módulos conectados:

```
Maintix
    ↓
Mantenimiento  →  Inventario  →  Compras  →  Ventas  →  Analytics
```

**Mensaje:**

> Un solo inicio de sesión. Una sola empresa. Una sola fuente de información.

→ [MKT-04 · Slide 4](04-presentacion-comercial.md#7--slide-4--una-plataforma)

---

### 5.4 · Beneficios

**No** listar funcionalidades. **Hablar** de resultados.

| Beneficio | Mensaje |
|-----------|---------|
| **Control** | Toda la información en un solo lugar |
| **Trazabilidad** | Historial completo de cada operación |
| **Productividad** | Menos tiempo buscando información |
| **Escalabilidad** | Nuevos módulos sin migrar |
| **Visibilidad** | Dashboards para decidir mejor |

→ [MKT-01 · Pilares](01-identidad-mensajes-marca.md#9--pilares-de-comunicación)

---

### 5.5 · Módulos

Mostrar **únicamente** los disponibles.

| Producción | Próximamente |
|------------|--------------|
| Maintenance | Purchasing |
| Inventory | CRM |
| | Finance |
| | Analytics |

**Regla:** siempre distinguir **producción** y **roadmap**.

→ [MCM-05 · Catálogo](/mcm/chapters/05-catalogo-modulos.md)

---

### 5.6 · Cómo funciona

Explicar el crecimiento:

```
Empieza  →  Digitaliza  →  Controla  →  Crece
```

**Mensaje:**

> *La transformación comienza con un módulo.*  
> *El crecimiento ocurre dentro de una sola plataforma.*

→ [MKT-04 · Slide 7](04-presentacion-comercial.md#10--slide-7--crecimiento-modular)

---

### 5.7 · Sectores

Mostrar tarjetas:

- Manufactura
- Comercio
- Agroindustria
- Talleres
- Distribución

Cada tarjeta debe llevar a una **landing específica** en v3 (roadmap).

→ [MCM-03 · Sectores](/mcm/chapters/03-sectores-mercados.md) · [MKT-02 · §6–10](02-elevator-pitch-guiones.md)

---

### 5.8 · Casos

Mostrar **máximo tres**. Cada caso responde:

```
Problema  →  Solución  →  Resultado
```

- **Nunca** inventar cifras
- Usar **únicamente** casos [MTX-CASE](../mtx-case/README.md)

Sugeridos para home (nivel D):

| Caso | Sector |
|------|--------|
| [MTX-CASE-001](../mtx-case/MTX-CASE-001-industria-colombia.md) | Manufactura |
| [MTX-CASE-002](../mtx-case/MTX-CASE-002-tornilleria-venezuela.md) | Comercio |
| [MTX-CASE-006](../mtx-case/MTX-CASE-006-comercio-multisede.md) | Operación mixta |

→ [MKT-03](03-casos-exito.md)

---

### 5.9 · Planes

Mostrar **únicamente** la evolución:

```
Start  →  Grow  →  Scale  →  Enterprise
```

**Botón:** Comparar planes

→ [MCM-04 · Planes SaaS](/mcm/chapters/04-planes-saas.md)

---

### 5.10 · Confianza

Elementos recomendados:

- Trial de 15 días
- Plataforma SaaS
- Multiempresa (tenant)
- Arquitectura modular
- API disponible ([MAG](/mag/))
- Documentación oficial ([Maintix Docs](/docs/))

---

### 5.11 · CTA final

| Elemento | Copy |
|----------|------|
| **Título** | Recupera el control de tu operación. |
| **CTA primario** | Comenzar prueba gratuita |
| **CTA secundario** | Agendar una demostración |

→ Slogan: [MKT-01 · §7](01-identidad-mensajes-marca.md#7--slogans-y-frases-de-marca)

---

## 6 · Navegación

### Menú principal

```
Producto · Soluciones · Planes · Recursos · Casos · Demo · Iniciar sesión
```

**Botón destacado (header):** Probar gratis

### Footer

Debe contener:

- Logo
- Slogan: **Toda la operación. Una sola plataforma.**
- Documentación · Privacidad · Contacto
- Redes sociales
- Copyright

---

## 7 · SEO

### Meta Title

```
Maintix | Plataforma SaaS para controlar la operación empresarial
```

### Meta Description

```
Maintix ayuda a empresas en crecimiento a organizar, controlar y hacer crecer su operación mediante una plataforma SaaS modular para mantenimiento e inventario.
```

### Palabras clave *(referencia · no stuffing)*

| | |
|---|---|
| software mantenimiento | software inventario |
| plataforma empresarial | gestión de activos |
| SaaS empresas | mantenimiento industrial |
| control de inventario | operación empresarial |

**Evitar en copy visible:** ERP · CMMS genérico · líder mundial · IA

→ [MKT-01 · §13 Palabras preferidas](01-identidad-mensajes-marca.md#13--palabras-preferidas)

---

## 8 · Conversiones

### CTAs principales

| CTA | Uso |
|-----|-----|
| **Probar gratis** | Hero · header · CTA final |
| **Solicitar demo** | Hero secundario · CTA final |

### CTAs secundarios

| CTA | Uso |
|-----|-----|
| Ver planes | Sección planes |
| Ver módulos | Sección producto |
| Casos de éxito | Sección casos |
| Contactar ventas | Footer · contacto |

### Métricas

| KPI | Objetivo |
|-----|----------|
| Conversión a trial | **Principal** |
| Solicitudes de demo | Alto |
| Tiempo en página | Alto |
| Rebote | Bajo |
| Conversión formulario | Alto |

---

## 9 · Adaptación por dispositivo

| Dispositivo | Prioridad |
|-------------|-----------|
| **Desktop** | Recorrido completo · todas las secciones |
| **Tablet** | Reducir bloques secundarios |
| **Mobile** | Hero · Beneficios · CTA · Sectores · Planes |

**Mobile — evitar:** bloques demasiado extensos · tablas comparativas · pantallas ilegibles.

→ [MUX · Responsive](/mux/responsive.md) · [MDL · Responsive](/mdl/responsive.md)

---

## 10 · Qué NO hacer

| ❌ Evitar | Por qué |
|----------|---------|
| Home llena de funcionalidades | Rompe flujo conversión |
| Pantallas pequeñas ilegibles | UX · credibilidad |
| Compararse con SAP u Oracle | MCM · ICP PYME |
| Prometer módulos no disponibles | MCM-05 · honestidad |
| Mostrar precios desactualizados | MCM-04 |
| Formularios largos | Fricción trial |
| Más de un objetivo por página | Diluye conversión |

→ [MKT-01 · §10](01-identidad-mensajes-marca.md#10--qué-no-comunicar)

---

## 11 · Integración documental

| Documento | Relación |
|-----------|----------|
| [MKT-01](01-identidad-mensajes-marca.md) | Mensajes y tono |
| [MKT-02](02-elevator-pitch-guiones.md) | Hero · Elevator Pitch |
| [MKT-03](03-casos-exito.md) | Casos MTX-CASE |
| [MKT-04](04-presentacion-comercial.md) | Narrativa alineada al deck |
| [MCM-01](/mcm/chapters/01-intro-filosofia-comercial.md) | Filosofía comercial |
| [MCM-03](/mcm/chapters/03-sectores-mercados.md) | Sectores |
| [MCM-04](/mcm/chapters/04-planes-saas.md) | Planes |
| [MCM-05](/mcm/chapters/05-catalogo-modulos.md) | Módulos |
| [MUX](/mux/) | UX y recorridos |
| [MDL](/mdl/) | Diseño visual |

---

## Filosofía del capítulo

La web de Maintix no debe intentar responder **todas** las preguntas.

Debe responder **una sola**:

> *«¿Vale la pena probar Maintix?»*

Si el visitante comprende el problema, identifica el valor y encuentra un camino claro para trial o demo, **la landing cumplió su objetivo**.

---

## Estado · Implementación

| Aspecto | Estado |
|---------|--------|
| Arquitectura web | ✅ Definida |
| Landing principal (copy) | ✅ Definida |
| Páginas de producto | 🟡 En desarrollo |
| Landings por sector | 📋 Roadmap v3 |
| Blog y recursos | 📋 Roadmap v2 |
| Centro de partners | 📋 Roadmap v4 |

---

## Exit Criteria · MKT-05

- [x] Arquitectura del sitio definida
- [x] Landing principal documentada (11 secciones)
- [x] CTAs oficiales establecidos
- [x] SEO básico documentado
- [x] Flujo de conversión definido
- [x] Integración con MCM · MUX · MDL
- [ ] Landings por sector *(roadmap v3)*

---

**Próximo capítulo:** [MKT-06 · Emails comerciales y secuencias](06-emails-secuencias.md) *(Sprint 12.6)*

---

*MKT-05 · Sales Enablement & Marketing Assets · Sprint 12 · 2026*
