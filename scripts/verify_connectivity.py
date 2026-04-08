#!/usr/bin/env python3
"""
Comprueba Ollama (HTTP) y MySQL usando variables del .env (Fase 0).

Uso (desde la raíz del workspace JIS_REPORTES_2.0):
  python scripts/verify_connectivity.py
  python scripts/verify_connectivity.py --check-agent   # además GET /info (servicio ya en marcha)

Carga .env raíz y luego el del toolkit (este último gana si hay claves duplicadas).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_dotenv_file(path: Path, *, override: bool = False) -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k, v = k.strip(), v.strip().strip('"').strip("'")
        if k and (override or k not in os.environ):
            os.environ[k] = v


def check_ollama(base: str) -> tuple[bool, str]:
    base = base.rstrip("/")
    url = f"{base}/api/tags"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=15) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        data = json.loads(body)
        models = [m.get("name", "?") for m in data.get("models", [])]
        return True, f"OK — modelos en servidor: {', '.join(models[:8])}{'…' if len(models) > 8 else ''}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"Red/URL: {e.reason}"
    except Exception as e:
        return False, str(e)


def check_mysql() -> tuple[bool, str]:
    try:
        import mysql.connector
    except ImportError:
        return False, "mysql-connector-python no instalado (omitir o: pip install mysql-connector-python)"

    user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER")
    password = os.getenv("DB_PASSWORD") or os.getenv("DB_READONLY_PASSWORD")
    host = os.getenv("DB_HOST")
    database = os.getenv("DB_DATABASE")
    port = int(os.getenv("DB_PORT", "3306"))
    if not all([user, password, host, database]):
        return False, "Faltan DB_HOST / DB_DATABASE / usuario o password"

    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=port,
            connection_timeout=10,
        )
        conn.close()
        return True, "OK — conexión MySQL"
    except Exception as e:
        return False, str(e)


def check_agent_info() -> tuple[bool, str]:
    host = os.getenv("HOST", "127.0.0.1").strip() or "127.0.0.1"
    port = os.getenv("PORT", "8080").strip() or "8080"
    if host == "0.0.0.0":
        host = "127.0.0.1"
    url = f"http://{host}:{port}/info"
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read().decode("utf-8", errors="replace")
        data = json.loads(body)
        agent = data.get("default_agent", "?")
        return True, f"OK — /info default_agent={agent!r}"
    except urllib.error.HTTPError as e:
        return False, f"HTTP {e.code}: {e.reason}"
    except urllib.error.URLError as e:
        return False, f"No responde ({url}): {e.reason}"
    except Exception as e:
        return False, str(e)


def main() -> int:
    p = argparse.ArgumentParser(
        description="Fase 0: verificar Ollama + MySQL (y opcionalmente API del agente).",
    )
    p.add_argument(
        "--env",
        type=Path,
        default=ROOT / "framework" / "agent-service-toolkit" / ".env",
        help="Ruta al .env del agente (default: toolkit); sobrescribe claves del .env raíz",
    )
    p.add_argument(
        "--check-agent",
        action="store_true",
        help="Comprueba GET /info con HOST y PORT del .env (arranca antes el servicio con run_service.py)",
    )
    args = p.parse_args()

    load_dotenv_file(ROOT / ".env")
    load_dotenv_file(args.env, override=True)

    print(f"Usando .env: {args.env.resolve() if args.env.is_file() else '(no encontrado)'}")

    obase = os.getenv("OLLAMA_BASE_URL", "").strip()
    if not obase:
        print("OLLAMA_BASE_URL no definido.")
        return 1
    ok, msg = check_ollama(obase)
    print(f"Ollama ({obase}): [{'OK' if ok else 'FAIL'}] {msg}")

    ok_db, msg_db = check_mysql()
    print(f"MySQL: [{'OK' if ok_db else 'FAIL'}] {msg_db}")

    all_ok = ok and ok_db

    if args.check_agent:
        ok_api, msg_api = check_agent_info()
        print(f"Agente API /info: [{'OK' if ok_api else 'FAIL'}] {msg_api}")
        all_ok = all_ok and ok_api

    if all_ok:
        print("\nFase 0: conectividad lista (Ollama + MySQL" + (" + API" if args.check_agent else "") + ").")
    else:
        print("\nFase 0: revisa los FAIL arriba antes de seguir.")

    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
