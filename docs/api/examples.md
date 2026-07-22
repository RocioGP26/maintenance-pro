# Ejemplos · API pública y Webhooks v1

Sustituye `BASE`, `API_KEY` y `WH_SECRET` por valores reales.

## Identidad

```bash
curl -sS "$BASE/api/v1/me" \
  -H "Authorization: Bearer $API_KEY"
```

## Listar activos incrementales

```bash
curl -sS "$BASE/api/v1/maintenance/assets?page=1&page_size=50&updated_since=2026-01-01T00:00:00Z" \
  -H "Authorization: Bearer $API_KEY"
```

## Crear incidencia (idempotente)

```bash
curl -sS -X POST "$BASE/api/v1/maintenance/incidents" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: incident-demo-001" \
  -d '{
    "title": "Vibración anormal",
    "description": "Detectada por sensor externo",
    "responsible_area": "Mantenimiento",
    "reporter_area": "Producción",
    "type": "mecanica",
    "priority": "alta",
    "asset_id": 15
  }'
```

## Registrar lectura de medidor

```bash
curl -sS -X POST "$BASE/api/v1/maintenance/meters/3/readings" \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -H "Idempotency-Key: reading-demo-001" \
  -d '{
    "value": "125.50",
    "measured_at": "2026-07-22T14:30:00Z",
    "notes": "Lectura desde integración"
  }'
```

## Verificar firma de webhook (Python)

```python
import hashlib
import hmac
import time

def verify(secret: str, timestamp: str, body: bytes, signature: str, max_skew=300) -> bool:
    ts = int(timestamp)
    if abs(int(time.time()) - ts) > max_skew:
        return False
    expected = "v1=" + hmac.new(
        secret.encode(), f"{ts}.".encode() + body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(expected, signature.strip())
```

## Receptor mínimo (Flask)

```python
from flask import Flask, request, abort
app = Flask(__name__)
SEEN = set()

@app.post("/hooks/roustix")
def hook():
    event_id = request.headers.get("X-Roustix-Event-Id")
    if event_id in SEEN:
        return {"ok": True, "deduped": True}
    if not verify(
        WH_SECRET,
        request.headers.get("X-Roustix-Timestamp"),
        request.get_data(),
        request.headers.get("X-Roustix-Signature", ""),
    ):
        abort(401)
    SEEN.add(event_id)
    payload = request.get_json(force=True)
    # procesar payload["type"] / payload["data"]["object"]
    return {"ok": True}
```

## Admin · stats de entregas (sesión)

```bash
curl -sS "$BASE/api/v1/admin/webhook-stats" \
  -H "Cookie: session=…"
```
