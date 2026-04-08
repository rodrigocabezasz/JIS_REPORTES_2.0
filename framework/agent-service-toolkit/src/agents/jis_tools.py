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


@tool
def jis_listar_sucursales() -> str:
    """Lista sucursales activas: id, nombre, responsable, dirección, zona, región.

    Misma consulta que get_all_sucursales en el backend legacy (vista QRY_BRANCH_OFFICES, status_id=7).
    """
    miss = _missing_db_config()
    if miss:
        return json.dumps(
            {"error": "Faltan variables de entorno", "variables": miss},
            ensure_ascii=False,
        )
    query = (
        "SELECT responsable, (id*1) as branch_office_id, branch_office, dte_code, "
        "principal AS marca, zone AS zona, segment AS segmento, address AS direccion, "
        "region, commune FROM QRY_BRANCH_OFFICES WHERE status_id = 7"
    )
    try:
        conn = mysql.connector.connect(**_db_params())
        cur = conn.cursor(dictionary=True)
        cur.execute(query)
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return json.dumps(
            {"success": True, "count": len(rows), "data": rows},
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
        return json.dumps(
            {
                "success": True,
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
