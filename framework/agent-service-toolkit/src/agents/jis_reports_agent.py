"""Agente JIS Reportes: solo herramientas de datos internos (MySQL), sin búsqueda web."""

import json
import re
import uuid
from datetime import datetime
from typing import Any, Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig, RunnableLambda, RunnableSerializable
from langgraph.graph import END, MessagesState, StateGraph
from langgraph.managed import RemainingSteps
from langgraph.prebuilt import ToolNode

from agents.jis_tools import jis_consultar_kpi_ingresos, jis_listar_sucursales
from agents.safeguard import Safeguard, SafeguardOutput, SafetyAssessment
from core import get_model, settings


class AgentState(MessagesState, total=False):
    safety: SafeguardOutput
    remaining_steps: RemainingSteps


tools = [jis_listar_sucursales, jis_consultar_kpi_ingresos]

_TOOL_NAMES = frozenset(t.name for t in tools)

current_date = datetime.now().strftime("%d/%m/%Y")
instructions = f"""
Eres el asistente de gestión de JIS PARKING (jisreportes). Fecha de hoy: {current_date}.

Tienes herramientas para:
- Listar sucursales activas con responsables y direcciones.
- Consultar KPI de ingresos por mes (vista mensual o acumulada), opcionalmente por sucursal.

Idioma (obligatorio):
- Todas las respuestas al usuario deben estar en español (Chile o neutro). No uses inglés ni mezclas.
- Si en el historial hay texto en inglés, ignóralo como referencia de idioma: tú respondes siempre en español.

Uso correcto de herramientas (evita confusiones):
- jis_listar_sucursales: filtros opcionales (no pidas año ni mes). Pregunta del usuario en español → argumento
  de la tool (columna real en MySQL entre paréntesis):
  - responsable / persona → responsable_contiene. Nombre largo (3+ palabras) = mismo criterio que Navicat
    (`LIKE '%frase%'`). Dos palabras tipo "david gomez" = ambas deben aparecer en el nombre completo.
  - sucursal / local / nombre del punto → sucursal_contiene (branch_office)
  - región → region_contiene (region)
  - comuna → comuna_contiene (commune; el usuario dice “comuna”, no “commune”)
  - zona → zona_contiene (zone)
  - segmento / tipo de negocio → segmento_contiene (segment)
  - marca / cadena / principal → principal_contiene (principal)
  - dirección / calle / direccion → direccion_contiene (address)
  - solo_activas: por defecto true (solo status_id = 7). Si preguntan "cuántas sucursales tiene" un
    responsable o quieren todas las asignadas aunque no estén activas, usa solo_activas=false; la tabla
    incluirá la columna status_id para distinguir.
  Puedes combinar varios filtros si el usuario acota (ej. región + comuna). Búsqueda parcial, sin mayúsculas.
  Listado completo → sin filtros o argumentos null.
- jis_consultar_kpi_ingresos: SÍ requiere tipo_vista (“mensual” o “acumulado”), year y month. Solo entonces
  pregunta año/mes si faltan. No mezcles requisitos del KPI con el listado de sucursales.

Reglas generales:
- Usa siempre las herramientas del sistema (function calling); no escribas en el texto bloques JSON
  con "name" / "arguments" como sustituto de una llamada real.
- Claro y conciso para gerencia, siempre en español.

Datos reales (obligatorio, anti-alucinación):
- Tras cada herramienta recibes un JSON en un mensaje de sistema/herramienta. Esa salida es la ÚNICA fuente
  de verdad. Cada cifra, nombre de sucursal, responsable y dirección DEBE coincidir literalmente con los
  campos del JSON (p. ej. branch_office, responsable, direccion, region, commune, branch_office_id).
- PROHIBIDO inventar o “ejemplificar”: no uses nombres genéricos (Juan Pérez, Sucursal Centro, Ciudad A,
  Calle Principal 123, etc.) salvo que aparezcan exactamente en el JSON.
- Si el JSON trae "success": false o "error", explica el error al usuario; no sustituyas con datos ficticios.
- Si "count" es 0 o "data" es [], di que no hay registros; no inventes filas.
- Al listar sucursales, el número de ítems en tu respuesta debe ser exactamente el de "data" (o el valor
  de "count" si viene). Menciona el total (count) al inicio.
- Para KPI de ingresos, solo valores y filas presentes en "data"; indica si hubo truncado.

Presentación:
- El usuario no necesita el JSON crudo: convierte filas en listas o tablas legibles, pero sin cambiar valores.
- Si el JSON de la herramienta incluye "source" / "tabla_o_vista", puedes mencionarlo en una frase
  breve para dejar claro que los datos vienen de MySQL (misma fuente que Navicat con reader_user).
"""


def _json_candidates_from_text(text: str) -> list[str]:
    text = text.strip()
    found: list[str] = [text]
    found.extend(m.group(1).strip() for m in re.finditer(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE))
    # Qwen/Ollama a veces emiten la tool como texto: <tool_response>{"name":...}</tool_response>
    for pat in (
        r"<tool_response>\s*([\s\S]*?)\s*</tool_response>",
        r"<tool_call>\s*([\s\S]*?)\s*</tool_call>",
    ):
        found.extend(m.group(1).strip() for m in re.finditer(pat, text, re.IGNORECASE))
    return [c for c in found if c]


def _tool_calls_from_json_obj(obj: Any) -> list[dict[str, Any]]:
    items = obj if isinstance(obj, list) else [obj]
    out: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        name = item.get("name")
        if name not in _TOOL_NAMES:
            continue
        args = item.get("arguments", item.get("args", {}))
        if isinstance(args, str):
            try:
                args = json.loads(args) if args.strip() else {}
            except json.JSONDecodeError:
                args = {}
        if not isinstance(args, dict):
            args = {}
        out.append(
            {
                "name": name,
                "args": args,
                "id": f"call_{uuid.uuid4().hex[:24]}",
                "type": "tool_call",
            }
        )
    return out


_LISTAR_TOOL = "jis_listar_sucursales"
_MAX_SUCURSALES_TABLA = 400


def _md_cell(value: Any) -> str:
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").strip()


def _tool_is_listar_sucursales(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _LISTAR_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return isinstance(p, dict) and p.get("tabla_o_vista") == "QRY_BRANCH_OFFICES"


def _format_sucursales_respuesta_es(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        rows = []
    count = int(payload.get("count", len(rows)))
    vista = payload.get("tabla_o_vista", "QRY_BRANCH_OFFICES")
    filtro = payload.get("filtro", "status_id = 7")
    user = payload.get("mysql_user", "")
    intro = (
        f"**Datos desde MySQL** (vista `{vista}`, filtro `{filtro}`"
        f"{f', usuario `{user}`' if user else ''}). "
        f"**Total de sucursales:** {count}.\n\n"
    )
    if count == 0 or not rows:
        solo_act = payload.get("solo_activas", True)
        vacio = (
            "No hay sucursales que coincidan con el filtro."
            if solo_act is False
            else "No hay sucursales activas que coincidan con el filtro."
        )
        msg = intro + vacio
        fa = payload.get("filtros_aplicados") or {}
        if isinstance(fa, dict) and fa:
            msg += (
                "\n\n*Sugerencia:* prueba con solo nombre o solo apellido, o variante sin tilde "
                "(p. ej. Gomez / Gómez), según cómo esté guardado en la base."
            )
        return msg

    show = rows[:_MAX_SUCURSALES_TABLA]
    truncated = len(rows) > _MAX_SUCURSALES_TABLA
    headers = ["ID", "Nombre", "Responsable", "Dirección", "Región", "Comuna", "Marca", "Zona"]
    keys: list[str] = [
        "branch_office_id",
        "branch_office",
        "responsable",
        "direccion",
        "region",
        "commune",
        "marca",
        "zona",
    ]
    if rows and isinstance(rows[0], dict) and "status_id" in rows[0]:
        headers.append("status_id")
        keys.append("status_id")
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    head = "| " + " | ".join(headers) + " |"
    lines = [intro, head, sep]
    for r in show:
        if not isinstance(r, dict):
            continue
        lines.append("| " + " | ".join(_md_cell(r.get(k)) for k in keys) + " |")
    out = "\n".join(lines)
    if truncated:
        out += f"\n\n*(Se muestran las primeras {_MAX_SUCURSALES_TABLA} de {count}; el resto sigue en la base.)*"
    return out


async def after_tools(state: AgentState, config: RunnableConfig) -> AgentState:
    """Tras ejecutar tools: si fue listar sucursales con éxito, respuesta fija desde MySQL (sin LLM)."""
    last = state["messages"][-1]
    if not isinstance(last, ToolMessage) or not _tool_is_listar_sucursales(last):
        return {}
    try:
        payload = json.loads(last.content) if isinstance(last.content, str) else json.loads(str(last.content))
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(payload, dict) or not payload.get("success"):
        return {}
    text = _format_sucursales_respuesta_es(payload)
    return {"messages": [AIMessage(content=text)]}


def route_after_tools(state: AgentState) -> Literal["model", "end"]:
    msgs = state["messages"]
    if len(msgs) < 2:
        return "model"
    last, prev = msgs[-1], msgs[-2]
    if isinstance(last, AIMessage) and not last.tool_calls and isinstance(prev, ToolMessage):
        if _tool_is_listar_sucursales(prev):
            try:
                p = json.loads(prev.content) if isinstance(prev.content, str) else json.loads(str(prev.content))
            except (json.JSONDecodeError, TypeError):
                return "model"
            if isinstance(p, dict) and p.get("success"):
                return "end"
    return "model"


def coerce_ollama_text_tool_calls(message: AIMessage) -> AIMessage:
    """Ollama/Qwen a veces devuelve la invocación como texto JSON sin rellenar tool_calls."""
    if message.tool_calls:
        return message
    raw = message.content
    if not isinstance(raw, str) or not raw.strip():
        return message
    for candidate in _json_candidates_from_text(raw):
        try:
            data = json.loads(candidate)
        except json.JSONDecodeError:
            continue
        tool_calls = _tool_calls_from_json_obj(data)
        if tool_calls:
            return AIMessage(
                content="",
                tool_calls=tool_calls,
                id=message.id,
                response_metadata=message.response_metadata,
            )
    return message


def wrap_model(model: BaseChatModel) -> RunnableSerializable[AgentState, AIMessage]:
    bound_model = model.bind_tools(tools)
    preprocessor = RunnableLambda(
        lambda state: [SystemMessage(content=instructions)] + state["messages"],
        name="StateModifier",
    )
    return preprocessor | bound_model  # type: ignore[return-value]


def format_safety_message(safety: SafeguardOutput) -> AIMessage:
    content = (
        f"Este mensaje fue bloqueado por políticas de seguridad: {', '.join(safety.unsafe_categories)}"
    )
    return AIMessage(content=content)


async def acall_model(state: AgentState, config: RunnableConfig) -> AgentState:
    m = get_model(config["configurable"].get("model", settings.DEFAULT_MODEL))
    model_runnable = wrap_model(m)
    response = await model_runnable.ainvoke(state, config)
    response = coerce_ollama_text_tool_calls(response)

    if state["remaining_steps"] < 2 and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="No alcanzaron pasos para completar la consulta. Intenta de nuevo.",
                )
            ]
        }
    return {"messages": [response]}


async def safeguard_input(state: AgentState, config: RunnableConfig) -> AgentState:
    safeguard = Safeguard()
    safety_output = await safeguard.ainvoke(state["messages"])
    return {"safety": safety_output, "messages": []}


async def block_unsafe_content(state: AgentState, config: RunnableConfig) -> AgentState:
    safety: SafeguardOutput = state["safety"]
    return {"messages": [format_safety_message(safety)]}


agent = StateGraph(AgentState)
agent.add_node("model", acall_model)
agent.add_node("tools", ToolNode(tools))
agent.add_node("after_tools", after_tools)
agent.add_node("guard_input", safeguard_input)
agent.add_node("block_unsafe_content", block_unsafe_content)
agent.set_entry_point("guard_input")


def check_safety(state: AgentState) -> Literal["unsafe", "safe"]:
    safety: SafeguardOutput = state["safety"]
    match safety.safety_assessment:
        case SafetyAssessment.UNSAFE:
            return "unsafe"
        case _:
            return "safe"


agent.add_conditional_edges(
    "guard_input", check_safety, {"unsafe": "block_unsafe_content", "safe": "model"}
)
agent.add_edge("block_unsafe_content", END)
agent.add_edge("tools", "after_tools")
agent.add_conditional_edges(
    "after_tools",
    route_after_tools,
    {"model": "model", "end": END},
)


def pending_tool_calls(state: AgentState) -> Literal["tools", "done"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        raise TypeError(f"Expected AIMessage, got {type(last_message)}")
    if last_message.tool_calls:
        return "tools"
    return "done"


agent.add_conditional_edges("model", pending_tool_calls, {"tools": "tools", "done": END})

jis_reports_agent = agent.compile()
