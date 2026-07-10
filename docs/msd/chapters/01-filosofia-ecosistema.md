# MSD-01-PHIL · Filosofía del ecosistema

**Código:** MSD-01-PHIL · Sprint 9.1 · **Entregado**

> MAG define el contrato. MSD entrega la experiencia.

**Toda la operación. Una sola plataforma.**

---

## Objetivo del capítulo

Establecer la **filosofía del ecosistema para desarrolladores** de Maintix: cómo el Sprint 9 transforma la documentación de la API en una experiencia práctica para integradores, partners y equipos de ingeniería.

---

## 1 · De contrato a experiencia

Sprint 8 entregó **MAG v1.0** — un estándar de API de nivel empresarial:

- contrato REST `/api/v1`
- JWT multi-tenant
- errores estructurados
- webhooks
- ejemplos y buenas prácticas

Sprint 9 responde la pregunta siguiente:

> *«Leí la documentación. ¿Cómo integro en producción esta semana?»*

**MSD (Maintix SDK & Developer Portal)** cierra esa brecha.

| Fase | Producto | Rol |
|------|----------|-----|
| Sprint 8 | **MAG** | Especificación del contrato |
| Sprint 9 | **MSD** | Herramientas, portal y clientes oficiales |

---

## 2 · Filosofía

Un ecosistema de desarrolladores excelente debe ser:

- **Accesible** — Quick Start en menos de 10 minutos
- **Consistente** — mismo contrato en portal, SDK, CLI y colecciones
- **Generado** — OpenAPI como fuente única de verdad
- **Multi-tenant aware** — ejemplos y sandbox con contexto de empresa
- **Profesional** — comparable a Stripe, GitHub, Microsoft Graph o Notion

La documentación no termina en la especificación. Debe incluir **herramientas que funcionen**.

---

## 3 · Componentes del ecosistema MSD

```
Maintix Developer Experience
│
├── Developer Portal      developer.maintix.app
├── OpenAPI 3.1           openapi.v1.yaml
├── SDK oficiales         Python · JavaScript · PHP
├── CLI                   maintix-cli
├── Sandbox               tenant demo · datos ficticios
├── API Explorer          Try it · desde OpenAPI
├── Quick Start           guías paso a paso
└── Colecciones           Postman · Insomnia
```

Cada componente consume el **mismo contrato MAG**.

---

## 4 · Relación con MAG

| MAG | MSD |
|-----|-----|
| `/api/v1/auth/login` | `client.auth.login()` |
| MAG-04 recursos | `client.maintenance.assets` |
| MAG-06 errores | SDK lanza `MaintixError(code=...)` |
| MAG-09 ejemplos | Quick Start ejecutable |
| MAG-07 OpenAPI | `openapi.v1.yaml` generado |

**Regla:** MSD nunca redefine el contrato. Solo lo **implementa**.

→ [MAG v1.0](/mag/)

---

## 5 · Audiencias

| Audiencia | Necesidad | Entrega MSD |
|-----------|-----------|-------------|
| Integrador interno | Automatizar procesos | SDK + Quick Start |
| Partner SaaS | Conectar ERP/CRM | Portal + colecciones |
| Desarrollador freelance | Prototipo rápido | Sandbox + Explorer |
| Equipo Maintix | Validar contrato | OpenAPI + CLI |

**Developer Docs (suite 09)** sigue siendo para quien **contribuye al repositorio** — no confundir con MSD.

---

## 6 · Principios de diseño

| # | Principio |
|---|-----------|
| 1 | OpenAPI primero — no escribir clientes a mano si pueden generarse |
| 2 | SDK idiomático por lenguaje — Python `snake_case`, JS `camelCase` en superficie |
| 3 | Ejemplos copiables — funcionan sin modificación significativa |
| 4 | Sandbox aislado — nunca datos de producción |
| 5 | Versionado alineado a MAG — MSD v1.0 sobre MAG v1.0 |
| 6 | Publicación reproducible — CI publica paquetes desde tags |

---

## 7 · Entregables Sprint 9

| Entrega | Descripción | Capítulo |
|---------|-------------|----------|
| Portal | developer.maintix.app | [MSD-02](02-developer-portal.md) |
| OpenAPI 3.1 | `openapi.v1.yaml` | [MSD-03](03-openapi.md) |
| SDK | Python · JS · PHP | [MSD-04](04-sdk-oficiales.md) |
| CLI | `maintix-cli` | [MSD-05](05-cli.md) |
| Sandbox | API Explorer | [MSD-06](06-sandbox-explorer.md) |
| Quick Start | Guías | [MSD-07](07-quick-start.md) |
| Colecciones | Postman · Insomnia | [MSD-08](08-colecciones.md) |
| Publicación | Primer paquete SDK | [MSD-09](09-publicacion.md) |

---

## 8 · Entorno local

| Recurso | URL local |
|---------|-----------|
| MSD (este manual) | http://127.0.0.1:5000/msd/ |
| MAG (contrato) | http://127.0.0.1:5000/mag/ |
| API | http://127.0.0.1:5000/api/v1 |
| Docs suite | http://127.0.0.1:5000/docs/ |

```powershell
python run.py
```

---

## Exit Criteria · MSD v1.0

MSD v1.0 se considerará completo cuando:

- [ ] Existe portal accesible (local o `developer.maintix.app`)
- [ ] OpenAPI 3.1 publicado y sincronizado con MAG-04
- [ ] Al menos un SDK oficial publicado (Python recomendado)
- [ ] Quick Start ejecutable de principio a fin
- [ ] Colección Postman generada desde OpenAPI
- [ ] Sandbox con tenant demo operativo

---

## Estado

| Aspecto | Valor |
|---------|-------|
| **Dependencia** | MAG v1.0 ✅ |
| **Implementación** | 🟡 MSD-01–02 entregados · MSD-03 siguiente |
| **Versión MSD** | v0.2.0 |
| **Siguiente capítulo** | [MSD-03 · OpenAPI 3.1](03-openapi.md) |

---

→ [MSD-02-PORT · Developer Portal](02-developer-portal.md) · [MSD-03 · OpenAPI](03-openapi.md)
