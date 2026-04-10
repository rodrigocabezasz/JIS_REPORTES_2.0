#!/usr/bin/env python3
"""
Introspección de MySQL (JIS Reportes 2.0) → catálogo Markdown.

Usa las mismas variables que jis_tools.py: DB_HOST, DB_PORT, DB_DATABASE,
DB_USER/DB_PASSWORD o DB_READONLY_*.

Ejecución (desde la raíz del repo, con .venv activo y túnel MySQL si aplica):

    python scripts/jis_db_mapper.py
    python scripts/jis_db_mapper.py --output docs/JIS_DB_MAP.md

Salida: JIS_DB_MAP.md (por defecto en la raíz del repo) para alimentar diseño
de tools y el prompt del agente. No incluye contraseñas ni datos de filas.
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Raíz del monorepo (…/JIS_REPORTES_2.0)
REPO_ROOT = Path(__file__).resolve().parent.parent


def _load_env() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(REPO_ROOT / ".env")
    load_dotenv(REPO_ROOT / "framework" / "agent-service-toolkit" / ".env", override=False)


def _db_params() -> dict:
    user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER")
    password = os.getenv("DB_PASSWORD") or os.getenv("DB_READONLY_PASSWORD")
    return {
        "host": os.getenv("DB_HOST"),
        "user": user,
        "password": password,
        "database": os.getenv("DB_DATABASE"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
    }


def _missing_db_config(params: dict) -> list[str]:
    missing: list[str] = []
    if not params.get("host"):
        missing.append("DB_HOST")
    if not params.get("user"):
        missing.append("DB_USER o DB_READONLY_USER")
    if not params.get("password"):
        missing.append("DB_PASSWORD o DB_READONLY_PASSWORD")
    if not params.get("database"):
        missing.append("DB_DATABASE")
    return missing


def _md_escape_cell(s: str | None) -> str:
    if s is None:
        return ""
    return str(s).replace("|", "\\|").replace("\n", " ").strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera JIS_DB_MAP.md desde INFORMATION_SCHEMA.")
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=REPO_ROOT / "JIS_DB_MAP.md",
        help="Ruta del Markdown de salida (default: raíz del repo / JIS_DB_MAP.md)",
    )
    parser.add_argument(
        "--schemas",
        type=str,
        default="",
        help="Lista separada por comas de schemas a incluir (vacío = solo DB_DATABASE)",
    )
    args = parser.parse_args()

    _load_env()
    params = _db_params()
    miss = _missing_db_config(params)
    if miss:
        print("Faltan variables de entorno: " + ", ".join(miss), file=sys.stderr)
        print("Completa .env en la raíz o en framework/agent-service-toolkit/.env", file=sys.stderr)
        return 2

    try:
        import mysql.connector
    except ImportError:
        print("Instala mysql-connector-python (pip install mysql-connector-python)", file=sys.stderr)
        return 2

    schemas_filter: list[str] | None = None
    if args.schemas.strip():
        schemas_filter = [s.strip() for s in args.schemas.split(",") if s.strip()]

    conn = mysql.connector.connect(**params)
    try:
        cur = conn.cursor(dictionary=True)
        db_name = params["database"]
        target_schemas = schemas_filter if schemas_filter else [db_name]

        # Tablas y vistas con metadatos
        cur.execute(
            """
            SELECT TABLE_SCHEMA, TABLE_NAME, TABLE_TYPE, ENGINE, TABLE_ROWS,
                   TABLE_COMMENT, CREATE_OPTIONS
            FROM information_schema.TABLES
            WHERE TABLE_SCHEMA IN ({})
            ORDER BY TABLE_SCHEMA, TABLE_TYPE, TABLE_NAME
            """.format(",".join(["%s"] * len(target_schemas))),
            tuple(target_schemas),
        )
        tables_meta = cur.fetchall()

        # Columnas
        cur.execute(
            """
            SELECT TABLE_SCHEMA, TABLE_NAME, COLUMN_NAME, ORDINAL_POSITION,
                   COLUMN_TYPE, IS_NULLABLE, COLUMN_KEY, COLUMN_DEFAULT, EXTRA, COLUMN_COMMENT
            FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA IN ({})
            ORDER BY TABLE_SCHEMA, TABLE_NAME, ORDINAL_POSITION
            """.format(",".join(["%s"] * len(target_schemas))),
            tuple(target_schemas),
        )
        columns = cur.fetchall()

        # Índices (útil para saber qué se puede filtrar/ordenar con eficiencia)
        cur.execute(
            """
            SELECT TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, NON_UNIQUE, SEQ_IN_INDEX, COLUMN_NAME
            FROM information_schema.STATISTICS
            WHERE TABLE_SCHEMA IN ({})
            ORDER BY TABLE_SCHEMA, TABLE_NAME, INDEX_NAME, SEQ_IN_INDEX
            """.format(",".join(["%s"] * len(target_schemas))),
            tuple(target_schemas),
        )
        stats = cur.fetchall()

        # Claves foráneas (relaciones lectura)
        cur.execute(
            """
            SELECT k.TABLE_SCHEMA, k.TABLE_NAME, k.COLUMN_NAME,
                   k.REFERENCED_TABLE_SCHEMA, k.REFERENCED_TABLE_NAME, k.REFERENCED_COLUMN_NAME,
                   c.CONSTRAINT_NAME
            FROM information_schema.KEY_COLUMN_USAGE k
            JOIN information_schema.TABLE_CONSTRAINTS c
              ON k.CONSTRAINT_SCHEMA = c.CONSTRAINT_SCHEMA
             AND k.TABLE_NAME = c.TABLE_NAME
             AND k.CONSTRAINT_NAME = c.CONSTRAINT_NAME
            WHERE c.CONSTRAINT_TYPE = 'FOREIGN KEY'
              AND k.TABLE_SCHEMA IN ({})
            ORDER BY k.TABLE_SCHEMA, k.TABLE_NAME, k.COLUMN_NAME
            """.format(",".join(["%s"] * len(target_schemas))),
            tuple(target_schemas),
        )
        fks = cur.fetchall()

        cur.close()
    finally:
        conn.close()

    # Agrupar columnas por (schema, table)
    col_by_table: dict[tuple[str, str], list[dict]] = {}
    for row in columns:
        key = (row["TABLE_SCHEMA"], row["TABLE_NAME"])
        col_by_table.setdefault(key, []).append(row)

    idx_by_table: dict[tuple[str, str], list[dict]] = {}
    for row in stats:
        key = (row["TABLE_SCHEMA"], row["TABLE_NAME"])
        idx_by_table.setdefault(key, []).append(row)

    fk_by_table: dict[tuple[str, str], list[dict]] = {}
    for row in fks:
        key = (row["TABLE_SCHEMA"], row["TABLE_NAME"])
        fk_by_table.setdefault(key, []).append(row)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines: list[str] = [
        "# Catálogo de base de datos JIS (MySQL)",
        "",
        f"*Generado automáticamente: {now}*",
        "",
        "## Conexión usada (sin secretos)",
        "",
        f"| Parámetro | Valor |",
        f"| --- | --- |",
        f"| Host | `{_md_escape_cell(params['host'])}` |",
        f"| Puerto | `{params['port']}` |",
        f"| Base (schema) | `{_md_escape_cell(db_name)}` |",
        f"| Usuario | `{_md_escape_cell(params['user'])}` |",
        "",
        "> **Nota:** `TABLE_ROWS` en MySQL/InnoDB es una estimación; úsala solo como orden de magnitud.",
        "",
        "## Resumen",
        "",
    ]

    n_tables = sum(1 for t in tables_meta if t["TABLE_TYPE"] == "BASE TABLE")
    n_views = sum(1 for t in tables_meta if t["TABLE_TYPE"] == "VIEW")
    lines.append(f"- **Tablas base:** {n_tables}")
    lines.append(f"- **Vistas:** {n_views}")
    lines.append(f"- **Objetos con columnas listadas:** {len(col_by_table)}")
    lines.append("")

    for meta in tables_meta:
        schema = meta["TABLE_SCHEMA"]
        name = meta["TABLE_NAME"]
        ttype = meta["TABLE_TYPE"]
        key = (schema, name)

        lines.append(f"## `{schema}`.`{name}`")
        lines.append("")
        lines.append(f"- **Tipo:** {ttype}")
        if meta.get("ENGINE"):
            lines.append(f"- **Motor:** {meta['ENGINE']}")
        if meta.get("TABLE_ROWS") is not None:
            lines.append(f"- **Filas estimadas (information_schema):** {meta['TABLE_ROWS']}")
        if meta.get("TABLE_COMMENT"):
            lines.append(f"- **Comentario tabla:** {_md_escape_cell(meta['TABLE_COMMENT'])}")
        lines.append("")

        cols = col_by_table.get(key, [])
        if not cols:
            lines.append("*Sin columnas visibles (permisos o objeto vacío en IS).*")
            lines.append("")
            continue

        lines.append("| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |")
        lines.append("| --- | --- | --- | --- | --- | --- | --- | --- |")
        for c in cols:
            lines.append(
                "| "
                + " | ".join(
                    [
                        str(c["ORDINAL_POSITION"]),
                        f"`{_md_escape_cell(c['COLUMN_NAME'])}`",
                        _md_escape_cell(c["COLUMN_TYPE"]),
                        _md_escape_cell(c["IS_NULLABLE"]),
                        _md_escape_cell(c["COLUMN_KEY"]),
                        f"`{_md_escape_cell(str(c['COLUMN_DEFAULT']))}`" if c["COLUMN_DEFAULT"] is not None else "",
                        _md_escape_cell(c["EXTRA"]),
                        _md_escape_cell(c["COLUMN_COMMENT"]),
                    ]
                )
                + " |"
            )
        lines.append("")

        fks_here = fk_by_table.get(key, [])
        if fks_here:
            lines.append("**Claves foráneas (salientes)**")
            lines.append("")
            lines.append("| Columna | Referencia | Constraint |")
            lines.append("| --- | --- | --- |")
            for fk in fks_here:
                ref = f"`{fk['REFERENCED_TABLE_NAME']}`.`{fk['REFERENCED_COLUMN_NAME']}`"
                lines.append(
                    f"| `{_md_escape_cell(fk['COLUMN_NAME'])}` | {ref} | `{_md_escape_cell(fk['CONSTRAINT_NAME'])}` |"
                )
            lines.append("")

        idx_here = idx_by_table.get(key, [])
        if idx_here:
            # Agrupar por INDEX_NAME
            by_name: dict[str, list[str]] = {}
            for s in idx_here:
                by_name.setdefault(s["INDEX_NAME"], []).append(s["COLUMN_NAME"])
            lines.append("**Índices**")
            lines.append("")
            for iname, cols_i in sorted(by_name.items()):
                sample = next((x for x in idx_here if x["INDEX_NAME"] == iname), None)
                # NON_UNIQUE: 0 = índice único
                u = "único" if sample and not sample["NON_UNIQUE"] else "no único"
                lines.append(f"- `{_md_escape_cell(iname)}` ({u}): {', '.join('`' + _md_escape_cell(c) + '`' for c in cols_i)}")
            lines.append("")

    lines.extend(
        [
            "---",
            "",
            "## Uso para el agente",
            "",
            "1. Priorizar **vistas** ya usadas por reportes (ej. `QRY_*`) para lecturas estables.",
            "2. Tablas base: solo lectura con SQL acotado y columnas explícitas.",
            "3. Cruzar con este mapa las **preguntas de negocio** → nuevas tools (inventario / resumen / ranking / tendencia).",
            "",
        ]
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text("\n".join(lines), encoding="utf-8")
    print(f"Escrito: {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
