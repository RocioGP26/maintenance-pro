# Rebranding · Roustix

**Fecha:** 2026-07-21  
**Estado:** aplicado en fuentes · pendiente validación de dominio y canales

## Identidad oficial

- Producto: **Roustix**
- Tagline: **Toda la operación. Una sola plataforma.**
- Logo de aplicación: `static/img/roustix-logo.svg`
- Favicon de aplicación: `static/img/roustix-favicon.svg`
- Contacto configurado por defecto: `contacto@roustix.com`
- API documentada: `api.roustix.app`
- Portal documentado: `developer.roustix.app`

Los dominios y buzones deben validarse antes de publicar producción. Hasta entonces,
el correo SMTP real continúa dependiendo de la configuración del entorno.

## Alcance aplicado

- Interfaz web, landing, administración y onboarding.
- Correos transaccionales.
- Metadatos de versión y comandos CLI.
- Exportaciones PDF/Excel y metadata MRL.
- OpenAPI, colecciones y documentación para integradores.
- Documentación funcional, comercial, UX y arquitectura.
- Workflow de versiones y nombres de releases.

## Compatibilidad preservada

No se cambian automáticamente los siguientes identificadores:

- Códigos documentales `MBB`, `MDL`, `MUX`, `MPA`, `MAG`, `MSD`, `MDO`, `MRG` y `MRL`.
- Prefijos documentales históricos `MTX-*`.
- Patrón heredado `mantis_*.db` del script de consolidación de tenants.
- Nombre interno del servicio existente en `render.yaml`.
- Clave local heredada del estado del sidebar.

Estos elementos no son marca visible. Cambiarlos requiere una migración separada con
aliases, redirecciones y pruebas de compatibilidad.

## Verificación requerida antes de producción

1. Confirmar propiedad de `roustix.com` y `roustix.app` o sustituirlos por los dominios reales.
2. Crear y autenticar el buzón remitente de Roustix en el proveedor SMTP.
3. Configurar DNS: SPF, DKIM y DMARC.
4. Verificar la reproducción del logo y favicon oficiales en los navegadores soportados.
5. Regenerar PDFs o materiales binarios publicados con la marca anterior.
