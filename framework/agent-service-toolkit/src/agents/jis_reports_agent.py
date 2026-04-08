"""Agente JIS Reportes: solo herramientas de datos internos (MySQL), sin búsqueda web."""

from datetime import datetime
from typing import Literal

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, SystemMessage
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

current_date = datetime.now().strftime("%d/%m/%Y")
instructions = f"""
Eres el asistente de gestión de JIS PARKING (jisreportes). Fecha de hoy: {current_date}.

Tienes herramientas para:
- Listar sucursales activas con responsables y direcciones.
- Consultar KPI de ingresos por mes (vista mensual o acumulada), opcionalmente por sucursal.

Reglas:
- Responde en español, claro y conciso para gerencia.
- El usuario NO ve el JSON crudo de las herramientas: resume cifras y hallazgos en texto.
- Si faltan parámetros (mes, año, tipo mensual/acumulado), pregúntalos antes de llamar a la herramienta.
- No inventes datos: solo lo que devuelven las herramientas.
"""


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
agent.add_edge("tools", "model")


def pending_tool_calls(state: AgentState) -> Literal["tools", "done"]:
    last_message = state["messages"][-1]
    if not isinstance(last_message, AIMessage):
        raise TypeError(f"Expected AIMessage, got {type(last_message)}")
    if last_message.tool_calls:
        return "tools"
    return "done"


agent.add_conditional_edges("model", pending_tool_calls, {"tools": "tools", "done": END})

jis_reports_agent = agent.compile()
