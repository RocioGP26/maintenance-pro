# MAG · Roustix API Guide

**Código:** MAG · Suite docs **07**  
**Versión:** v1.0.12  
**Acceso:** 🌐 **100 % público** — contrato de integración para CTOs, TI e integradores  
**Frase:** Toda la operación. Una sola plataforma.

> La forma **oficial** de interactuar con Roustix desde el exterior — no solo una lista de endpoints.

## Ver documentación

```powershell
python run.py
```

→ http://127.0.0.1:5000/mag/ · portal público  
→ http://127.0.0.1:5000/api/v1/openapi.yaml · especificación  
→ http://127.0.0.1:5000/msd/ · SDK, sandbox y colecciones

## Qué es público vs qué requiere login

| Público (sin login) | Protegido |
|---------------------|-----------|
| Índice `/mag/` · guía HTML `/mag/guide/*` · OpenAPI | Fuente `.md` en `/mag/chapters/` |
| Portal MSD (herramientas) | API keys / credenciales de integración |
| | Arquitectura interna (**MPA**) · llamadas reales |

Ejemplo: el flujo JWT y los códigos HTTP viven en [`/mag/guide/autenticacion-jwt`](/mag/guide/autenticacion-jwt). El archivo `chapters/02-autenticacion-jwt.md` es solo para el equipo.

## Objetivo

Documentar cómo integradores, partners y desarrolladores se conectan a Roustix: filosofía, JWT, multi-tenant, recursos, errores, versionado, webhooks y buenas prácticas.

**MPA** (privado) describe la arquitectura interna; **MAG** (público) describe el contrato externo.

## Capítulos

| # | Código | Título |
|---|--------|--------|
| 01 | MAG-01-PHIL | [Filosofía de la API](chapters/01-filosofia-api.md) |
| 02 | MAG-02-AUTH | [Autenticación JWT](chapters/02-autenticacion-jwt.md) |
| 03 | MAG-03-TNT | [Multi-tenant](chapters/03-multi-tenant.md) |
| 04 | MAG-04-RES | [Recursos REST](chapters/04-recursos.md) |
| 05 | MAG-05-NAM | [Convenciones de nombres](chapters/05-convenciones-nombres.md) |
| 06 | MAG-06-ERR | [Manejo de errores](chapters/06-manejo-errores.md) |
| 07 | MAG-07-VER | [Versionado](chapters/07-versionado.md) |
| 08 | MAG-08-HOOK | [Webhooks](chapters/08-webhooks.md) |
| 09 | MAG-09-EX | [Ejemplos y SDK](chapters/09-ejemplos.md) |
| 10 | MAG-10-LIM | [Límites y buenas prácticas](chapters/10-limites-buenas-practicas.md) |

## Relacionado

| Doc | Rol |
|-----|-----|
| [MPA](/mpa/) | Arquitectura · MPA-06 integraciones |
| [MRL](/mrl/) | PDF · exportaciones |
| [API reference](../api/README.md) | OpenAPI (planificado) |
| [SDK](../sdk/README.md) | Clientes oficiales · [MSD](/msd/) Sprint 9 |

## Roustix Documentation Suite

| Meta | Enlace |
|------|--------|
| Índice | [/docs/](http://127.0.0.1:5000/docs/) |
| Versiones | [VERSIONS.md](../VERSIONS.md) |
| Referencias cruzadas | [CROSS-REFERENCES.md](../CROSS-REFERENCES.md) |
