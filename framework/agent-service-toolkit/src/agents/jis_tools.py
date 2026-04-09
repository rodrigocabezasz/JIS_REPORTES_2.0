"""Herramientas JIS PARKING: consultas MySQL alineadas a jisreportes_back (legacy)."""

import json
import os
from typing import Any

import mysql.connector
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()


def _db_params() -> dict[str, Any]:
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


def _coerce_solo_activas(value: Any, default: bool = True) -> bool:
    """El LLM a veces manda 'false' como string."""
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    s = str(value).strip().lower()
    if s in ("false", "0", "no"):
        return False
    if s in ("true", "1", "si", "sí", "yes"):
        return True
    return default


def _missing_db_config() -> list[str]:
    p = _db_params()
    missing: list[str] = []
    if not p.get("host"):
        missing.append("DB_HOST")
    if not p.get("user"):
        missing.append("DB_USER o DB_READONLY_USER")
    if not p.get("password"):
        missing.append("DB_PASSWORD o DB_READONLY_PASSWORD")
    if not p.get("database"):
        missing.append("DB_DATABASE")
    return missing


# Palabras que no aportan a buscar un nombre (evita AND débil tipo %de% %la%)
_STOP_NOMBRE = frozenset(
    {
        "de",
        "la",
        "el",
        "los",
        "las",
        "del",
        "y",
        "o",
        "en",
        "un",
        "una",
        "al",
        "a",
    }
)


def _tokens_busqueda_nombre(raw: str) -> list[str]:
    """Parte el texto en tokens útiles para AND de LIKE sobre nombres completos."""
    out: list[str] = []
    for part in raw.replace(",", " ").split():
        t = part.strip()
        if len(t) < 2:
            continue
        tl = t.lower()
        if tl in _STOP_NOMBRE:
            continue
        out.append(t)
    return out


def _append_responsable_filters(
    conds: list[str],
    params: list[str],
    fa: dict[str, Any],
    filtro_parts: list[str],
    raw: str | None,
) -> None:
    """Alineado a Navicat: nombre largo → un LIKE %frase%; 2 palabras → AND (ej. david gomez)."""
    v = (raw or "").strip()
    if not v:
        return
    tokens = _tokens_busqueda_nombre(v)
    if len(tokens) >= 3:
        # Igual que: responsable LIKE '%Benjamin Leonardo Bruyer Gonzalez%' (un substring continuo)
        phrase = " ".join(tokens)
        conds.append("LOWER(responsable) LIKE LOWER(%s)")
        params.append(f"%{phrase}%")
        fa["responsable_contiene"] = v
        fa["responsable_modo"] = "frase_completa"
        filtro_parts.append(f"Responsable contiene la frase «{phrase}» (LIKE, como Navicat)")
    elif len(tokens) == 2:
        for t in tokens:
            conds.append("LOWER(responsable) LIKE LOWER(%s)")
            params.append(f"%{t}%")
        fa["responsable_contiene"] = v
        fa["responsable_modo"] = "dos_palabras_and"
        fa["responsable_tokens"] = tokens
        filtro_parts.append(
            "Responsable incluye ambas palabras: " + ", ".join(f"«{t}»" for t in tokens)
        )
    else:
        needle = tokens[0] if tokens else v
        conds.append("LOWER(responsable) LIKE LOWER(%s)")
        params.append(f"%{needle}%")
        fa["responsable_contiene"] = v
        fa["responsable_modo"] = "una_palabra"
        filtro_parts.append(f"Responsable contiene «{needle}» (LIKE)")


def _append_like(
    conds: list[str],
    params: list[str],
    fa: dict[str, Any],
    filtro_parts: list[str],
    raw: str | None,
    *,
    columna_sql: str,
    clave_json: str,
    etiqueta_humana: str,
) -> None:
    v = (raw or "").strip()
    if not v:
        return
    conds.append(f"LOWER({columna_sql}) LIKE LOWER(%s)")
    params.append(f"%{v}%")
    fa[clave_json] = v
    filtro_parts.append(f"{etiqueta_humana} contiene «{v}» (LIKE)")


@tool
def jis_listar_sucursales(
    responsable_contiene: str | None = None,
    sucursal_contiene: str | None = None,
    nombre_sucursal_contiene: str | None = None,
    region_contiene: str | None = None,
    comuna_contiene: str | None = None,
    zona_contiene: str | None = None,
    segmento_contiene: str | None = None,
    principal_contiene: str | None = None,
    direccion_contiene: str | None = None,
    solo_activas: bool | None = True,
) -> str:
    """Lista sucursales (vista QRY_BRANCH_OFFICES). No pide año/mes.

    Por defecto solo sucursales activas (status_id = 7), alineado al listado operativo del legacy.

    Los argumentos están en español para el usuario; en MySQL se filtra por la columna en inglés indicada.

    Args:
        responsable_contiene: Persona responsable (columna responsable). Tres o más palabras → un solo
            LIKE con la frase (igual que Navicat). Dos palabras (ej. "david gomez") → ambas deben aparecer
            aunque haya texto entre medias.
        sucursal_contiene: Nombre del local (columna branch_office). Si el usuario dice "sucursal", usa esto.
        nombre_sucursal_contiene: Alias de sucursal_contiene (compatibilidad); si pasan ambos, gana el no vacío más específico.
        region_contiene: Región (columna region).
        comuna_contiene: Comuna (columna commune). Si dice "comuna", usa esto, no "commune".
        zona_contiene: Zona (columna zone).
        segmento_contiene: Segmento (columna segment).
        principal_contiene: Marca / cadena principal (columna principal).
        direccion_contiene: Dirección / calle (columna address).
        solo_activas: True (default) = solo status_id 7. False = todas las filas de la vista para ese
            responsable u otros filtros (útil para "cuántas sucursales tiene X" si hay locales inactivos).
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )
    activas = _coerce_solo_activas(solo_activas, default=True)
    base_select = (
        "SELECT responsable, (id*1) as branch_office_id, branch_office, dte_code, "
        "principal AS marca, zone AS zona, segment AS segmento, address AS direccion, "
        "region, commune, status_id FROM QRY_BRANCH_OFFICES WHERE "
    )
    if activas:
        base_select += "status_id = 7"
    else:
        base_select += "1=1"
    conds: list[str] = []
    params: list[str] = []
    fa: dict[str, Any] = {}
    filtro_parts: list[str] = (
        ["status_id = 7 (solo activas)"] if activas else ["sin filtro de status (todas las filas de la vista)"]
    )

    suc_val = (sucursal_contiene or "").strip() or (nombre_sucursal_contiene or "").strip()

    _append_responsable_filters(conds, params, fa, filtro_parts, responsable_contiene)
    _append_like(
        conds, params, fa, filtro_parts, suc_val if suc_val else None,
        columna_sql="branch_office", clave_json="sucursal_contiene", etiqueta_humana="Sucursal (branch_office)",
    )
    _append_like(
        conds, params, fa, filtro_parts, region_contiene,
        columna_sql="region", clave_json="region_contiene", etiqueta_humana="Región",
    )
    _append_like(
        conds, params, fa, filtro_parts, comuna_contiene,
        columna_sql="commune", clave_json="comuna_contiene", etiqueta_humana="Comuna (commune)",
    )
    _append_like(
        conds, params, fa, filtro_parts, zona_contiene,
        columna_sql="zone", clave_json="zona_contiene", etiqueta_humana="Zona (zone)",
    )
    _append_like(
        conds, params, fa, filtro_parts, segmento_contiene,
        columna_sql="segment", clave_json="segmento_contiene", etiqueta_humana="Segmento (segment)",
    )
    _append_like(
        conds, params, fa, filtro_parts, principal_contiene,
        columna_sql="principal", clave_json="principal_contiene", etiqueta_humana="Marca / principal",
    )
    _append_like(
        conds, params, fa, filtro_parts, direccion_contiene,
        columna_sql="address", clave_json="direccion_contiene", etiqueta_humana="Dirección (address)",
    )

    query = base_select
    filtro = "; ".join(filtro_parts)
    if conds:
        query += " AND " + " AND ".join(conds)
    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)
        if params:
            cur.execute(query, tuple(params))
        else:
            cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        db_user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER") or ""
        return json.dumps(
            {
                "success": True,
                "source": "mysql",
                "tabla_o_vista": "QRY_BRANCH_OFFICES",
                "filtro": filtro,
                "solo_activas": activas,
                "filtros_aplicados": fa if fa else {},
                "mysql_user": db_user,
                "count": len(rows),
                "data": rows,
            },
            default=str,
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


@tool
def jis_consultar_kpi_ingresos(
    tipo_vista: str,
    year: int,
    month: int,
    branch_office_id: int | None = None,
) -> str:
    """KPI de ingresos desde KPI_INGRESOS_IMG_MES (mensual o acumulado).

    Args:
        tipo_vista: Texto 'mensual' o 'acumulado'.
        year: Año de la consulta (ej. 2025).
        month: Mes numérico 1-12.
        branch_office_id: Si se informa, filtra solo esa sucursal; si no, todas las activas.
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )
    periodo = "Acumulado" if str(tipo_vista).strip().lower() == "acumulado" else "Mensual"
    base_sql = """
        SELECT k.*
        FROM KPI_INGRESOS_IMG_MES k
        INNER JOIN QRY_BRANCH_OFFICES bo ON bo.id = k.branch_office_id AND bo.status_id = 7
        WHERE k.periodo = %s
          AND k.metrica = 'ingresos'
          AND k.año IN (%s, %s)
          AND MONTH(k.date) = %s
    """
    if branch_office_id is not None:
        query = base_sql + " AND k.branch_office_id = %s"
        params = (periodo, year, year - 1, month, branch_office_id)
    else:
        query = base_sql
        params = (periodo, year, year - 1, month)
    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        rows = cur.fetchall()
        max_rows = 500
        truncated = len(rows) > max_rows
        out_rows = rows[:max_rows] if truncated else rows
        cur.close()
        conn.close()
        db_user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER") or ""
        return json.dumps(
            {
                "success": True,
                "source": "mysql",
                "tabla_o_vista": "KPI_INGRESOS_IMG_MES + QRY_BRANCH_OFFICES",
                "mysql_user": db_user,
                "periodo": periodo,
                "truncated": truncated,
                "count": len(rows),
                "data": out_rows,
            },
            default=str,
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
