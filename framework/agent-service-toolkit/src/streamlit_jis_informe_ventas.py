"""Presentación en Streamlit del JSON de `jis_informe_ventas_comparativo` (solo canal chat / LLM)."""

from __future__ import annotations

import json
from typing import Any

import pandas as pd
import streamlit as st

INFORME_TOOL_NAME = "jis_informe_ventas_comparativo"
# Debe coincidir con el encabezado del markdown que genera `after_tools` en jis_reports_agent.py
INFORME_MARKDOWN_PREFIX = "**Informe de ventas**"

_MESES = (
    "",
    "ene.",
    "feb.",
    "mar.",
    "abr.",
    "may.",
    "jun.",
    "jul.",
    "ago.",
    "sep.",
    "oct.",
    "nov.",
    "dic.",
)


def parse_informe_ventas_payload(content: str) -> dict[str, Any] | None:
    try:
        d = json.loads(content)
    except (json.JSONDecodeError, TypeError):
        return None
    if not isinstance(d, dict):
        return None
    if d.get("tipo_resultado") != "informe_ventas_comparativo":
        return None
    return d


def _fmt_money(v: Any) -> str:
    if v is None:
        return "—"
    try:
        n = int(round(float(v)))
    except (TypeError, ValueError):
        return "—"
    return "$" + f"{n:,}".replace(",", ".")


def _fmt_pct(v: Any) -> str:
    if v is None:
        return "—"
    try:
        if isinstance(v, float) and pd.isna(v):
            return "—"
    except (TypeError, ValueError):
        pass
    try:
        return f"{float(v):.2f} %"
    except (TypeError, ValueError):
        return "—"


def _fmt_num(v: Any) -> str:
    if v is None:
        return "—"
    try:
        if isinstance(v, float) and pd.isna(v):
            return "—"
    except (TypeError, ValueError):
        pass
    try:
        n = int(round(float(v)))
    except (TypeError, ValueError):
        return "—"
    return f"{n:,}".replace(",", ".")


def _is_missing_cell(v: Any) -> bool:
    if v is None:
        return True
    try:
        return bool(pd.isna(v))
    except (ValueError, TypeError):
        return False


def _safe_money(v: Any) -> str:
    return "—" if _is_missing_cell(v) else _fmt_money(v)


def _safe_pct(v: Any) -> str:
    if _is_missing_cell(v):
        return "—"
    return _fmt_pct(v)


def _safe_num(v: Any) -> str:
    return "—" if _is_missing_cell(v) else _fmt_num(v)


def _format_informe_detalle_dataframe(df: pd.DataFrame, y: Any, yp: Any) -> pd.DataFrame:
    """Montos y % legibles (estilo CL: $ con miles por punto)."""
    out = df.copy()
    for col in (f"Ingresos {y}", f"Ingresos {yp}", "Presupuesto", "T. prom."):
        if col in out.columns:
            out[col] = out[col].map(_safe_money)
    for col in ("Var %", "Desv % vs ppto"):
        if col in out.columns:
            out[col] = out[col].map(_safe_pct)
    for col in (f"Tickets {y}", f"Tickets {yp}"):
        if col in out.columns:
            out[col] = out[col].map(_safe_num)
    return out


def render_informe_ventas_report(payload: dict[str, Any]) -> None:
    """Resumen con `st.metric` o tabla con `st.dataframe` (información densa, sin imitar dashboards web)."""
    y = payload.get("year", "")
    yp = payload.get("year_anterior", "")
    m = int(payload.get("month") or 0)
    mes = _MESES[m] if 1 <= m <= 12 else str(m)
    alc = str(payload.get("alcance_temporal", "mes"))
    p = payload.get("periodo", "")
    agr = str(payload.get("agrupacion", "total"))

    alc_txt = f"Acumulado ene.–{mes}" if alc == "ytd" else f"Mes {mes}"
    st.markdown(
        f"##### Informe de ventas · {y} vs {yp} · {alc_txt} · `{p}` · **{agr}**",
        help="MySQL KPI_INGRESOS_IMG_MES. Ingresos = efectivo neto + tarjeta neta + abonados.",
    )

    rows = payload.get("data") or []
    if not isinstance(rows, list) or not rows:
        st.info("Sin filas en el informe.")
        return

    if agr == "total":
        r = rows[0] if isinstance(rows[0], dict) else {}
        if not r:
            return
        row1 = st.columns(4)
        row2 = st.columns(4)
        with row1[0]:
            st.metric(f"Ingresos {y}", _fmt_money(r.get("ingresos_proxy_año_actual")), help="Periodo actual")
        with row1[1]:
            st.metric(f"Ingresos {yp}", _fmt_money(r.get("ingresos_proxy_año_anterior")), help="Periodo anterior")
        with row1[2]:
            st.metric("Presupuesto (meta)", _fmt_money(r.get("presupuesto_año_actual")))
        with row1[3]:
            st.metric("Sucursales", _fmt_num(r.get("sucursales_en_filtro")))
        with row2[0]:
            st.metric("Var % vs año ant.", _fmt_pct(r.get("var_pct_ingresos_yoy")), help="YoY ingresos")
        with row2[1]:
            st.metric("Desv % vs PPTO", _fmt_pct(r.get("desv_pct_ingresos_vs_presupuesto")), help="Cumplimiento")
        with row2[2]:
            st.metric("Ticket promedio", _fmt_money(r.get("ticket_promedio_año_actual")))
        with row2[3]:
            st.metric(
                f"Tickets {y} / {yp}",
                f"{_fmt_num(r.get('tickets_año_actual'))} / {_fmt_num(r.get('tickets_año_anterior'))}",
            )
        return

    records: list[dict[str, Any]] = [x for x in rows if isinstance(x, dict)]
    if not records:
        return

    df = pd.DataFrame(records)
    rename = {
        "grupo": "Grupo",
        "branch_office_id": "ID",
        "branch_office": "Sucursal",
        "responsable": "Responsable",
        "ingresos_proxy_año_actual": f"Ingresos {y}",
        "ingresos_proxy_año_anterior": f"Ingresos {yp}",
        "var_pct_ingresos_yoy": "Var %",
        "presupuesto_año_actual": "Presupuesto",
        "desv_pct_ingresos_vs_presupuesto": "Desv % vs ppto",
        "tickets_año_actual": f"Tickets {y}",
        "tickets_año_anterior": f"Tickets {yp}",
        "ticket_promedio_año_actual": "T. prom.",
    }
    base_metrics = [
        "ingresos_proxy_año_actual",
        "ingresos_proxy_año_anterior",
        "var_pct_ingresos_yoy",
        "presupuesto_año_actual",
        "desv_pct_ingresos_vs_presupuesto",
        "tickets_año_actual",
        "tickets_año_anterior",
        "ticket_promedio_año_actual",
    ]
    if agr == "sucursal" and "branch_office" in df.columns:
        leader = ["branch_office_id", "branch_office", "responsable"]
    elif agr == "responsable":
        leader = ["grupo"]
    else:
        leader = ["grupo"]
    cols_order = [c for c in leader if c in df.columns] + [c for c in base_metrics if c in df.columns]
    df = df[cols_order].rename(columns=rename)
    df = _format_informe_detalle_dataframe(df, y, yp)
    st.caption("Tabla detalle; montos en pesos (CL). Ordená columnas desde los encabezados.")
    st.dataframe(df, use_container_width=True, hide_index=True)


def should_fold_informe_markdown(content: str) -> bool:
    c = (content or "").strip()
    return bool(c.startswith(INFORME_MARKDOWN_PREFIX))
