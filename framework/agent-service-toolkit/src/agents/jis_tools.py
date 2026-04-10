"""Herramientas JIS PARKING: consultas MySQL alineadas a jisreportes_back (legacy)."""

import json
import os
import re
from calendar import monthrange
from datetime import date, datetime
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


def _coerce_modo_respuesta(value: Any) -> str:
    """listar = tabla completa en UI; contar = solo total (el grafo formatea en una frase)."""
    if value is None:
        return "listar"
    s = str(value).strip().lower()
    if s in ("contar", "count", "solo_conteo", "conteo", "resumen_numerico"):
        return "contar"
    return "listar"


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


def _normalizar_sta_santa_en_frase(text: str | None) -> str | None:
    """Expande abreviatura inicial Sta/STA/Sta. → Santa (ej. principal 'SANTA ISABEL' en BD)."""
    if text is None:
        return None
    t = str(text).strip()
    if not t:
        return t
    return re.sub(r"(?i)^sta\.?\s+", "Santa ", t, count=1)


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


def _append_like_or_columnas(
    conds: list[str],
    params: list[Any],
    fa: dict[str, Any],
    filtro_parts: list[str],
    raw: str | None,
    *,
    columnas_sql: list[str],
    clave_json: str,
    etiqueta_filtro: str,
) -> None:
    """Un mismo texto en cualquiera de las columnas (OR), p. ej. nombre local vs marca vs comuna."""
    v = (raw or "").strip()
    if not v:
        return
    needle = f"%{v}%"
    parts = [f"LOWER({c}) LIKE LOWER(%s)" for c in columnas_sql]
    conds.append("(" + " OR ".join(parts) + ")")
    for _ in columnas_sql:
        params.append(needle)
    fa[clave_json] = v
    filtro_parts.append(f"{etiqueta_filtro}: «{v}» (OR sobre {', '.join(columnas_sql)})")


def _append_marca_principal_u_office_si_multipalabra(
    conds: list[str],
    params: list[Any],
    fa: dict[str, Any],
    filtro_parts: list[str],
    marca_val: str,
) -> None:
    """Frases tipo «LIDER CORDILLERA» suelen ser nombre de local (branch_office), no la columna principal."""
    v = marca_val.strip()
    if not v:
        return
    needle = f"%{v}%"
    if len(v.split()) >= 2:
        conds.append(
            "(LOWER(principal) LIKE LOWER(%s) OR LOWER(branch_office) LIKE LOWER(%s))"
        )
        params.append(needle)
        params.append(needle)
        fa["principal_contiene"] = v
        fa["marca_multipalabra_incluye_branch_office"] = True
        filtro_parts.append(
            f"Marca / principal O sucursal (branch_office) contiene «{v}» (LIKE; frase de 2+ palabras)"
        )
    else:
        conds.append("LOWER(principal) LIKE LOWER(%s)")
        params.append(needle)
        fa["principal_contiene"] = v
        filtro_parts.append(f"Marca / principal contiene «{v}» (LIKE)")


def _coerce_visibility_reporte(value: Any) -> bool | None:
    """True = mismo criterio que reportes por responsable en legacy (visibility_id = 1)."""
    if value is None:
        return None
    if isinstance(value, bool):
        return value if value else None
    s = str(value).strip().lower()
    if s in ("true", "1", "si", "sí", "yes"):
        return True
    return None


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
    marca_contiene: str | None = None,
    direccion_contiene: str | None = None,
    codigo_dte_contiene: str | None = None,
    supervisor_contiene: str | None = None,
    branch_office_id: int | None = None,
    solo_activas: bool | None = True,
    solo_visibilidad_reporte: bool | None = None,
    modo_respuesta: str | None = None,
    local_marca_o_comuna_contiene: str | None = None,
) -> str:
    """Lista sucursales (vista QRY_BRANCH_OFFICES). No pide año/mes.

    Por defecto solo sucursales activas (status_id = 7), alineado a jisreportes (GET /sucursales, joins).

    En la práctica el usuario casi siempre identifica el local por el **nombre de sucursal** (columna branch_office),
    p. ej. «LIDER CORDILLERA», «TOTTUS LA FLORIDA». Para «dame el id», «código DTE», «número de sucursal» o
    «código de local» usando ese nombre → usa **sucursal_contiene** (o nombre_sucursal_contiene), no marca_contiene.
    La respuesta incluye branch_office_id (id API) y dte_code en cada fila.

    Los argumentos están en español para el usuario; en MySQL se filtra por la columna real indicada.

    Args:
        responsable_contiene: Responsable comercial (columna responsable). 3+ palabras → frase única LIKE
            (Navicat). 2 palabras → ambas deben aparecer (AND LIKE).
        sucursal_contiene: Nombre del local (branch_office).
        nombre_sucursal_contiene: Alias de sucursal_contiene; si ambos vienen, se usa el no vacío.
        region_contiene: Región (region).
        comuna_contiene: Comuna (commune).
        zona_contiene: Zona (zone).
        segmento_contiene: Segmento de negocio (segment), ej. MALL, SUPERMERCADO.
        principal_contiene: Marca corta en columna principal (ej. LIDER, TOTTUS). Si el usuario dice varias
            palabras juntas (ej. «LIDER CORDILLERA»), suele ser nombre del local: la tool busca también en branch_office.
        marca_contiene: Alias de principal_contiene (el usuario suele decir "marca"); gana el no vacío.
        direccion_contiene: Dirección (address).
        codigo_dte_contiene: Buscar por **fragmento del código DTE** cuando el usuario ya trae el código (dte_code).
            Si el usuario trae el **nombre del local** y quiere saber el DTE → usa sucursal_contiene, no este campo.
        supervisor_contiene: Supervisor / RUT en principal_supervisor (búsqueda parcial LIKE).
        branch_office_id: ID exacto de sucursal (id en la vista = branch_office_id en APIs).
        solo_activas: True (default) = status_id 7. False = incluye otras filas de la vista (p. ej. totales
            asignados a un responsable con locales inactivos).
        solo_visibilidad_reporte: True = visibility_id 1 (criterio reportes por responsable en legacy).
        modo_respuesta: "listar" (default) devuelve filas para tabla; "contar" para que el agente responda
            solo el total en texto (misma consulta, menos ruido en chat).
        local_marca_o_comuna_contiene: Cuando el usuario nombra un lugar o texto que puede estar en el **nombre
            del local** (branch_office, ej. "LIDER STA ISABEL"), en la **marca** (principal) o en la **comuna**
            (commune), pero no sabes cuál. Usa esto en lugar de solo marca_contiene para evitar 0 resultados.
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )
    activas = _coerce_solo_activas(solo_activas, default=True)
    modo = _coerce_modo_respuesta(modo_respuesta)
    vis = _coerce_visibility_reporte(solo_visibilidad_reporte)

    base_select = (
        "SELECT responsable, (id*1) as branch_office_id, branch_office, dte_code, "
        "principal AS marca, zone AS zona, segment AS segmento, address AS direccion, "
        "region, commune, visibility_id, status_id FROM QRY_BRANCH_OFFICES WHERE "
    )
    if activas:
        base_select += "status_id = 7"
    else:
        base_select += "1=1"
    conds: list[str] = []
    params: list[Any] = []
    fa: dict[str, Any] = {"modo_respuesta": modo}
    filtro_parts: list[str] = (
        ["status_id = 7 (solo activas)"] if activas else ["sin filtro de status (todas las filas de la vista)"]
    )

    if vis is True:
        conds.append("visibility_id = 1")
        filtro_parts.append("visibility_id = 1 (solo sucursales visibles en reportes por responsable)")
        fa["solo_visibilidad_reporte"] = True

    if branch_office_id is not None:
        try:
            bid = int(branch_office_id)
        except (TypeError, ValueError):
            bid = None
        if bid is not None:
            conds.append("id = %s")
            params.append(bid)
            fa["branch_office_id"] = bid
            filtro_parts.append(f"id (branch_office_id) = {bid}")

    suc_raw = (sucursal_contiene or "").strip() or (nombre_sucursal_contiene or "").strip()
    suc_val = _normalizar_sta_santa_en_frase(suc_raw) or ""
    marca_raw = (principal_contiene or "").strip() or (marca_contiene or "").strip()
    marca_val = _normalizar_sta_santa_en_frase(marca_raw) or ""
    local_raw = (local_marca_o_comuna_contiene or "").strip()
    local_val = _normalizar_sta_santa_en_frase(local_raw) if local_raw else None

    if marca_raw and marca_val and marca_raw.strip().lower() != marca_val.lower():
        fa["marca_busqueda_ampliada_sta_santa"] = marca_val
    if suc_raw and suc_val and suc_raw.strip().lower() != suc_val.lower():
        fa["sucursal_busqueda_ampliada_sta_santa"] = suc_val
    if local_raw and local_val and local_raw.strip().lower() != (local_val or "").lower():
        fa["local_marca_comuna_busqueda_ampliada_sta_santa"] = local_val

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
    if marca_val:
        _append_marca_principal_u_office_si_multipalabra(conds, params, fa, filtro_parts, marca_val)
    _append_like(
        conds, params, fa, filtro_parts, direccion_contiene,
        columna_sql="address", clave_json="direccion_contiene", etiqueta_humana="Dirección (address)",
    )
    _append_like(
        conds, params, fa, filtro_parts, codigo_dte_contiene,
        columna_sql="dte_code", clave_json="codigo_dte_contiene", etiqueta_humana="Código DTE (dte_code)",
    )
    _append_like(
        conds, params, fa, filtro_parts, supervisor_contiene,
        columna_sql="principal_supervisor",
        clave_json="supervisor_contiene",
        etiqueta_humana="Supervisor / RUT (principal_supervisor)",
    )
    _append_like_or_columnas(
        conds,
        params,
        fa,
        filtro_parts,
        local_val,
        columnas_sql=["branch_office", "principal", "commune"],
        clave_json="local_marca_o_comuna_contiene",
        etiqueta_filtro="Nombre local O marca O comuna",
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
                "modo_respuesta": modo,
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


# dimension arg (español) -> columna SQL en QRY_BRANCH_OFFICES
_DISTRIBUCION_COLUMNAS: dict[str, tuple[str, str]] = {
    "segmento": ("segment", "Segmento"),
    "zona": ("zone", "Zona"),
    "region": ("region", "Región"),
    "comuna": ("commune", "Comuna"),
    "marca": ("principal", "Marca / principal"),
}


@tool
def jis_distribucion_sucursales(
    dimension: str,
    solo_activas: bool | None = True,
) -> str:
    """Cantidad y porcentaje de sucursales agrupadas por una dimensión (solo conteos, sin listar cada local).

    Usar cuando piden "porcentaje por segmento", "cuántas por zona", "distribución por marca/comuna", etc.

    Args:
        dimension: Una de: segmento, zona, region, comuna, marca (sin importar mayúsculas).
        solo_activas: True (default) = solo status_id = 7; False = todas las filas de la vista.
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )
    dim_key = str(dimension).strip().lower()
    aliases = {
        "segmentos": "segmento",
        "marcas": "marca",
        "zonas": "zona",
        "regiones": "region",
        "comunas": "comuna",
    }
    dim_key = aliases.get(dim_key, dim_key)
    if dim_key not in _DISTRIBUCION_COLUMNAS:
        return json.dumps(
            {
                "success": False,
                "error": f"dimension inválida: {dimension!r}. Use: {', '.join(_DISTRIBUCION_COLUMNAS)}",
            },
            ensure_ascii=False,
        )
    col_sql, dim_label = _DISTRIBUCION_COLUMNAS[dim_key]
    activas = _coerce_solo_activas(solo_activas, default=True)
    where = "status_id = 7" if activas else "1=1"
    query = (
        f"SELECT {col_sql} AS grupo, COUNT(*) AS cantidad "
        f"FROM QRY_BRANCH_OFFICES WHERE {where} GROUP BY {col_sql} ORDER BY cantidad DESC"
    )
    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)
        cur.execute(query)
        raw_rows = cur.fetchall()
        cur.close()
        conn.close()
        db_user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER") or ""
        rows: list[dict[str, Any]] = []
        for r in raw_rows:
            if not isinstance(r, dict):
                continue
            g = r.get("grupo")
            if g is None or (isinstance(g, str) and not str(g).strip()):
                g = "(sin valor)"
            rows.append({"grupo": g, "cantidad": int(r.get("cantidad") or 0)})
        total = sum(x["cantidad"] for x in rows)
        out_data: list[dict[str, Any]] = []
        for x in rows:
            pct = round(100.0 * x["cantidad"] / total, 2) if total else 0.0
            out_data.append(
                {"grupo": x["grupo"], "cantidad": x["cantidad"], "porcentaje": pct}
            )
        return json.dumps(
            {
                "success": True,
                "source": "mysql",
                "tipo_resultado": "distribucion_sucursales",
                "tabla_o_vista": "QRY_BRANCH_OFFICES",
                "dimension": dim_key,
                "dimension_etiqueta": dim_label,
                "solo_activas": activas,
                "mysql_user": db_user,
                "total_sucursales": total,
                "count": len(out_data),
                "data": out_data,
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
    """KPI de ingresos desde KPI_INGRESOS_IMG_MES (mensual o acumulado), un año y un mes.

    Para cuadro **ingresos + presupuesto vs año anterior** (total, por sucursal o por responsable) usar
    **jis_informe_ventas_comparativo**.

    Args:
        tipo_vista: Texto 'mensual' o 'acumulado'.
        year: Año de la consulta (ej. 2025).
        month: Mes numérico 1-12.
        branch_office_id: Si se informa, filtra solo esa sucursal; si no, todas las activas.
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"success": False, "error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )
    periodo = "Acumulado" if str(tipo_vista).strip().lower() == "acumulado" else "Mensual"
    base_sql = """
        SELECT k.*
        FROM KPI_INGRESOS_IMG_MES k
        INNER JOIN QRY_BRANCH_OFFICES bo ON bo.id = k.branch_office_id AND bo.status_id = 7
        WHERE k.periodo = %s
          AND k.metrica = 'ingresos'
          AND k.año = %s
          AND MONTH(k.date) = %s
    """
    if branch_office_id is not None:
        query = base_sql + " AND k.branch_office_id = %s"
        params = (periodo, year, month, branch_office_id)
    else:
        query = base_sql
        params = (periodo, year, month)
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
                "year": year,
                "month": month,
                "truncated": truncated,
                "count": len(rows),
                "data": out_rows,
            },
            default=str,
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


# Misma definición de “Ingresos” que el dashboard jisreportes.com (informe gerencial): neto + abonados.
# El ranking / top sucursales sigue usando bruto+tarjeta+abonados en sus queries dedicadas.
_AGG_INGRESOS_TICKETS_PPTO = """
        SUM(
            CASE WHEN k.metrica = 'ingresos' THEN
                COALESCE(k.cash_net_amount, 0) + COALESCE(k.card_net_amount, 0) + COALESCE(k.subscribers, 0)
            ELSE 0 END
        ) AS ingresos_proxy,
        SUM(
            CASE WHEN k.metrica = 'ingresos' THEN COALESCE(k.ticket_number, 0) ELSE 0 END
        ) AS tickets,
        SUM(
            CASE WHEN k.metrica = 'ppto' THEN COALESCE(k.ppto, 0) ELSE 0 END
        ) AS presupuesto
"""


def _float_val(v: Any) -> float:
    if v is None:
        return 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def _pct_yoy(actual: float, prev: float) -> float | None:
    if prev is None or prev == 0:
        return None
    return round((actual - prev) / prev * 100.0, 2)


def _pct_vs_presupuesto(ingresos: float, ppto: float) -> float | None:
    """Desv % vs PPTO del dashboard (cumplimiento): (real - meta) / meta."""
    if ppto is None or ppto == 0:
        return None
    return round((ingresos - ppto) / ppto * 100.0, 2)


def _ticket_promedio(ingresos: float, tickets: float) -> float | None:
    if tickets is None or tickets == 0:
        return None
    return round(ingresos / tickets, 2)


_INFORME_MESES_ES = (
    "",
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
)


def _fila_informe_ventas(
    *,
    grupo: str,
    ry: dict[str, Any],
    rp: dict[str, Any],
    branch_office_id: int | None = None,
    branch_office: Any = None,
    responsable: Any = None,
    sucursales_en_filtro: int | None = None,
) -> dict[str, Any]:
    ia = _float_val(ry.get("ingresos_proxy"))
    ip = _float_val(rp.get("ingresos_proxy"))
    ta = _float_val(ry.get("tickets"))
    tp = _float_val(rp.get("tickets"))
    pa = _float_val(ry.get("presupuesto"))
    pp = _float_val(rp.get("presupuesto"))
    out: dict[str, Any] = {
        "grupo": grupo,
        "ingresos_proxy_año_actual": ia,
        "ingresos_proxy_año_anterior": ip,
        "presupuesto_año_actual": pa,
        "presupuesto_año_anterior": pp,
        "var_pct_ingresos_yoy": _pct_yoy(ia, ip),
        "var_pct_presupuesto_yoy": _pct_yoy(pa, pp),
        "desv_pct_ingresos_vs_presupuesto": _pct_vs_presupuesto(ia, pa),
        "tickets_año_actual": ta,
        "tickets_año_anterior": tp,
        "ticket_promedio_año_actual": _ticket_promedio(ia, ta),
        "ticket_promedio_año_anterior": _ticket_promedio(ip, tp),
    }
    if branch_office_id is not None:
        out["branch_office_id"] = branch_office_id
    if branch_office is not None:
        out["branch_office"] = branch_office
    if responsable is not None:
        out["responsable"] = responsable
    if sucursales_en_filtro is not None:
        out["sucursales_en_filtro"] = sucursales_en_filtro
    return out


@tool
def jis_informe_ventas_comparativo(
    year: int,
    month: int,
    agrupacion: str = "total",
    tipo_periodo: str = "mensual",
    alcance_temporal: str = "mes",
    branch_office_id: int | None = None,
    responsable_contiene: str | None = None,
) -> str:
    """Informe de ventas al estilo jisreportes.com: ingresos vs año anterior, presupuesto, tickets y ticket promedio.

    Réplica funcional del **Resumen general** e **Informe gerencial** (sin gráficos). Los **ingresos** usan
    efectivo **neto** + tarjeta **neta** + abonados (misma base que el dashboard web), no los montos brutos.

    Args:
        year: Año actual del análisis (ej. 2026); se compara con year-1.
        month: Mes de referencia 1-12. En modo **mes** es el único mes; en **ytd** es el tope del acumulado (ene..mes).
        agrupacion: "total" (tarjetas resumen), "sucursal" (tabla gerencial por parking), "responsable".
        tipo_periodo: Solo si **alcance_temporal** = "mes": "mensual" o "acumulado" (columna `periodo` en KPI).
        alcance_temporal: "mes" = un solo mes (vista Mensual histórico); "ytd" = acumulado ene..month con filas
            **Mensual** del KPI (vista Acumulado mes en curso en el dashboard legacy).
        branch_office_id: Opcional; una sucursal activa.
        responsable_contiene: Opcional; filtro LIKE sobre `bo.responsable`.
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"success": False, "error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )
    ag = (agrupacion or "total").strip().lower()
    if ag not in ("total", "sucursal", "responsable"):
        return json.dumps(
            {
                "success": False,
                "error": 'agrupacion debe ser "total", "sucursal" o "responsable".',
            },
            ensure_ascii=False,
        )
    alc = (alcance_temporal or "mes").strip().lower()
    if alc not in ("mes", "ytd"):
        return json.dumps(
            {"success": False, "error": 'alcance_temporal debe ser "mes" o "ytd".'},
            ensure_ascii=False,
        )
    y = int(year)
    m = int(month)
    if not (1 <= m <= 12):
        return json.dumps({"success": False, "error": "month debe estar entre 1 y 12."}, ensure_ascii=False)
    y_prev = y - 1
    periodo = _kpi_periodo_tipo(tipo_periodo) if alc == "mes" else "Mensual"
    if alc == "ytd":
        base_where = """
        WHERE k.periodo = %s
          AND k.metrica IN ('ingresos', 'ppto')
          AND k.año IN (%s, %s)
          AND MONTH(k.date) BETWEEN 1 AND %s
        """
        params_base: list[Any] = ["Mensual", y, y_prev, m]
    else:
        base_where = """
        WHERE k.periodo = %s
          AND k.metrica IN ('ingresos', 'ppto')
          AND k.año IN (%s, %s)
          AND MONTH(k.date) = %s
        """
        params_base = [periodo, y, y_prev, m]

    if branch_office_id is not None:
        base_where += " AND k.branch_office_id = %s"
        params_base.append(int(branch_office_id))
    rc = (responsable_contiene or "").strip()
    if rc:
        base_where += " AND LOWER(bo.responsable) LIKE LOWER(%s)"
        params_base.append(f"%{rc}%")

    join = """
        FROM KPI_INGRESOS_IMG_MES k
        INNER JOIN QRY_BRANCH_OFFICES bo ON bo.id = k.branch_office_id AND bo.status_id = 7
    """
    if ag == "total":
        sql = f"""
            SELECT k.año, {_AGG_INGRESOS_TICKETS_PPTO},
                COUNT(DISTINCT k.branch_office_id) AS sucursales_distintas
            {join}
            {base_where}
            GROUP BY k.año
        """
    elif ag == "responsable":
        sql = f"""
            SELECT bo.responsable, k.año, {_AGG_INGRESOS_TICKETS_PPTO}
            {join}
            {base_where}
            GROUP BY bo.responsable, k.año
            ORDER BY bo.responsable
        """
    else:
        sql = f"""
            SELECT k.branch_office_id, bo.branch_office, bo.responsable, k.año,
            {_AGG_INGRESOS_TICKETS_PPTO}
            {join}
            {base_where}
            GROUP BY k.branch_office_id, bo.branch_office, bo.responsable, k.año
            ORDER BY bo.branch_office
        """

    max_out = 500
    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, tuple(params_base))
        rows = cur.fetchall()
        cur.close()
        conn.close()
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)

    db_user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER") or ""

    def empty_year_row() -> dict[str, Any]:
        return {"ingresos_proxy": 0.0, "tickets": 0.0, "presupuesto": 0.0, "sucursales_distintas": 0}

    def normalize_year_row(r: dict[str, Any]) -> dict[str, Any]:
        return {
            "ingresos_proxy": _float_val(r.get("ingresos_proxy")),
            "tickets": _float_val(r.get("tickets")),
            "presupuesto": _float_val(r.get("presupuesto")),
            "sucursales_distintas": int(r.get("sucursales_distintas") or 0),
        }

    data: list[dict[str, Any]] = []
    if ag == "total":
        by_year: dict[int, dict[str, Any]] = {}
        for r in rows:
            if not isinstance(r, dict):
                continue
            año = int(r.get("año") or 0)
            by_year[año] = normalize_year_row(r)
        ry = by_year.get(y, empty_year_row())
        rp = by_year.get(y_prev, empty_year_row())
        suc = int(ry.get("sucursales_distintas") or 0)
        data.append(
            _fila_informe_ventas(
                grupo="TOTAL",
                ry=ry,
                rp=rp,
                sucursales_en_filtro=suc,
            )
        )
    elif ag == "responsable":
        by_resp: dict[str, dict[int, dict[str, Any]]] = {}
        for r in rows:
            if not isinstance(r, dict):
                continue
            resp = str(r.get("responsable") or "").strip() or "(sin responsable)"
            año = int(r.get("año") or 0)
            by_resp.setdefault(resp, {})[año] = normalize_year_row(r)
        for resp in sorted(by_resp):
            bm = by_resp[resp]
            ry = bm.get(y, empty_year_row())
            rp = bm.get(y_prev, empty_year_row())
            data.append(
                _fila_informe_ventas(
                    grupo=resp, ry=ry, rp=rp, responsable=resp
                )
            )
    else:
        by_branch: dict[int, dict[str, Any]] = {}
        for r in rows:
            if not isinstance(r, dict):
                continue
            bid = int(r.get("branch_office_id") or 0)
            año = int(r.get("año") or 0)
            if bid not in by_branch:
                by_branch[bid] = {
                    "branch_office": r.get("branch_office"),
                    "responsable": r.get("responsable"),
                    "by_year": {},
                }
            by_branch[bid]["by_year"][año] = normalize_year_row(r)
        for bid in sorted(by_branch):
            meta = by_branch[bid]
            bm = meta["by_year"]
            ry = bm.get(y, empty_year_row())
            rp = bm.get(y_prev, empty_year_row())
            data.append(
                _fila_informe_ventas(
                    grupo=str(meta.get("branch_office") or bid),
                    ry=ry,
                    rp=rp,
                    branch_office_id=bid,
                    branch_office=meta.get("branch_office"),
                    responsable=meta.get("responsable"),
                )
            )

    truncated = len(data) > max_out
    data = data[:max_out]

    mes_nom = _INFORME_MESES_ES[m] if 1 <= m <= 12 else str(m)
    alc_label = f"YTD (enero–{mes_nom})" if alc == "ytd" else f"Solo {mes_nom}"
    nota = (
        "Paridad jisreportes.com: **ingresos** = efectivo **neto** + tarjeta **neta** + abonados ($); "
        "presupuesto = suma ppto; Var % = YoY ingresos; Desv % vs PPTO = (ingresos−presupuesto)/presupuesto; "
        "ticket promedio = ingresos/tickets. "
        "(El ranking por volumen del agente usa montos **brutos** — no es el mismo criterio que este informe.) "
        f"**Alcance:** {alc_label} · filas KPI `periodo`={periodo!r}."
    )

    return json.dumps(
        {
            "success": True,
            "source": "mysql",
            "tabla_o_vista": "KPI_INGRESOS_IMG_MES + QRY_BRANCH_OFFICES",
            "mysql_user": db_user,
            "tipo_resultado": "informe_ventas_comparativo",
            "ingresos_criterio": "efectivo_neto + tarjeta_neta + abonados (paridad jisreportes.com)",
            "agrupacion": ag,
            "alcance_temporal": alc,
            "periodo": periodo,
            "year": y,
            "year_anterior": y_prev,
            "month": m,
            "branch_office_id": branch_office_id,
            "responsable_contiene": rc or None,
            "nota": nota,
            "truncated": truncated,
            "count": len(data),
            "data": data,
        },
        default=str,
        ensure_ascii=False,
    )


_MAX_DIAS_VENTAS_DIARIAS = 93
_MAX_FILAS_VENTAS_DIARIAS = 500


@tool
def jis_consultar_ventas_diarias(
    fecha_desde: str,
    fecha_hasta: str,
    metrica: str = "ingresos",
    branch_office_id: int | None = None,
    sucursal_contiene: str | None = None,
) -> str:
    """Informe de ventas **por día** (misma fuente que ventas diarias en jisreportes: KPI_INGRESOS_DIARIO).

    Usar cuando el usuario pide ventas **diarias**, **día a día**, **por fecha**, **una semana**, **rango de fechas**,
    desglose diario de un mes, o comparar días — no cuando solo piden el **total del mes** sin desglose diario
    (para eso suelen bastar jis_obtener_resumen_ejecutivo o jis_ranking_sucursales / jis_consultar_kpi_ingresos).

    Args:
        fecha_desde: Inicio inclusive, formato YYYY-MM-DD.
        fecha_hasta: Fin inclusive, formato YYYY-MM-DD.
        metrica: "ingresos" (default) o "ppto" (presupuesto en filas con metrica ppto en BD).
        branch_office_id: Opcional; filtra una sucursal (id numérico como en APIs).
        sucursal_contiene: Opcional; nombre del local (branch_office) si no tienes el id; debe resolver a una sola activa.
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"success": False, "error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )

    def _parse_day(s: str) -> date | None:
        raw = (s or "").strip()
        if not raw:
            return None
        try:
            return datetime.strptime(raw[:10], "%Y-%m-%d").date()
        except ValueError:
            return None

    d0 = _parse_day(fecha_desde)
    d1 = _parse_day(fecha_hasta)
    if d0 is None or d1 is None:
        return json.dumps(
            {
                "success": False,
                "error": "fechas inválidas; usa YYYY-MM-DD en fecha_desde y fecha_hasta.",
            },
            ensure_ascii=False,
        )
    if d0 > d1:
        d0, d1 = d1, d0
    span = (d1 - d0).days + 1
    if span > _MAX_DIAS_VENTAS_DIARIAS:
        return json.dumps(
            {
                "success": False,
                "error": (
                    f"Rango de {span} días: máximo {_MAX_DIAS_VENTAS_DIARIAS} días por consulta. "
                    "Acorta el periodo o divide la pregunta."
                ),
            },
            ensure_ascii=False,
        )

    met = str(metrica).strip().lower()
    if met in ("ppto", "presupuesto", "meta"):
        met_sql = "ppto"
    else:
        met_sql = "ingresos"

    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)

        bid_filter: str | None = None
        if branch_office_id is not None:
            bid_filter = str(int(branch_office_id))
        elif (sucursal_contiene or "").strip():
            bid_int, err = _resolve_single_branch_id(cur, sucursal_contiene)
            if err:
                cur.close()
                conn.close()
                return json.dumps({"success": False, "error": err}, ensure_ascii=False)
            bid_filter = str(bid_int)

        sql = """
            SELECT
                k.date AS fecha,
                k.branch_office_id,
                bo.branch_office,
                bo.responsable,
                k.cash_amount,
                k.cash_net_amount,
                k.card_amount,
                k.card_net_amount,
                k.subscribers,
                k.ticket_number,
                k.ppto,
                k.metrica
            FROM KPI_INGRESOS_DIARIO k
            LEFT JOIN QRY_BRANCH_OFFICES bo
                ON bo.id = CAST(NULLIF(TRIM(k.branch_office_id), '') AS UNSIGNED)
            WHERE k.periodo = 'Diario'
              AND k.metrica = %s
              AND k.date >= %s
              AND k.date <= %s
        """
        params: list[Any] = [met_sql, d0.isoformat(), d1.isoformat()]
        if bid_filter is not None:
            sql += " AND TRIM(k.branch_office_id) = %s"
            params.append(bid_filter)

        sql += " ORDER BY k.date ASC, k.branch_office_id ASC LIMIT %s"
        params.append(_MAX_FILAS_VENTAS_DIARIAS + 1)

        cur.execute(sql, tuple(params))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        truncated = len(rows) > _MAX_FILAS_VENTAS_DIARIAS
        out_rows = rows[:_MAX_FILAS_VENTAS_DIARIAS] if truncated else rows
        db_user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER") or ""

        return json.dumps(
            {
                "success": True,
                "source": "mysql",
                "tipo_resultado": "ventas_diarias",
                "tabla_o_vista": "KPI_INGRESOS_DIARIO + QRY_BRANCH_OFFICES",
                "mysql_user": db_user,
                "fecha_desde": d0.isoformat(),
                "fecha_hasta": d1.isoformat(),
                "metrica_consulta": met_sql,
                "branch_office_id": int(bid_filter) if bid_filter is not None else None,
                "truncated": truncated,
                "count": len(out_rows),
                "data": out_rows,
            },
            default=str,
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


def _kpi_periodo_tipo(tipo: str) -> str:
    return "Acumulado" if str(tipo).strip().lower() == "acumulado" else "Mensual"


def _resolve_single_branch_id(
    cur: Any, sucursal_contiene: str | None
) -> tuple[int | None, str | None]:
    """Devuelve (id, None) o (None, mensaje_error)."""
    raw = (sucursal_contiene or "").strip()
    if not raw:
        return None, "Indica branch_office_id o sucursal_contiene (nombre del local)."
    cur.execute(
        "SELECT id FROM QRY_BRANCH_OFFICES WHERE status_id = 7 "
        "AND LOWER(branch_office) LIKE LOWER(%s)",
        (f"%{raw}%",),
    )
    found = cur.fetchall()
    if not found:
        return None, f"No hay sucursal activa cuyo nombre coincida con «{raw}»."
    if len(found) > 1:
        return None, (
            f"Hay {len(found)} sucursales que coinciden con «{raw}». "
            "Aclara el nombre o usa branch_office_id."
        )
    return int(found[0]["id"]), None


@tool
def jis_obtener_resumen_ejecutivo(
    year: int,
    month: int,
    tipo_periodo: str = "mensual",
    branch_office_id: int | None = None,
) -> str:
    """Agregados totales de ingresos (sumas) para un mes; misma fuente que el dashboard (KPI_INGRESOS_IMG_MES).

    Usar cuando el usuario pide total, suma, cuánto ganamos, resumen del mes — no listados sucursal a sucursal.

    Args:
        year: Año (ej. 2025).
        month: Mes 1-12.
        tipo_periodo: "mensual" o "acumulado" (misma semántica que jis_consultar_kpi_ingresos).
        branch_office_id: Si se informa, solo esa sucursal activa; si no, todas las activas.
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"success": False, "error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )
    periodo = _kpi_periodo_tipo(tipo_periodo)
    base = """
        SELECT
            COUNT(DISTINCT k.branch_office_id) AS sucursales_en_agregado,
            SUM(COALESCE(k.cash_amount, 0)) AS suma_efectivo_bruto,
            SUM(COALESCE(k.cash_net_amount, 0)) AS suma_efectivo_neto,
            SUM(COALESCE(k.card_amount, 0)) AS suma_tarjeta_bruto,
            SUM(COALESCE(k.card_net_amount, 0)) AS suma_tarjeta_neto,
            SUM(COALESCE(k.subscribers, 0)) AS suma_abonados_monto,
            SUM(COALESCE(k.ticket_number, 0)) AS suma_tickets
        FROM KPI_INGRESOS_IMG_MES k
        INNER JOIN QRY_BRANCH_OFFICES bo ON bo.id = k.branch_office_id AND bo.status_id = 7
        WHERE k.periodo = %s
          AND k.metrica = 'ingresos'
          AND k.año = %s
          AND MONTH(k.date) = %s
    """
    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)
        if branch_office_id is not None:
            q = base + " AND k.branch_office_id = %s"
            cur.execute(q, (periodo, year, month, int(branch_office_id)))
        else:
            cur.execute(base, (periodo, year, month))
        row = cur.fetchone()
        cur.close()
        conn.close()
        db_user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER") or ""
        return json.dumps(
            {
                "success": True,
                "source": "mysql",
                "tabla_o_vista": "KPI_INGRESOS_IMG_MES (agregado)",
                "mysql_user": db_user,
                "periodo": periodo,
                "year": year,
                "month": month,
                "branch_office_id": branch_office_id,
                "data": [row] if row else [],
                "año_consulta": year,
                "nota": (
                    "Solo año indicado (sin mezclar año anterior). Montos KPI: efectivo/tarjeta/abonados; tickets en cantidad. "
                    "Para comparar con año anterior y presupuesto usar jis_informe_ventas_comparativo."
                ),
            },
            default=str,
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


@tool
def jis_ranking_sucursales(
    year: int,
    month: int,
    top_n: int = 5,
    tipo_periodo: str = "mensual",
) -> str:
    """Top sucursales por volumen de ingresos proxy (efectivo bruto + tarjeta bruto + abonados $) en un mes.

    Args:
        year: Año.
        month: Mes 1-12.
        top_n: Cantidad de filas (máximo 50).
        tipo_periodo: "mensual" o "acumulado".
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"success": False, "error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )
    n = min(max(int(top_n) if top_n else 5, 1), 50)
    periodo = _kpi_periodo_tipo(tipo_periodo)
    sql = """
        SELECT
            k.branch_office_id,
            bo.branch_office,
            bo.responsable,
            (COALESCE(k.cash_amount, 0) + COALESCE(k.card_amount, 0) + COALESCE(k.subscribers, 0))
                AS total_proxy_ingresos,
            k.cash_amount,
            k.card_amount,
            k.subscribers,
            k.ticket_number
        FROM KPI_INGRESOS_IMG_MES k
        INNER JOIN QRY_BRANCH_OFFICES bo ON bo.id = k.branch_office_id AND bo.status_id = 7
        WHERE k.periodo = %s
          AND k.metrica = 'ingresos'
          AND k.año = %s
          AND MONTH(k.date) = %s
        ORDER BY total_proxy_ingresos DESC
        LIMIT %s
    """
    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, (periodo, year, month, n))
        rows = cur.fetchall()
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
                "year": year,
                "month": month,
                "criterio_orden": "cash_amount + card_amount + subscribers (proxy ingresos)",
                "count": len(rows),
                "data": rows,
            },
            default=str,
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


@tool
def jis_obtener_evolucion_temporal(
    year: int,
    mes_desde: int = 1,
    mes_hasta: int = 12,
    branch_office_id: int | None = None,
    sucursal_contiene: str | None = None,
    semestre: int | None = None,
) -> str:
    """Serie mensual de KPI de ingresos para una sucursal activa (un punto por mes en el rango).

    Para "primer semestre" / "segundo semestre" usa semestre=1 (meses 1-6) o semestre=2 (7-12).

    Args:
        year: Año calendario.
        mes_desde / mes_hasta: rango inclusive de meses (1-12). Si pasas semestre, se sobreescriben.
        branch_office_id: ID de sucursal (prioridad sobre sucursal_contiene).
        sucursal_contiene: Texto para buscar un único nombre en branch_office (activas).
        semestre: 1 o 2; opcional.
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"success": False, "error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )
    md, mh = int(mes_desde), int(mes_hasta)
    if semestre == 1:
        md, mh = 1, 6
    elif semestre == 2:
        md, mh = 7, 12
    md = max(1, min(12, md))
    mh = max(1, min(12, mh))
    if md > mh:
        md, mh = mh, md

    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)
        bid: int | None = None
        if branch_office_id is not None:
            bid = int(branch_office_id)
        else:
            bid, err = _resolve_single_branch_id(cur, sucursal_contiene)
            if err:
                cur.close()
                conn.close()
                return json.dumps({"success": False, "error": err}, ensure_ascii=False)

        sql = """
            SELECT
                MONTH(k.date) AS mes,
                k.branch_office_id,
                bo.branch_office,
                bo.responsable,
                k.cash_amount,
                k.cash_net_amount,
                k.card_amount,
                k.card_net_amount,
                k.subscribers,
                k.ticket_number
            FROM KPI_INGRESOS_IMG_MES k
            INNER JOIN QRY_BRANCH_OFFICES bo ON bo.id = k.branch_office_id AND bo.status_id = 7
            WHERE k.periodo = 'Mensual'
              AND k.metrica = 'ingresos'
              AND k.año = %s
              AND MONTH(k.date) BETWEEN %s AND %s
              AND k.branch_office_id = %s
            ORDER BY MONTH(k.date)
        """
        cur.execute(sql, (year, md, mh, bid))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        db_user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER") or ""
        return json.dumps(
            {
                "success": True,
                "source": "mysql",
                "tabla_o_vista": "KPI_INGRESOS_IMG_MES + QRY_BRANCH_OFFICES",
                "mysql_user": db_user,
                "year": year,
                "mes_desde": md,
                "mes_hasta": mh,
                "branch_office_id": bid,
                "count": len(rows),
                "data": rows,
            },
            default=str,
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


# Estados en QRY_REPORTE_DEPOSITOS (literales legacy / jisreportes; no pasar texto arbitrario del usuario al SQL).
_ESTADOS_DEPOSITO_CANON: tuple[str, ...] = (
    "Pendiente",
    "Depositado con Diferencia",
    "Depositado a Favor",
    "Depositado Correcto",
)

_MAX_FILAS_DEPOSITOS = 500
_MAX_RANGO_DIAS_DEPOSITOS = 366
# Misma collation que la conexión (_db_params); evita 1267 al comparar con columnas en utf8mb4_0900_ai_ci.
_DEPOSITOS_STRING_COLLATE = "utf8mb4_unicode_ci"


def _parse_iso_date_depositos(s: str | None) -> date | None:
    raw = (s or "").strip()
    if not raw:
        return None
    try:
        return datetime.strptime(raw[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def _coerce_estado_deposito(value: str | None) -> str | None:
    if value is None or not str(value).strip():
        return None
    v = str(value).strip()
    for canon in _ESTADOS_DEPOSITO_CANON:
        if v.lower() == canon.lower():
            return canon
    return "__invalid__"


def _sql_excluir_oficina(excluir: bool) -> tuple[str, list[Any]]:
    if not excluir:
        return "", []
    c = _DEPOSITOS_STRING_COLLATE
    return (
        f" AND UPPER(COALESCE(d.Sucursal, '') COLLATE {c}) NOT LIKE %s",
        ["%OFICINA%"],
    )


def _coerce_excluir_oficina(value: Any, default: bool = True) -> bool:
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


def _depositos_append_filtros_columnas(
    conds: list[str],
    params: list[Any],
    fa: dict[str, Any],
    *,
    est: str | None,
    branch_office_id: int | None,
    sucursal_contiene: str | None,
    supervisor_contiene: str | None,
    responsable_contiene: str | None,
) -> None:
    """Filtros comunes listado/resumen sobre QRY_REPORTE_DEPOSITOS (alias d.)."""
    c = _DEPOSITOS_STRING_COLLATE
    if est:
        conds.append(f"d.Estado_Deposito COLLATE {c} = %s")
        params.append(est)
        fa["estado_deposito"] = est
    if branch_office_id is not None:
        conds.append("d.branch_office_id = %s")
        params.append(int(branch_office_id))
        fa["branch_office_id"] = int(branch_office_id)
    suc = (sucursal_contiene or "").strip()
    if suc:
        conds.append(f"d.Sucursal COLLATE {c} LIKE %s")
        params.append(f"%{suc}%")
        fa["sucursal_contiene"] = suc
    sup = (supervisor_contiene or "").strip()
    if sup:
        conds.append(f"d.Supervisor COLLATE {c} LIKE %s")
        params.append(f"%{sup}%")
        fa["supervisor_contiene"] = sup
    resp = (responsable_contiene or "").strip()
    if resp:
        conds.append(f"d.Supervisor COLLATE {c} LIKE %s")
        params.append(f"%{resp}%")
        fa["responsable_contiene"] = resp


@tool
def jis_consultar_depositos(
    fecha_recaudacion_desde: str | None = None,
    fecha_recaudacion_hasta: str | None = None,
    year: int | None = None,
    month: int | None = None,
    estado_deposito: str | None = None,
    branch_office_id: int | None = None,
    sucursal_contiene: str | None = None,
    supervisor_contiene: str | None = None,
    responsable_contiene: str | None = None,
    excluir_sucursal_oficina: bool | None = True,
) -> str:
    """Listado de depósitos / recaudación desde **QRY_REPORTE_DEPOSITOS** (paridad reportes jisreportes).

    Usar cuando piden depósitos **pendientes**, **con diferencia**, listado por **sucursal** o **supervisor**,
    o movimientos en un **rango de fechas** (fecha de recaudación).

    Args:
        fecha_recaudacion_desde / fecha_recaudacion_hasta: YYYY-MM-DD (inclusive) sobre **Fecha_Recaudacion**.
            Si no vienen, podés usar **year** + **month** (mes calendario completo).
        year + month: Mes de recaudación 1-12; se usa solo si faltan las dos fechas ISO.
        estado_deposito: Opcional; valor **exacto** permitido: Pendiente | Depositado con Diferencia |
            Depositado a Favor | Depositado Correcto (mayúsculas como en la vista).
        branch_office_id: Filtro por id de sucursal.
        sucursal_contiene: LIKE sobre columna **Sucursal** (nombre del local en la vista).
        supervisor_contiene: LIKE sobre **Supervisor** (supervisor comercial en la vista; legacy “responsable”).
        responsable_contiene: Igual que **supervisor_contiene** (sinónimo para preguntas “por responsable”).
        excluir_sucursal_oficina: True (default) alinea al KPI legacy que excluye filas cuyo nombre de sucursal
            contiene «OFICINA».
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"success": False, "error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )

    d0 = _parse_iso_date_depositos(fecha_recaudacion_desde)
    d1 = _parse_iso_date_depositos(fecha_recaudacion_hasta)
    if d0 is None and d1 is None and year is not None and month is not None:
        y, m = int(year), int(month)
        if not (1 <= m <= 12):
            return json.dumps({"success": False, "error": "month debe estar entre 1 y 12."}, ensure_ascii=False)
        d0 = date(y, m, 1)
        d1 = date(y, m, monthrange(y, m)[1])
    if d0 is None or d1 is None:
        return json.dumps(
            {
                "success": False,
                "error": (
                    "Indica periodo: fecha_recaudacion_desde y fecha_recaudacion_hasta (YYYY-MM-DD), "
                    "o year y month (mes calendario)."
                ),
            },
            ensure_ascii=False,
        )
    if d0 > d1:
        d0, d1 = d1, d0
    span = (d1 - d0).days + 1
    if span > _MAX_RANGO_DIAS_DEPOSITOS:
        return json.dumps(
            {
                "success": False,
                "error": (
                    f"Rango de {span} días: máximo {_MAX_RANGO_DIAS_DEPOSITOS} días. "
                    "Acorta el periodo o divide la consulta."
                ),
            },
            ensure_ascii=False,
        )

    est = _coerce_estado_deposito(estado_deposito)
    if est == "__invalid__":
        return json.dumps(
            {
                "success": False,
                "error": (
                    f"estado_deposito inválido. Valores permitidos: {', '.join(_ESTADOS_DEPOSITO_CANON)}."
                ),
            },
            ensure_ascii=False,
        )

    excluir = _coerce_excluir_oficina(excluir_sucursal_oficina, default=True)
    sql_excl, params_excl = _sql_excluir_oficina(excluir)

    conds: list[str] = [
        "d.Fecha_Recaudacion IS NOT NULL",
        "d.Fecha_Recaudacion >= %s",
        "d.Fecha_Recaudacion <= %s",
    ]
    params: list[Any] = [d0.isoformat(), d1.isoformat()]

    fa_cols: dict[str, Any] = {}
    _depositos_append_filtros_columnas(
        conds,
        params,
        fa_cols,
        est=est,
        branch_office_id=branch_office_id,
        sucursal_contiene=sucursal_contiene,
        supervisor_contiene=supervisor_contiene,
        responsable_contiene=responsable_contiene,
    )

    c = _DEPOSITOS_STRING_COLLATE
    where_rest = " AND ".join(conds)
    query = (
        f"SELECT d.* FROM QRY_REPORTE_DEPOSITOS d WHERE {where_rest}"
        f"{sql_excl} ORDER BY d.Fecha_Recaudacion DESC, d.Sucursal COLLATE {c} ASC LIMIT %s"
    )
    params.extend(params_excl)
    params.append(_MAX_FILAS_DEPOSITOS + 1)

    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)
        cur.execute(query, tuple(params))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        truncated = len(rows) > _MAX_FILAS_DEPOSITOS
        out_rows = rows[:_MAX_FILAS_DEPOSITOS] if truncated else rows
        db_user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER") or ""
        fa: dict[str, Any] = {
            "fecha_recaudacion_desde": d0.isoformat(),
            "fecha_recaudacion_hasta": d1.isoformat(),
            "excluir_sucursal_oficina": excluir,
            **fa_cols,
        }
        return json.dumps(
            {
                "success": True,
                "source": "mysql",
                "tipo_resultado": "depositos_listado",
                "tabla_o_vista": "QRY_REPORTE_DEPOSITOS",
                "mysql_user": db_user,
                "estados_validos": list(_ESTADOS_DEPOSITO_CANON),
                "filtros_aplicados": fa,
                "truncated": truncated,
                "count": len(out_rows),
                "data": out_rows,
            },
            default=str,
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)


@tool
def jis_resumen_depositos(
    year: int | None = None,
    month: int | None = None,
    fecha_recaudacion_desde: str | None = None,
    fecha_recaudacion_hasta: str | None = None,
    estado_deposito: str | None = None,
    branch_office_id: int | None = None,
    sucursal_contiene: str | None = None,
    supervisor_contiene: str | None = None,
    responsable_contiene: str | None = None,
    excluir_sucursal_oficina: bool | None = True,
) -> str:
    """Resumen agregado de depósitos (Fecha_Recaudacion), vista **QRY_REPORTE_DEPOSITOS**.

    Alineado a KPI legacy jisreportes (totales, suma diferencias, latencia, desglose por estado). Permite el mismo
    corte que el listado: **sucursal**, **supervisor/responsable**, **estado**, rango de fechas o mes calendario.

    Args:
        year + month: Mes calendario de recaudación (1-12). Usar si no pasás fechas ISO explícitas.
        fecha_recaudacion_desde / fecha_recaudacion_hasta: YYYY-MM-DD inclusive; si vienen ambas válidas,
            tienen prioridad sobre year/month (máximo 366 días).
        estado_deposito: Opcional; mismo conjunto canónico que **jis_consultar_depositos**.
        branch_office_id, sucursal_contiene: filtro sucursal.
        supervisor_contiene / responsable_contiene: LIKE sobre **Supervisor** (responsable comercial en la vista).
        excluir_sucursal_oficina: True (default) = excluye sucursales cuyo nombre contiene OFICINA.
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"success": False, "error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )

    d0 = _parse_iso_date_depositos(fecha_recaudacion_desde)
    d1 = _parse_iso_date_depositos(fecha_recaudacion_hasta)
    if d0 is None or d1 is None:
        if year is None or month is None:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        "Indica periodo: year y month (mes calendario), o "
                        "fecha_recaudacion_desde y fecha_recaudacion_hasta (YYYY-MM-DD)."
                    ),
                },
                ensure_ascii=False,
            )
        y, m = int(year), int(month)
        if not (1 <= m <= 12):
            return json.dumps({"success": False, "error": "month debe estar entre 1 y 12."}, ensure_ascii=False)
        d0 = date(y, m, 1)
        d1 = date(y, m, monthrange(y, m)[1])
        y_out, m_out = y, m
        periodo_por_mes_calendario = True
    else:
        y_out = d0.year
        m_out = d0.month
        periodo_por_mes_calendario = False
        if d0 > d1:
            d0, d1 = d1, d0
        span = (d1 - d0).days + 1
        if span > _MAX_RANGO_DIAS_DEPOSITOS:
            return json.dumps(
                {
                    "success": False,
                    "error": (
                        f"Rango de {span} días: máximo {_MAX_RANGO_DIAS_DEPOSITOS} días. "
                        "Acorta el periodo o usa year+month."
                    ),
                },
                ensure_ascii=False,
            )

    est = _coerce_estado_deposito(estado_deposito)
    if est == "__invalid__":
        return json.dumps(
            {
                "success": False,
                "error": (
                    f"estado_deposito inválido. Valores permitidos: {', '.join(_ESTADOS_DEPOSITO_CANON)}."
                ),
            },
            ensure_ascii=False,
        )

    excluir = _coerce_excluir_oficina(excluir_sucursal_oficina, default=True)
    sql_excl, params_excl = _sql_excluir_oficina(excluir)

    conds: list[str] = [
        "d.Fecha_Recaudacion IS NOT NULL",
        "d.Fecha_Recaudacion >= %s",
        "d.Fecha_Recaudacion <= %s",
    ]
    params_base: list[Any] = [d0.isoformat(), d1.isoformat()]
    fa: dict[str, Any] = {
        "fecha_recaudacion_desde": d0.isoformat(),
        "fecha_recaudacion_hasta": d1.isoformat(),
        "excluir_sucursal_oficina": excluir,
    }
    _depositos_append_filtros_columnas(
        conds,
        params_base,
        fa,
        est=est if est else None,
        branch_office_id=branch_office_id,
        sucursal_contiene=sucursal_contiene,
        supervisor_contiene=supervisor_contiene,
        responsable_contiene=responsable_contiene,
    )
    base_where = " AND ".join(conds) + sql_excl
    params_base.extend(params_excl)

    c = _DEPOSITOS_STRING_COLLATE
    # Latencia “seguimiento”: mismo criterio que reportes/PDF legacy (excluye depósitos ya “al día”).
    sql_totals = f"""
        SELECT
            COUNT(*) AS total_registros,
            SUM(d.Diferencia) AS suma_diferencia,
            SUM(d.Monto_Recaudado) AS suma_monto_recaudado,
            SUM(d.Monto_Depositado) AS suma_monto_depositado,
            AVG(d.Dias_Latencia) AS promedio_dias_latencia,
            AVG(
                CASE
                    WHEN d.Estado_Deposito COLLATE {c} NOT IN ('Depositado Correcto', 'Depositado a Favor')
                    THEN d.Dias_Latencia
                END
            ) AS promedio_dias_latencia_seguimiento
        FROM QRY_REPORTE_DEPOSITOS d
        WHERE {base_where}
    """
    sql_por_estado = f"""
        SELECT (d.Estado_Deposito COLLATE {c}) AS estado, COUNT(*) AS cantidad
        FROM QRY_REPORTE_DEPOSITOS d
        WHERE {base_where}
        GROUP BY (d.Estado_Deposito COLLATE {c})
        ORDER BY cantidad DESC
    """

    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)
        cur.execute(sql_totals, tuple(params_base))
        agg = cur.fetchone()
        cur.execute(sql_por_estado, tuple(params_base))
        por_estado_rows = cur.fetchall()
        cur.close()
        conn.close()
        db_user = os.getenv("DB_USER") or os.getenv("DB_READONLY_USER") or ""
        por_estado: list[dict[str, Any]] = []
        for r in por_estado_rows or []:
            if isinstance(r, dict):
                por_estado.append(
                    {
                        "estado": r.get("estado"),
                        "cantidad": int(r.get("cantidad") or 0),
                    }
                )
        agg_dict = agg if isinstance(agg, dict) else {}
        return json.dumps(
            {
                "success": True,
                "source": "mysql",
                "tipo_resultado": "depositos_resumen",
                "tabla_o_vista": "QRY_REPORTE_DEPOSITOS",
                "mysql_user": db_user,
                "year": y_out,
                "month": m_out,
                "periodo_por_mes_calendario": periodo_por_mes_calendario,
                "filtros_aplicados": fa,
                "fecha_recaudacion_desde": d0.isoformat(),
                "fecha_recaudacion_hasta": d1.isoformat(),
                "excluir_sucursal_oficina": excluir,
                "total_registros": int(agg_dict.get("total_registros") or 0),
                "suma_diferencia": agg_dict.get("suma_diferencia"),
                "suma_monto_recaudado": agg_dict.get("suma_monto_recaudado"),
                "suma_monto_depositado": agg_dict.get("suma_monto_depositado"),
                "promedio_dias_latencia": agg_dict.get("promedio_dias_latencia"),
                "promedio_dias_latencia_seguimiento": agg_dict.get("promedio_dias_latencia_seguimiento"),
                "por_estado": por_estado,
            },
            default=str,
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps({"success": False, "error": str(e)}, ensure_ascii=False)
