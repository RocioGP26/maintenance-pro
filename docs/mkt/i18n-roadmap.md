# i18n · Roadmap de internacionalización Roustix

## Corto plazo · antes del piloto ✅

**Protección de marcas** frente a traducción automática del navegador (Chrome/Google Translate):

| Mecanismo | Uso |
|-----------|-----|
| `translate="no"` + `class="notranslate"` | Nombres comerciales y módulos en HTML |
| Filtro Jinja `\|notranslate` | Un término: `{{ app_name\|notranslate }}` |
| Filtro Jinja `\|protect_brands` | Párrafos con marcas embebidas |
| Módulo | `app/brand_protect.py` |
| Macro | `templates/landing/_brand.html` |

Términos protegidos: Roustix, Roustix Maintenance/Inventory/Docs, Start, Business, Enterprise, **Planes** (evita «Aviones»), CRM, Purchasing, Analytics, códigos de manuales (MAG, MSD, MCM…).

**Problema que resuelve:** traducciones erróneas tipo *Start* → «Aviones» / *Business* → «Negocio» en contextos de marca.

---

## Mediano plazo · antes de expansión internacional 📋

Implementar **i18n propio** (no depender del traductor del navegador):

| Entrega | Descripción |
|---------|-------------|
| Catálogo de idiomas | `es` (default) · `en` primero |
| Archivos de idioma | JSON o gettext (`.po`) por dominio: landing, app, emails |
| Selector de idioma | Preferencia de usuario / tenant |
| Convenciones | Claves estables · sin hardcode de copy en plantillas nuevas |
| QA | Checklist de marcas que **nunca** se traducen (whitelist = `BRAND_TERMS`) |

**Beneficio:** control total de cada frase, tono B2B coherente en español e inglés, experiencia profesional al salir del mercado hispanohablante.

**No hacer:** activar traducción automática global (`<meta name="google" content="notranslate">` en toda la página) — bloquearía la UX legítima de lectores que sí quieren traducir el contenido en español.

---

*MKT · alineado a recomendación piloto · 2026-07-29*
