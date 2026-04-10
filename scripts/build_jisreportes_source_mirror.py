#!/usr/bin/env python3
"""
Clona (o actualiza) jisreportes_back y jisreportes_front desde GitHub y genera un único .md en docs/
(**JISREPORTES_COM_FUENTE_OFICIAL.md** está en `.gitignore`: solo en tu equipo, no en GitHub) con:

1. Metadatos (commits, URLs).
2. Mapa automático: routers FastAPI → rutas HTTP.
3. Mapa automático: páginas Streamlit → llamadas api_request (endpoints).
4. Cruce sugerido dashboards menú → página → APIs.
5. Anexo: código fuente completo de todos los .py de ambos repos (fuente de verdad local).

Uso (desde la raíz del repo JIS_REPORTES_2.0):

    python scripts/build_jisreportes_source_mirror.py

Requisitos: git en PATH, red para clone/pull.
"""

from __future__ import annotations

import datetime as dt
import os
import re
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

# Raíz del monorepo JIS_REPORTES_2.0
ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = ROOT / "artifacts" / "jisreportes_upstream"
BACK_DIR = ARTIFACTS / "jisreportes_back"
FRONT_DIR = ARTIFACTS / "jisreportes_front"
BACK_REMOTE = "https://github.com/rodrigocabezasz/jisreportes_back.git"
FRONT_REMOTE = "https://github.com/rodrigocabezasz/jisreportes_front.git"
OUT_PATH = ROOT / "docs" / "JISREPORTES_COM_FUENTE_OFICIAL.md"

SKIP_DIR_NAMES = {".git", "__pycache__", "node_modules", ".venv", "venv"}


def run(cmd: list[str], cwd: Path | None = None) -> str:
    p = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if p.returncode != 0:
        raise RuntimeError(f"Command failed: {' '.join(cmd)}\n{p.stderr}")
    return p.stdout.strip()


def ensure_shallow_clone(path: Path, remote: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if (path / ".git").is_dir():
        run(["git", "-C", str(path), "fetch", "--depth", "1", "origin"])
        run(["git", "-C", str(path), "reset", "--hard", "origin/main"])
    else:
        run(
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--branch",
                "main",
                remote,
                str(path),
            ]
        )


def git_head(path: Path) -> str:
    return run(["git", "-C", str(path), "rev-parse", "HEAD"])


def iter_py_files(repo_root: Path) -> list[Path]:
    out: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIR_NAMES]
        for fn in filenames:
            if fn.endswith(".py"):
                out.append(Path(dirpath) / fn)
    return sorted(out)


def extract_router_prefix(text: str) -> str:
    m = re.search(r'APIRouter\s*\([^)]*?prefix\s*=\s*["\']([^"\']+)["\']', text, re.DOTALL)
    return m.group(1).rstrip("/") if m else ""


def extract_fastapi_routes(file_text: str, default_prefix: str = "") -> list[tuple[str, str, str]]:
    """
    Returns list of (method, full_path, function_name_or_?)
    """
    prefix = extract_router_prefix(file_text) or default_prefix
    routes: list[tuple[str, str, str]] = []
    for m in re.finditer(
        r'@(?:router|app)\.(get|post|put|patch|delete)\s*\(\s*["\']([^"\']*)["\']',
        file_text,
        re.IGNORECASE,
    ):
        method, sub = m.group(1).upper(), m.group(2)
        sub = sub or "/"
        if not sub.startswith("/"):
            sub = "/" + sub
        if prefix:
            full = prefix.rstrip("/") + sub if sub != "/" else prefix or "/"
        else:
            full = sub
        routes.append((method, full, ""))
    return routes


def scan_backend_routers(repo_root: Path, backend_app: Path) -> list[tuple[str, str, str, str]]:
    """(rel_path, method, path, router_file)"""
    routers_dir = backend_app / "routers"
    rows: list[tuple[str, str, str, str]] = []
    if not routers_dir.is_dir():
        return rows
    for fp in sorted(routers_dir.glob("*.py")):
        if fp.name.startswith("_"):
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        rel = fp.relative_to(repo_root).as_posix()
        for method, path, _ in extract_fastapi_routes(text):
            rows.append((rel, method, path, fp.name))
    main_py = backend_app / "main.py"
    if main_py.is_file():
        text = main_py.read_text(encoding="utf-8", errors="replace")
        rel = main_py.relative_to(repo_root).as_posix()
        for method, path, _ in extract_fastapi_routes(text, default_prefix=""):
            rows.append((rel, method, path, "main.py"))
    rows.sort(key=lambda x: (x[2], x[1], x[0]))
    return rows


def extract_api_request_paths(text: str) -> list[tuple[str, str]]:
    """(method, path) best-effort."""
    found: list[tuple[str, str]] = []
    for m in re.finditer(
        r'api_request\s*\(\s*["\'](GET|POST|PUT|PATCH|DELETE)["\']\s*,\s*f?["\']([^"\']+)["\']',
        text,
        re.IGNORECASE | re.DOTALL,
    ):
        found.append((m.group(1).upper(), m.group(2)))
    return found


def scan_front_pages(front_root: Path) -> dict[str, list[tuple[str, str]]]:
    out: dict[str, list[tuple[str, str]]] = {}
    pages = front_root / "pages"
    if not pages.is_dir():
        return out
    for fp in sorted(pages.glob("*.py")):
        text = fp.read_text(encoding="utf-8", errors="replace")
        eps = extract_api_request_paths(text)
        if eps:
            out[f"pages/{fp.name}"] = sorted(set(eps))
    for extra in ["app.py", "api_client.py", "sales_common.py", "menu.py", "auth.py", "session_manager.py"]:
        p = front_root / extra
        if p.is_file():
            text = p.read_text(encoding="utf-8", errors="replace")
            eps = extract_api_request_paths(text)
            if eps:
                out[extra] = sorted(set(eps))
    return out


# Páginas del menú principal (menu.py) → descripción para el cruce con JIS 2.0
DASHBOARD_MENU_MAP = [
    ("pages/dashboard_ventas_unificado.py", "Centro de Mando Ventas"),
    ("pages/ventas.py", "Dashboard de Ventas"),
    ("pages/ventas_diario.py", "Dashboard de Ventas Diarias"),
    ("pages/depositos.py", "Dashboard de Depósitos"),
    ("pages/dtes.py", "Dashboard Track de Abonados"),
    ("pages/rendiciones.py", "Dashboard Rendiciones"),
    ("pages/informe.py", "Informe / reporte gerencial (ventas)"),
    ("pages/datos_maestros.py", "Datos maestros / sucursales"),
]


def md_escape_fence(s: str) -> str:
    return s.replace("```", "``\u200b`")


def append_file_section(lines: list[str], repo_name: str, full_path: Path, repo_root: Path) -> None:
    rel = full_path.relative_to(repo_root).as_posix()
    try:
        body = full_path.read_text(encoding="utf-8", errors="replace")
    except OSError as e:
        body = f"# Error leyendo archivo: {e}\n"
    lines.append(f"\n\n---\n\n## `{repo_name}/{rel}`\n\n")
    lines.append(f"```{md_lang(rel)}\n")
    lines.append(md_escape_fence(body))
    if not body.endswith("\n"):
        lines.append("\n")
    lines.append("```\n")


def md_lang(rel: str) -> str:
    return "python"


def build_document() -> str:
    lines: list[str] = []
    now = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    ensure_shallow_clone(BACK_DIR, BACK_REMOTE)
    ensure_shallow_clone(FRONT_DIR, FRONT_REMOTE)
    back_sha = git_head(BACK_DIR)
    front_sha = git_head(FRONT_DIR)

    backend_app = BACK_DIR / "backend" / "app"
    routes = scan_backend_routers(BACK_DIR, backend_app)
    front_eps = scan_front_pages(FRONT_DIR)

    lines.append("# jisreportes.com — espejo de código y mapa de dashboards\n\n")
    lines.append(
        "Documento **generado automáticamente**. No editar a mano: volver a ejecutar "
        "`python scripts/build_jisreportes_source_mirror.py`.\n\n"
    )
    lines.append(f"- **Generado:** {now}\n")
    lines.append(f"- **Backend:** [{BACK_REMOTE}]({BACK_REMOTE}) @ `{back_sha}`\n")
    lines.append(f"- **Frontend:** [{FRONT_REMOTE}]({FRONT_REMOTE}) @ `{front_sha}`\n\n")

    lines.append("## 1. Qué contiene este archivo\n\n")
    lines.append(
        "1. **Inventario de rutas** del API FastAPI (prefijos de `APIRouter` + decoradores).\n"
        "2. **Endpoints** detectados en el front (patrón `api_request(\"GET\", \"/ruta\")`). "
        "Las rutas armadas por variables (f-strings dinámicos) pueden no aparecer.\n"
        "3. **Cruce** menú Streamlit → página → APIs usadas (cuando el scraper las encontró).\n"
        "4. **Anexo:** todo el código `.py` de ambos repos (clon bajo `artifacts/jisreportes_upstream/`, no versionado en Git).\n\n"
    )

    lines.append("## 2. Routers FastAPI (backend)\n\n")
    lines.append("| Archivo | Método | Ruta |\n")
    lines.append("|---------|--------|------|\n")
    for rel, method, path, _ in routes:
        lines.append(f"| `{rel}` | {method} | `{path}` |\n")
    lines.append("\n")

    lines.append("## 3. Llamadas `api_request` por archivo (frontend)\n\n")
    for page in sorted(front_eps.keys()):
        lines.append(f"### `{page}`\n\n")
        for method, ep in front_eps[page]:
            lines.append(f"- `{method}` `{ep}`\n")
        lines.append("\n")

    lines.append("## 4. Dashboards del menú → APIs detectadas en esa página\n\n")
    lines.append("| Pantalla (menú) | Archivo | Endpoints detectados |\n")
    lines.append("|-----------------|---------|----------------------|\n")
    for path, title in DASHBOARD_MENU_MAP:
        eps = front_eps.get(path, [])
        eps_s = ", ".join(f"`{m} {e}`" for m, e in eps) if eps else "*(dinámico o no detectado)*"
        lines.append(f"| {title} | `{path}` | {eps_s} |\n")
    lines.append("\n")

    lines.append("## 5. Paridad JIS Reportes 2.0 (recordatorio)\n\n")
    lines.append(
        "- **Sucursales:** legacy `GET /sucursales` y vistas `QRY_BRANCH_OFFICES` → agente `jis_listar_sucursales` / distribución.\n"
        "- **Ventas / informe:** KPI `KPI_INGRESOS_IMG_MES`, diario `KPI_INGRESOS_DIARIO` → tools `jis_*` alineadas en `PLAN_CATALOGO_DB_Y_HERRAMIENTAS.md`.\n"
        "- **Depósitos:** legacy `GET /operations/deposit_report` y vista `QRY_REPORTE_DEPOSITOS` → `jis_consultar_depositos` / `jis_resumen_depositos`.\n\n"
    )

    lines.append("---\n\n# Anexo A — Código completo: jisreportes_back\n\n")
    back_files = iter_py_files(BACK_DIR)
    lines.append(f"*Total archivos .py:* {len(back_files)}\n\n")
    for fp in back_files:
        append_file_section(lines, "jisreportes_back", fp, BACK_DIR)

    lines.append("\n\n---\n\n# Anexo B — Código completo: jisreportes_front\n\n")
    front_files = iter_py_files(FRONT_DIR)
    lines.append(f"*Total archivos .py:* {len(front_files)}\n\n")
    for fp in front_files:
        append_file_section(lines, "jisreportes_front", fp, FRONT_DIR)

    return "".join(lines)


def main() -> int:
    try:
        text = build_document()
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(text, encoding="utf-8")
    size_mb = OUT_PATH.stat().st_size / (1024 * 1024)
    print(f"OK: {OUT_PATH} ({size_mb:.2f} MiB)")
    if size_mb > 3:
        print("Nota: archivo grande; GitHub muestra bien pero el editor puede ir lento.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
