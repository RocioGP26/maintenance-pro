# SDK · Roustix

**Suite docs 08** — implementación de clientes oficiales (parte de **MSD**).

→ **[MSD-04 · SDK oficiales](/msd/chapters/04-sdk-oficiales.md)** · **[Developer Portal](/msd/)**

## Contrato

Todos los SDK oficiales consumen el mismo contrato MAG:

- Base: `/api/v1`
- Generación desde [OpenAPI](/api/v1/openapi.json) · [`openapi.v1.yaml`](../api/openapi.v1.yaml)
- Estructura alineada a [MAG-04](../mag/chapters/04-recursos.md)

## Lenguajes oficiales (MSD v1.0)

| Lenguaje | Paquete | Instalación | Estado |
|----------|---------|-------------|--------|
| Python | `roustix` | `pip install roustix` | 📋 |
| JavaScript / TS | `@roustix/sdk` | `npm install @roustix/sdk` | 📋 |
| PHP | `roustix/sdk` | `composer require roustix/sdk` | 📋 |

## Inicialización

```python
from roustix import RoustixClient

client = RoustixClient(
    base_url="https://api.roustix.app/api/v1",
    token="...",
)

assets = client.maintenance.assets.list()
```

## Estructura del cliente

```
client.auth · client.me · client.maintenance · client.inventory
client.purchasing · client.sales · client.crm · client.admin
```

## Repositorios (planificados)

- `github.com/roustix/sdk-python`
- `github.com/roustix/sdk-js`
- `github.com/roustix/sdk-php`

| Relacionado | Ruta |
|-------------|------|
| MSD (08) | [../msd/README.md](../msd/README.md) · [/msd/](/msd/) |
| MAG (07) | [../mag/README.md](../mag/README.md) |
| OpenAPI | [MSD-03](../msd/chapters/03-openapi.md) |

→ [Índice maestro](../README.md) · [/docs/](http://127.0.0.1:5000/docs/)
