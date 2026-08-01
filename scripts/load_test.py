"""Prueba de carga de solo lectura para el gate productivo de Roustix.

El login web y el login API se ejecutan una sola vez para no convertir la
prueba en un bypass del rate limit. Las peticiones concurrentes posteriores son
exclusivamente GET sobre dashboard, incidencias, OT y API pública.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import http.cookiejar
import json
import math
import os
import random
import re
import statistics
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urlparse


LOCAL_HOSTS = {"127.0.0.1", "localhost", "::1"}
WEB_PATHS = ("/dashboard", "/incidencias", "/ordenes")
API_PATHS = (
    "/api/v1/me",
    "/api/v1/maintenance/assets?page=1&page_size=25",
    "/api/v1/maintenance/work-orders?page=1&page_size=25",
)


@dataclass(frozen=True)
class Sample:
    path: str
    status: int
    elapsed_ms: float
    ok: bool
    error: str = ""


def percentile(values: list[float], value: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    rank = max(0, math.ceil((value / 100) * len(ordered)) - 1)
    return round(ordered[rank], 2)


def traffic_light(*, p95_ms: float, error_rate: float) -> str:
    if error_rate > 3 or p95_ms > 5000:
        return "red"
    if error_rate >= 1 or p95_ms > 2500:
        return "yellow"
    return "green"


def summarize(samples: list[Sample]) -> dict:
    if not samples:
        return {
            "requests": 0,
            "failures": 0,
            "error_rate_pct": 0.0,
            "latency_ms": {"mean": 0.0, "p50": 0.0, "p95": 0.0, "p99": 0.0, "max": 0.0},
            "verdict": "no_data",
        }
    elapsed = [item.elapsed_ms for item in samples]
    failures = sum(not item.ok for item in samples)
    error_rate = round((failures / len(samples) * 100), 2) if samples else 100.0
    result = {
        "requests": len(samples),
        "failures": failures,
        "error_rate_pct": error_rate,
        "latency_ms": {
            "mean": round(statistics.fmean(elapsed), 2) if elapsed else 0.0,
            "p50": percentile(elapsed, 50),
            "p95": percentile(elapsed, 95),
            "p99": percentile(elapsed, 99),
            "max": round(max(elapsed), 2) if elapsed else 0.0,
        },
    }
    result["verdict"] = traffic_light(
        p95_ms=result["latency_ms"]["p95"], error_rate=error_rate
    )
    return result


def _request(
    base_url: str,
    path: str,
    *,
    method: str = "GET",
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
    opener=None,
    timeout: float = 20,
) -> tuple[int, bytes, str]:
    request = urllib.request.Request(
        urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/")),
        data=body,
        headers={"User-Agent": "Roustix-Load-Gate/1.0", **(headers or {})},
        method=method,
    )
    handler = opener.open if opener is not None else urllib.request.urlopen
    try:
        with handler(request, timeout=timeout) as response:
            return response.status, response.read(), response.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, exc.read(), exc.geturl()


def _csrf_token(body: bytes) -> str:
    match = re.search(
        rb'name=["\']csrf_token["\'][^>]*value=["\']([^"\']+)', body, re.I
    )
    if match is None:
        raise RuntimeError("No se encontró el token CSRF del login.")
    return match.group(1).decode("utf-8")


def web_session_cookie(base_url: str, username: str, password: str, slug: str) -> str:
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    status, page, _ = _request(base_url, "/login", opener=opener)
    if status != 200:
        raise RuntimeError(f"GET /login devolvió HTTP {status}.")
    form = urllib.parse.urlencode(
        {
            "csrf_token": _csrf_token(page),
            "username": username,
            "password": password,
            "empresa_slug": slug,
        }
    ).encode()
    status, _, final_url = _request(
        base_url,
        "/login",
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            # Flask-WTF aplica validación estricta del referente en HTTPS.
            "Origin": base_url.rstrip("/"),
            "Referer": urllib.parse.urljoin(base_url.rstrip("/") + "/", "login"),
        },
        body=form,
        opener=opener,
    )
    final_path = urlparse(final_url).path
    if status != 200:
        raise RuntimeError(f"El login web devolvió HTTP {status}.")
    if final_path == "/login":
        raise RuntimeError(
            "El login web regresó al formulario de acceso; "
            "verifica usuario, contraseña y empresa."
        )
    return "; ".join(f"{cookie.name}={cookie.value}" for cookie in jar)


def api_token(base_url: str, username: str, password: str, slug: str) -> str:
    payload = json.dumps(
        {"username": username, "password": password, "empresa_slug": slug}
    ).encode()
    status, body, _ = _request(
        base_url,
        "/api/v1/auth/login",
        method="POST",
        headers={"Content-Type": "application/json"},
        body=payload,
    )
    if status != 200:
        raise RuntimeError(f"El login API devolvió HTTP {status}.")
    token = json.loads(body).get("token")
    if not token:
        raise RuntimeError("El login API no devolvió token.")
    return token


def _sample(base_url: str, path: str, headers: dict[str, str], timeout: float) -> Sample:
    started = time.perf_counter()
    try:
        status, _, _ = _request(base_url, path, headers=headers, timeout=timeout)
        elapsed = (time.perf_counter() - started) * 1000
        return Sample(path, status, round(elapsed, 2), 200 <= status < 400)
    except Exception as exc:  # El informe conserva sólo el tipo, no credenciales.
        elapsed = (time.perf_counter() - started) * 1000
        return Sample(path, 0, round(elapsed, 2), False, type(exc).__name__)


def run_stage(
    base_url: str,
    *,
    users: int,
    duration: int,
    scenarios: list[tuple[str, dict[str, str]]],
    timeout: float,
) -> list[Sample]:
    # La línea base garantiza representación de cada endpoint incluso en
    # escalones cortos; el periodo concurrente comienza después de medirla.
    samples: list[Sample] = [
        _sample(base_url, path, headers, timeout) for path, headers in scenarios
    ]
    stop_at = time.monotonic() + duration
    lock = threading.Lock()

    def virtual_user(seed: int) -> None:
        rng = random.Random(seed)
        local: list[Sample] = []
        while time.monotonic() < stop_at:
            path, headers = rng.choice(scenarios)
            local.append(_sample(base_url, path, headers, timeout))
            time.sleep(rng.uniform(0.15, 0.45))
        with lock:
            samples.extend(local)

    with concurrent.futures.ThreadPoolExecutor(max_workers=users) as pool:
        futures = [pool.submit(virtual_user, index) for index in range(users)]
        for future in futures:
            future.result()
    return samples


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:5000")
    parser.add_argument("--users", type=int, default=5)
    parser.add_argument("--duration", type=int, default=30)
    parser.add_argument("--timeout", type=float, default=20)
    parser.add_argument("--allow-production", action="store_true")
    parser.add_argument("--public-only", action="store_true")
    parser.add_argument("--env-file", type=Path)
    parser.add_argument("--output", type=Path)
    return parser


def load_env_file(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"No existe el archivo local de credenciales: {path}")
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        if key in {
            "LOAD_TEST_USERNAME",
            "LOAD_TEST_PASSWORD",
            "LOAD_TEST_EMPRESA_SLUG",
        }:
            os.environ.setdefault(key, value.strip().strip('"').strip("'"))


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    host = (urlparse(args.base_url).hostname or "").lower()
    if host not in LOCAL_HOSTS and not args.allow_production:
        raise SystemExit("Destino remoto bloqueado: añade --allow-production conscientemente.")
    if not 1 <= args.users <= 50:
        raise SystemExit("--users debe estar entre 1 y 50.")
    if not 5 <= args.duration <= 300:
        raise SystemExit("--duration debe estar entre 5 y 300 segundos.")

    scenarios: list[tuple[str, dict[str, str]]] = [
        ("/health/live", {}),
        ("/health/ready", {}),
    ]
    if not args.public_only:
        if args.env_file:
            load_env_file(args.env_file)
        username = os.environ.get("LOAD_TEST_USERNAME", "").strip()
        password = os.environ.get("LOAD_TEST_PASSWORD", "")
        slug = os.environ.get("LOAD_TEST_EMPRESA_SLUG", "").strip()
        if not username or not password or not slug:
            raise SystemExit(
                "Define LOAD_TEST_USERNAME, LOAD_TEST_PASSWORD y LOAD_TEST_EMPRESA_SLUG."
            )
        try:
            # Validar primero la API evita consumir también el rate limit web
            # cuando las credenciales o el tenant son incorrectos.
            token = api_token(args.base_url, username, password, slug)
            cookie = web_session_cookie(args.base_url, username, password, slug)
        except RuntimeError as exc:
            print(
                json.dumps(
                    {
                        "phase": "authentication",
                        "ok": False,
                        "error": str(exc),
                    },
                    ensure_ascii=False,
                )
            )
            return 2
        scenarios.extend((path, {"Cookie": cookie}) for path in WEB_PATHS)
        scenarios.extend(
            (path, {"Authorization": f"Bearer {token}"}) for path in API_PATHS
        )

    samples = run_stage(
        args.base_url,
        users=args.users,
        duration=args.duration,
        scenarios=scenarios,
        timeout=args.timeout,
    )
    report = {
        "base_url": args.base_url,
        "users": args.users,
        "duration_seconds": args.duration,
        "generated_at_epoch": int(time.time()),
        "summary": summarize(samples),
        "by_path": {
            path: summarize([item for item in samples if item.path == path])
            for path, _ in scenarios
        },
        "failures": [asdict(item) for item in samples if not item.ok][:50],
    }
    rendered = json.dumps(report, indent=2, ensure_ascii=False)
    print(rendered)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    return 1 if report["summary"]["verdict"] == "red" else 0


if __name__ == "__main__":
    raise SystemExit(main())
