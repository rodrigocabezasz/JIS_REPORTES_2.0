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

from agents.jis_tools import (
    jis_consultar_abonados,
    jis_consultar_depositos,
    jis_consultar_kpi_ingresos,
    jis_consultar_ventas_diarias,
    jis_distribucion_sucursales,
    jis_informe_ventas_comparativo,
    jis_listar_sucursales,
    jis_obtener_evolucion_temporal,
    jis_obtener_resumen_ejecutivo,
    jis_ranking_sucursales,
    jis_resumen_abonados,
    jis_resumen_depositos,
)
from agents.safeguard import Safeguard, SafeguardOutput, SafetyAssessment
from core import get_model, settings


class AgentState(MessagesState, total=False):
    safety: SafeguardOutput
    remaining_steps: RemainingSteps


tools = [
    jis_listar_sucursales,
    jis_distribucion_sucursales,
    jis_obtener_resumen_ejecutivo,
    jis_ranking_sucursales,
    jis_obtener_evolucion_temporal,
    jis_consultar_kpi_ingresos,
    jis_informe_ventas_comparativo,
    jis_consultar_ventas_diarias,
    jis_consultar_depositos,
    jis_resumen_depositos,
    jis_consultar_abonados,
    jis_resumen_abonados,
]

_TOOL_NAMES = frozenset(t.name for t in tools)

current_date = datetime.now().strftime("%d/%m/%Y")
instructions = f"""
Eres el asistente de gestión de JIS PARKING (jisreportes). Fecha de hoy: {current_date}.

Tienes herramientas para: catálogo de sucursales (QRY_BRANCH_OFFICES), distribución y % por segmento/zona/región/
comuna/marca, **informes de ventas** (mensuales y **diarios**), resumen ejecutivo agregado, ranking por mes,
evolución temporal por sucursal, detalle KPI fila a fila (KPI_INGRESOS_IMG_MES), y **depósitos / recaudación**
(vista **QRY_REPORTE_DEPOSITOS**: listado filtrado y resumen mensual), y **abonados / DTEs**
(**CABECERA_ABONADOS** + **dte_types**), alineado a jisreportes.com (Track de Abonados y KPI DTE).

Idioma (obligatorio):
- Todas las respuestas al usuario deben estar en español (Chile o neutro). No uses inglés ni mezclas.
- Si en el historial hay texto en inglés, ignóralo como referencia de idioma: tú respondes siempre en español.

Invocación de herramientas (modelos locales / Ollama):
- Si debes llamar una herramienta, haz **una sola** invocación por turno (usa las tool_calls nativas del API).
- **No** escribas JSON de herramienta repetido ni en bloque en el texto de respuesta; el sistema ejecuta las tools por sí solo.

--- Matriz de decisión (intención → herramienta) ---

Elige UNA herramienta según la intención principal. Si faltan año o mes para KPIs, pregunta solo lo mínimo.

| Pregunta típica del usuario | Herramienta | Por qué |
|----------------------------|--------------|---------|
| ¿Quién es el responsable/jefe de la sucursal X? ¿Dónde queda? Datos del local | jis_listar_sucursales | Inventario / texto; QRY_BRANCH_OFFICES. |
| **ID de sucursal, número de sucursal, código de local, dte_code / código DTE** cuando el usuario da el **nombre del parking/local** | jis_listar_sucursales | **sucursal_contiene** = texto sobre **branch_office**; la tabla trae `branch_office_id` y `dte_code`. |
| ¿Cuánto ganamos en total en enero? Suma del mes, total empresa, resumen ejecutivo | jis_obtener_resumen_ejecutivo | Agregados SUM; no devuelve fila por fila por sucursal. |
| Top 5 / 10 parkings que más venden; ranking por ingresos | jis_ranking_sucursales | ORDER BY + LIMIT sobre KPI mensual. |
| ¿Cómo le fue a Cerrillos este semestre? Evolución mes a mes de UNA sucursal | jis_obtener_evolucion_temporal | Serie temporal (varios meses, una sucursal). |
| Detalle KPI por sucursal (tabla de filas k.* como en Navicat), un año/mes | jis_consultar_kpi_ingresos | Mensual/acumulado; no pivota año anterior ni presupuesto en un cuadro. |
| **Resumen / informe gerencial** como jisreportes (tarjetas + tabla): ingresos, año ant., ppto, Var %, Desv % vs ppto, tickets, ticket prom. | **jis_informe_ventas_comparativo** | `alcance_temporal`: **mes** = un mes (Mensual histórico); **ytd** = ene.–mes (Acumulado mes en curso). |
| **Ventas diarias**, desglose **día a día**, por **rango de fechas**, semana, “cómo vendimos cada día en…” | **jis_consultar_ventas_diarias** | KPI_INGRESOS_DIARIO + nombre sucursal; pide `fecha_desde` / `fecha_hasta` en YYYY-MM-DD. |
| Presupuesto / **ppto** diario (cuando lo piden explícito como meta o presupuesto diario) | jis_consultar_ventas_diarias | `metrica="ppto"` (misma tabla, filas con metrica ppto). |
| Porcentaje o cantidad de sucursales **por segmento** (o zona, región, comuna, marca) | **jis_distribucion_sucursales** | `GROUP BY` + conteos y %; no uses solo jis_listar_sucursales para eso. |
| **Depósitos** listados (pendientes, con diferencia, por sucursal/supervisor, rango de fechas de **recaudación**) | **jis_consultar_depositos** | `QRY_REPORTE_DEPOSITOS`; fechas YYYY-MM-DD o `year`+`month`; **estado_deposito** solo valores literales permitidos. |
| **Resumen KPI depósitos** (totales, sumas recaudado/depositado/diferencia, latencia, latencia “seguimiento” sin correctos/a favor, por estado); mismo filtro que listado | **jis_resumen_depositos** | `year`+`month` o rango ISO; opcional: sucursal, supervisor/**responsable**, estado; excl. OFICINA por defecto. |
| **Abonados / DTEs** listado (folio, RUT, cliente, status, montos, tipo documento, sucursal) por **fecha de documento** | **jis_consultar_abonados** | Rango ISO o `year`+`month`; opcional **status_id** (ej. 4 = KPI pendientes legacy), **imputada_por_pagar**, sucursal, responsable sucursal, RUT, cliente, **dte_type_id**, folio. |
| **Resumen abonados** (totales, por status, KPI status_id=4, bloque imputada por pagar) | **jis_resumen_abonados** | Mismos filtros de periodo y sucursal que el listado (sin RUT/cliente/folio). |

Reglas rápidas:
- "Total / cuánto ganamos / suma del mes" → jis_obtener_resumen_ejecutivo (year, month, tipo_periodo si dicen acumulado).
- "Los que más venden / top N" → jis_ranking_sucursales (year, month, top_n).
- "Evolución / semestre / mes a mes / tendencia de [nombre sucursal]" → jis_obtener_evolucion_temporal
  (year, semestre=1 o 2, o mes_desde/mes_hasta; sucursal_contiene o branch_office_id).
- "Desglose por sucursal del KPI" / "dame el KPI mensual detallado" → jis_consultar_kpi_ingresos.
- "Vs año anterior" + **presupuesto** / **ppto** / "informe gerencial" / "resumen general" / "real vs meta" / tickets / ticket promedio → **jis_informe_ventas_comparativo** (`agrupacion` total|sucursal|responsable; `alcance_temporal` **mes** o **ytd** según filtros del dashboard).
- "Ventas por día" / "informe diario" / "última semana día a día" / "del 1 al 15 de marzo" → jis_consultar_ventas_diarias
  (calcula fechas ISO; máx. ~93 días por consulta).
- "Depósitos pendientes" / "reporte de depósitos" / "diferencias en depósitos" / "latencia depósitos" / recaudación
  vs depositado → **jis_consultar_depositos** (tabla) o **jis_resumen_depositos** (agregados del mes).
- Piden **totales del mes**, **cuántos por estado**, **suma de diferencias**, **montos recaudado/depositado**, **KPI días de retraso/latencia** (promedio general y excluyendo “Depositado Correcto” y “Depositado a Favor”) → **jis_resumen_depositos** (`year`, `month`, o fechas ISO; opcional sucursal / **responsable_contiene** / supervisor / estado).
- “Abonados”, “DTEs”, “track abonados”, “imputada por pagar”, “pendientes DTE”, folio/RUT/cliente en documentos abonados → **jis_consultar_abonados** (tabla) o **jis_resumen_abonados** (agregados y KPI **status_id=4**).

--- Depósitos (QRY_REPORTE_DEPOSITOS) ---

- **Fecha de negocio** para filtrar listados: **Fecha_Recaudacion** (`fecha_recaudacion_desde` / `fecha_recaudacion_hasta`
  en ISO, o **`year` + `month`** para el mes calendario completo).
- **estado_deposito** (solo si el usuario filtra por estado): usa **exactamente** uno de:
  `Pendiente`, `Depositado con Diferencia`, `Depositado a Favor`, `Depositado Correcto` (como en la vista; el modelo
  puede mapear sinónimos del usuario a estos literales).
- **excluir_sucursal_oficina** (default true): coherente con KPI depósitos legacy que no cuenta filas tipo OFICINA;
  si piden **incluir oficina** o **todos sin filtrar oficina**, pasá `false`.
- **sucursal_contiene** = nombre del local en la vista (**Sucursal**); **supervisor_contiene** o **responsable_contiene**
  = columna **Supervisor** (responsable comercial; mismo campo que muestra el legacy).
  Para id numérico → **branch_office_id**.
- No confundas con **ventas diarias** (KPI_INGRESOS_DIARIO): depósitos = herramientas **jis_consultar_depositos** /
  **jis_resumen_depositos**.

--- Abonados / DTEs (CABECERA_ABONADOS, dashboard Track jisreportes) ---

- Fecha de corte: columna **date** del documento (`fecha_documento_desde` / `fecha_documento_hasta` o `year`+`month`).
- **status_id=4** = mismo criterio que el KPI **GET /kpi/dtes/resumen** (DTE pendientes en el legacy).
- **imputada_por_pagar=true** filtra el texto de status como en el front (**imputada por pagar**, minúsculas); no mezclar con **status_id** en la misma llamada (si mandás **status_id**, tiene prioridad).
- **responsable_sucursal_contiene** = columna **responsable** del maestro **QRY_BRANCH_OFFICES** (supervisor del local), no confundir con depósitos (**Supervisor** en la vista de depósitos).
- Sin login no hay “solo mis sucursales”: no inventes filtro por cartera de usuario.

--- Informes de ventas (cuándo usar cada tool) ---

- **Vista mensual / “cuánto vendimos en marzo” / total empresa / todas las sucursales en un mes:** prioriza
  **jis_obtener_resumen_ejecutivo** (totales) o **jis_ranking_sucursales** (top por parking) o **jis_consultar_kpi_ingresos**
  (detalle por sucursal en ese mes). Si piden **presupuesto**, **año anterior**, **Var %**, **Desv % vs meta**,
  **tickets** o **tabla tipo informe gerencial** → **jis_informe_ventas_comparativo** con **alcance_temporal="mes"**.
- **Vista acumulada año (ene.–mes en curso)** como el dashboard “Acumulado (Mes en Curso)” → la misma tool con **alcance_temporal="ytd"** (suma filas KPI **Mensual** de enero a `month`).
  No uses ventas diarias si no piden desglose por **día**.
- **Vista diaria / evolución dentro del mes por día / comparar días:** **jis_consultar_ventas_diarias** con rango
  `fecha_desde`–`fecha_hasta`. Si dicen “marzo 2026” y quieren diario → `2026-03-01` a `2026-03-31`.
- **Una sucursal por nombre:** en ventas diarias usa **sucursal_contiene** (como en otras tools) o **branch_office_id**.
- **Presupuesto diario:** `metrica="ppto"` en **jis_consultar_ventas_diarias** cuando el usuario hable de meta/presupuesto/ppto.

--- jis_listar_sucursales (inventario / maestro sucursales) ---

Misma semántica que el legacy: por defecto solo activas (status_id = 7). No pidas año ni mes.

**Regla de oro — nombre que dice el usuario = casi siempre branch_office:**
La mayoría de preguntas llegan con el **nombre comercial del local** tal como aparece en reportes (columna **branch_office**):
«LIDER CORDILLERA», «TOTTUS QUILICURA», etc. Ahí debes usar **sucursal_contiene** (o **nombre_sucursal_contiene**).
**marca_contiene / principal_contiene** es solo cuando hablan de la **cadena corta** (LIDER, TOTTUS, SANTA ISABEL) sin nombre de local.
- Piden **id**, **número de sucursal**, **branch_office_id**, **código de local**, **dte_code**, **código DTE** y dan un nombre → **jis_listar_sucursales** con **sucursal_contiene**; lee `branch_office_id` y `dte_code` del JSON y responde en español.
- **codigo_dte_contiene** solo si el usuario trae **un trozo del código DTE** para buscar, no cuando trae el nombre del local.

**modo_respuesta (importante):**
- Preguntas del tipo "¿cuántas sucursales…?", "dame el número", "solo el total" → modo_respuesta="contar".
- "Lista", "muéstrame", "detalle", "cuáles son", "dónde está" → modo_respuesta="listar" (o omítelo; listar es el default).

**Filtros (pregunta del usuario → argumento → columna SQL):**

| Idea del usuario | Argumento de la tool | Columna |
|------------------|----------------------|---------|
| Responsable, supervisor comercial, persona a cargo | responsable_contiene | responsable |
| Nombre del local, parking, sucursal | sucursal_contiene o nombre_sucursal_contiene | branch_office |
| Región (Metropolitana, etc.) | region_contiene | region |
| Comuna (Providencia, Santiago…) | comuna_contiene | commune |
| Zona (Centro, Norte…) | zona_contiene | zone |
| Segmento (MALL, SUPERMERCADO, EDIFICIOS…) | segmento_contiene | segment |
| Marca, cadena, principal (LIDER, TOTTUS…) | principal_contiene o marca_contiene | principal |
| Nombre tipo **«LIDER CORDILLERA»** (marca + lugar en una frase) | **sucursal_contiene** o **local_marca_o_comuna_contiene** (mejor); si el modelo pasó solo marca con 2+ palabras, la tool también busca en branch_office | branch_office (+ OR) |
| Dirección, calle | direccion_contiene | address |
| Código DTE (usuario trae dígitos/texto del código) | codigo_dte_contiene | dte_code |
| RUT o texto del supervisor en principal_supervisor | supervisor_contiene | principal_supervisor |
| ID numérico de sucursal (el de la API / branch_office_id) | branch_office_id | id |
| Texto que puede ser **nombre del local**, **marca** o **comuna** (ej. "Sta Isabel", "Santa Isabel", barrio en el nombre del parking) | **local_marca_o_comuna_contiene** | OR en branch_office, principal, commune |

**Importante:** `principal` puede ser la cadena literal **SANTA ISABEL** (marca), no solo LIDER/TOTTUS. Si el
usuario escribe **"Sta Isabel" / "STA ISABEL"**, el LIKE `%sta isabel%` **no** coincide con `SANTA ISABEL` en
MySQL (falta la "N"); la tool normaliza **Sta./STA + espacio → Santa** en búsquedas de sucursal, marca y
`local_marca_o_comuna_contiene`. Para dudas entre nombre de local, comuna y marca en una sola frase, sigue
siendo útil **local_marca_o_comuna_contiene** (OR en branch_office, principal, commune).

**Otros flags:**
- solo_activas=false: cuando quieran **todas** las filas de la vista para ese criterio (activas + inactivas),
  p. ej. "cuántas sucursales tiene asignadas [X] incluyendo cerradas". Si no, deja true (solo status_id = 7).
- solo_visibilidad_reporte=true: solo sucursales con visibility_id = 1 (criterio de reportes filtrados por
  responsable en jisreportes). Úsalo si piden explícitamente cartera visible en reportes / mis sucursales
  según visibilidad de sistema (no inventes IDs de usuario: sin login solo aplicas esto si el usuario lo pide claro).

**Reglas de nombre (responsable_contiene):**
- 3+ palabras significativas → una frase completa en LIKE (como Navicat).
- 2 palabras (ej. "david gomez") → ambas deben aparecer en el nombre (AND de LIKE).
- 1 palabra → un LIKE.

**Combinaciones:** puedes pasar varios filtros a la vez (ej. region_contiene + comuna_contiene + segmento_contiene).
Búsquedas parciales, sin distinguir mayúsculas. Listado global → todos los argumentos null.

**Ejemplos de intención (para que elijas argumentos):**
- "Sucursales de David Gómez" → responsable_contiene="David Gómez" (o dos tokens si dice "david gomez").
- "Locales Lider en la Región Metropolitana" → marca_contiene="Lider", region_contiene="Metropolitana".
- "Malls en comuna Santiago" → segmento_contiene="MALL", comuna_contiene="Santiago".
- "Zona Centro, segmento supermercado" → zona_contiene="Centro", segmento_contiene="SUPERMERCADO".
- "Sucursal con id 42" → branch_office_id=42.
- "ID de Lider Cordillera" / "número de sucursal de LIDER CORDILLERA" → sucursal_contiene o
  local_marca_o_comuna_contiene="Lider Cordillera" (preferido). Si usas marca_contiene con 2+ palabras, la tool
  busca también en branch_office (OR con principal).
- "¿Cuántas sucursales activas hay en Providencia?" → comuna_contiene="Providencia", modo_respuesta="contar".
- "Lista todas las Tottus" → marca_contiene="Tottus", modo_respuesta="listar".
- "¿Cuántas sucursales Sta Isabel y listarlas?" → local_marca_o_comuna_contiene="Sta Isabel" (o "STA ISABEL"),
  modo_respuesta="listar" (o "contar" si solo piden número en otra pregunta).
- "Porcentaje de sucursales por segmento" / "distribución por marca" → **jis_distribucion_sucursales** con
  dimension="segmento" (o marca, zona, region, comuna). **No** uses jis_listar_sucursales sin filtros para eso.

--- jis_distribucion_sucursales ---

Agregación: cuenta sucursales por `dimension` (segmento, zona, region, comuna, marca) y devuelve `porcentaje`
sobre el total. `solo_activas` como en el maestro. El sistema formatea tabla en español al final.

--- jis_obtener_resumen_ejecutivo ---

Agregado de un mes: sumas de efectivo/tarjeta/abonados/tickets sobre sucursales activas (join BO).
Argumentos: year, month, tipo_periodo ("mensual" o "acumulado"), branch_office_id opcional para una sola sucursal.
Respuesta: data[0] con campos suma_*; explica cifras al usuario sin inventar.

--- jis_ranking_sucursales ---

Top N sucursales por proxy ingresos (efectivo bruto + tarjeta bruto + abonados $) en un mes.
Argumentos: year, month, top_n (default 5, máx. 50), tipo_periodo.
Indica en la respuesta el criterio de orden (viene en JSON criterio_orden).

--- jis_obtener_evolucion_temporal ---

Serie mensual (Mensual + ingresos) para una sucursal: branch_office_id O sucursal_contiene (debe resolver a una sola).
year obligatorio. Para "este semestre": semestre=1 (ene-jun) o 2 (jul-dic). O mes_desde/mes_hasta explícitos.
Si hay varias sucursales con nombre parecido, el JSON trae error: pide aclaración al usuario.

--- jis_consultar_kpi_ingresos ---

Detalle: filas completas del KPI (k.*) por sucursal activa, mensual o acumulado, **un** año y mes.
Requiere tipo_vista ("mensual" o "acumulado"), year y month. Solo pregunta año/mes si faltan.
No uses esta tool si solo quieren un total agregado (usa jis_obtener_resumen_ejecutivo) ni ranking ni serie temporal.
Para comparación YoY + presupuesto en tabla resumida usa **jis_informe_ventas_comparativo**.
No mezcles requisitos del KPI con el listado de sucursales.

--- jis_informe_ventas_comparativo ---

Paridad funcional con **jisreportes.com** (resumen general + informe gerencial; sin gráficos).
**Ingresos** = efectivo neto + tarjeta neta + abonados (no usar criterio bruto del ranking).
**agrupacion:** `total` (tarjetas KPI: ingresos, ppto, sucursales, Var % YoY, Desv % vs ppto, ticket prom., tickets),
`sucursal` / `responsable` (tabla con columnas tipo gerencial).
**alcance_temporal:** `mes` = solo ese **month** (vista “Mensual histórico”); `ytd` = suma **ene.–month** con `periodo='Mensual'`.
Con **alcance_temporal=mes**, **tipo_periodo** sigue siendo mensual/acumulado (columna `periodo` del KPI). Filtros: **branch_office_id**, **responsable_contiene**.

--- jis_consultar_ventas_diarias ---

Tabla **KPI_INGRESOS_DIARIO** (periodo Diario), join con nombres en **QRY_BRANCH_OFFICES**.
Argumentos obligatorios: **fecha_desde**, **fecha_hasta** (YYYY-MM-DD). Opcional: **metrica** ingresos|ppto, filtro sucursal.
El sistema formatea tabla en español al final (como ranking/KPI).

Reglas generales:
- Usa siempre las herramientas del sistema (function calling); no escribas en el texto bloques JSON
  con "name" / "arguments" como sustituto de una llamada real.
- Claro y conciso para gerencia, siempre en español.

Datos reales (obligatorio, anti-alucinación):
- Tras cada herramienta recibes un JSON. Es la ÚNICA fuente de verdad. Cifras y nombres = literales del JSON.
- PROHIBIDO inventar ejemplos genéricos salvo que existan en "data".
- Si "success": false o "error", explica el error; no sustituyas con datos ficticios.
- Si count es 0 o data vacío, dilo claramente.
- Listado de sucursales: el número de filas debe coincidir con count (y con len(data)).
- Resumen ejecutivo, ranking y evolución: solo cifras y nombres del JSON; indica sucursales_en_agregado o count según corresponda.
- KPI detalle (jis_consultar_kpi_ingresos): solo valores presentes en "data"; indica truncado si aplica.
- Informe comparativo ventas: JSON con ingresos/ppto, Var % YoY, Desv % vs ppto, tickets, ticket promedio, sucursales (si total); indica **alcance_temporal** (mes vs ytd), agrupación y si truncated.
- Ventas diarias: columnas del JSON (fecha, montos, tickets); indica si truncated por límite de filas.
- Depósitos listado: filas de `QRY_REPORTE_DEPOSITOS`; indica truncated; estados = literales del JSON.
- Resumen depósitos: total_registros, suma_monto_recaudado, suma_monto_depositado, suma_diferencia,
  promedio_dias_latencia, promedio_dias_latencia_seguimiento (sin correctos ni a favor), tabla por_estado.
- Abonados listado/resumen: cifras del JSON; **kpi_dtes_pendientes** = status_id 4; **imputada_por_pagar** = bloque dedicado en resumen.

Presentación:
- El usuario no necesita JSON crudo salvo que pida depuración.
- Si modo_respuesta fue "contar" en sucursales, el sistema ya devuelve un texto breve; no repitas tabla larga.
- Si el JSON incluye source / tabla_o_vista, puedes mencionar en una frase que los datos vienen de MySQL (Navicat/reader_user).
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


def _first_json_value(text: str) -> Any | None:
    """Primer objeto JSON válido en `text` (p. ej. varios objetos JSON concatenados sin separador)."""
    dec = json.JSONDecoder()
    s = text.strip()
    for i, c in enumerate(s):
        if c != "{":
            continue
        try:
            return dec.raw_decode(s, i)[0]
        except json.JSONDecodeError:
            continue
    return None


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
_DISTRIBUCION_TOOL = "jis_distribucion_sucursales"
_RANKING_TOOL = "jis_ranking_sucursales"
_RESUMEN_TOOL = "jis_obtener_resumen_ejecutivo"
_EVOLUCION_TOOL = "jis_obtener_evolucion_temporal"
_KPI_CONSULTA_TOOL = "jis_consultar_kpi_ingresos"
_INFORME_VENTAS_TOOL = "jis_informe_ventas_comparativo"
_VENTAS_DIARIAS_TOOL = "jis_consultar_ventas_diarias"
_DEPOSITOS_LISTADO_TOOL = "jis_consultar_depositos"
_DEPOSITOS_RESUMEN_TOOL = "jis_resumen_depositos"
_ABONADOS_LISTADO_TOOL = "jis_consultar_abonados"
_ABONADOS_RESUMEN_TOOL = "jis_resumen_abonados"
_MAX_SUCURSALES_TABLA = 400
_MAX_DEPOSITOS_TABLA = 80
_MAX_ABONADOS_TABLA = 60

_MESES_ES = (
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
    if not isinstance(p, dict) or p.get("tabla_o_vista") != "QRY_BRANCH_OFFICES":
        return False
    if p.get("tipo_resultado") == "distribucion_sucursales":
        return False
    return True


def _tool_is_distribucion_sucursales(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _DISTRIBUCION_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return (
        isinstance(p, dict)
        and p.get("tipo_resultado") == "distribucion_sucursales"
        and p.get("tabla_o_vista") == "QRY_BRANCH_OFFICES"
    )


def _tool_is_ranking_sucursales(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _RANKING_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return isinstance(p, dict) and "criterio_orden" in p


def _tool_is_resumen_ejecutivo(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _RESUMEN_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    if not isinstance(p, dict):
        return False
    row = (p.get("data") or [{}])[0] if p.get("data") else {}
    return isinstance(row, dict) and "sucursales_en_agregado" in row


def _tool_is_evolucion_temporal(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _EVOLUCION_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return isinstance(p, dict) and "mes_desde" in p and "mes_hasta" in p and "branch_office_id" in p


def _tool_is_consultar_kpi(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _KPI_CONSULTA_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    if not isinstance(p, dict):
        return False
    if p.get("tipo_resultado") == "informe_ventas_comparativo":
        return False
    return p.get("truncated") is not None and p.get("tabla_o_vista") == (
        "KPI_INGRESOS_IMG_MES + QRY_BRANCH_OFFICES"
    )


def _tool_is_informe_ventas_comparativo(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _INFORME_VENTAS_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return isinstance(p, dict) and p.get("tipo_resultado") == "informe_ventas_comparativo"


def _tool_is_ventas_diarias(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _VENTAS_DIARIAS_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return isinstance(p, dict) and p.get("tipo_resultado") == "ventas_diarias"


def _tool_is_depositos_listado(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _DEPOSITOS_LISTADO_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return isinstance(p, dict) and p.get("tipo_resultado") == "depositos_listado"


def _tool_is_depositos_resumen(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _DEPOSITOS_RESUMEN_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return isinstance(p, dict) and p.get("tipo_resultado") == "depositos_resumen"


def _tool_is_abonados_listado(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _ABONADOS_LISTADO_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return isinstance(p, dict) and p.get("tipo_resultado") == "abonados_listado"


def _tool_is_abonados_resumen(msg: ToolMessage) -> bool:
    if getattr(msg, "name", None) == _ABONADOS_RESUMEN_TOOL:
        return True
    raw = msg.content
    if not isinstance(raw, str):
        return False
    try:
        p = json.loads(raw)
    except json.JSONDecodeError:
        return False
    return isinstance(p, dict) and p.get("tipo_resultado") == "abonados_resumen"


def _format_ranking_sucursales_es(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        rows = []
    vista = payload.get("tabla_o_vista", "KPI")
    user = payload.get("mysql_user", "")
    y, m = int(payload.get("year", 0)), int(payload.get("month", 0))
    mes_txt = _MESES_ES[m] if 1 <= m <= 12 else str(m)
    intro = (
        f"**Ranking de sucursales por ingresos (proxy)** · `{vista}`"
        f"{f' · usuario `{user}`' if user else ''}.\n\n"
        f"**Periodo:** {mes_txt} {y} · **Criterio:** efectivo bruto + tarjeta bruto + abonados ($).\n\n"
    )
    if not rows:
        return intro + "No hay filas para ese mes y criterio (o no hay datos en KPI)."

    headers = [
        "#",
        "ID",
        "Sucursal",
        "Responsable",
        "Total proxy",
        "Efectivo",
        "Tarjeta",
        "Abonados",
        "Tickets",
    ]
    keys = [
        "branch_office_id",
        "branch_office",
        "responsable",
        "total_proxy_ingresos",
        "cash_amount",
        "card_amount",
        "subscribers",
        "ticket_number",
    ]
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    head = "| " + " | ".join(headers) + " |"
    lines: list[str] = [intro, head, sep]
    for i, r in enumerate(rows, start=1):
        if not isinstance(r, dict):
            continue
        cells = [str(i)] + [_md_cell(r.get(k)) for k in keys]
        lines.append("| " + " | ".join(cells) + " |")
    lines.append("")
    lines.append(f"*Mostrando {len(rows)} sucursal(es).*")
    return "\n".join(lines)


def _format_resumen_ejecutivo_es(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list) or not rows or not isinstance(rows[0], dict):
        return "**Resumen ejecutivo:** sin filas agregadas para el periodo."
    r = rows[0]
    vista = payload.get("tabla_o_vista", "KPI")
    user = payload.get("mysql_user", "")
    y = int(payload.get("year", 0))
    m = int(payload.get("month", 0))
    mes_txt = _MESES_ES[m] if 1 <= m <= 12 else str(m)
    p = payload.get("periodo", "")
    intro = (
        f"**Resumen ejecutivo de ingresos** · `{vista}`"
        f"{f' · usuario `{user}`' if user else ''}\n\n"
        f"**Periodo:** {p} · **{mes_txt} {y}**\n\n"
    )
    lines = [
        f"- **Sucursales en el agregado:** {_md_cell(r.get('sucursales_en_agregado'))}",
        f"- **Suma efectivo bruto:** {_md_cell(r.get('suma_efectivo_bruto'))}",
        f"- **Suma efectivo neto:** {_md_cell(r.get('suma_efectivo_neto'))}",
        f"- **Suma tarjeta bruto:** {_md_cell(r.get('suma_tarjeta_bruto'))}",
        f"- **Suma tarjeta neto:** {_md_cell(r.get('suma_tarjeta_neto'))}",
        f"- **Suma abonados ($):** {_md_cell(r.get('suma_abonados_monto'))}",
        f"- **Suma tickets:** {_md_cell(r.get('suma_tickets'))}",
    ]
    return intro + "\n".join(lines)


def _format_evolucion_temporal_es(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        rows = []
    vista = payload.get("tabla_o_vista", "KPI")
    user = payload.get("mysql_user", "")
    y = int(payload.get("year", 0))
    md, mh = int(payload.get("mes_desde", 1)), int(payload.get("mes_hasta", 12))
    bid = payload.get("branch_office_id", "")
    intro = (
        f"**Evolución mensual (ingresos)** · `{vista}`"
        f"{f' · usuario `{user}`' if user else ''}\n\n"
        f"**Año:** {y} · **Meses:** {md}–{mh} · **branch_office_id:** {bid}\n\n"
    )
    if not rows:
        return intro + "No hay puntos en el rango."

    headers = ["Mes", "Efectivo bruto", "Tarjeta bruto", "Abonados", "Tickets"]
    keys = ["mes", "cash_amount", "card_amount", "subscribers", "ticket_number"]
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    head = "| " + " | ".join(headers) + " |"
    lines = [intro, head, sep]
    for r in rows:
        if not isinstance(r, dict):
            continue
        mes_n = int(r.get("mes") or 0)
        mes_l = _MESES_ES[mes_n] if 1 <= mes_n <= 12 else str(mes_n)
        cells = [mes_l] + [_md_cell(r.get(k)) for k in keys[1:]]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _format_ventas_diarias_es(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        rows = []
    vista = payload.get("tabla_o_vista", "KPI_INGRESOS_DIARIO")
    user = payload.get("mysql_user", "")
    fd = payload.get("fecha_desde", "")
    fh = payload.get("fecha_hasta", "")
    met = payload.get("metrica_consulta", "ingresos")
    trunc = bool(payload.get("truncated"))
    bid = payload.get("branch_office_id")
    intro = (
        f"**Ventas diarias** · `{vista}`"
        f"{f' · usuario `{user}`' if user else ''}\n\n"
        f"**Rango:** {fd} a {fh} · **Métrica:** {met}"
        f"{f' · **Sucursal id:** {bid}' if bid is not None else ''}\n\n"
    )
    if not rows:
        return intro + "No hay filas en ese rango (o sin datos para la sucursal/métrica indicada)."

    headers = [
        "Fecha",
        "ID",
        "Sucursal",
        "Responsable",
        "Efectivo bruto",
        "Efectivo neto",
        "Tarjeta bruto",
        "Tarjeta neto",
        "Abonados",
        "Tickets",
        "Ppto",
    ]
    keys = [
        "fecha",
        "branch_office_id",
        "branch_office",
        "responsable",
        "cash_amount",
        "cash_net_amount",
        "card_amount",
        "card_net_amount",
        "subscribers",
        "ticket_number",
        "ppto",
    ]
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    head = "| " + " | ".join(headers) + " |"
    lines = [intro, head, sep]
    for r in rows:
        if not isinstance(r, dict):
            continue
        lines.append("| " + " | ".join(_md_cell(r.get(k)) for k in keys) + " |")
    out = "\n".join(lines)
    if trunc:
        out += f"\n\n*Se alcanzó el límite de filas; hay más días/sucursales en la base.*"
    return out


def _format_depositos_listado_es(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        rows = []
    vista = payload.get("tabla_o_vista", "QRY_REPORTE_DEPOSITOS")
    user = payload.get("mysql_user", "")
    fa = payload.get("filtros_aplicados") or {}
    trunc = bool(payload.get("truncated"))
    intro = (
        f"**Depósitos / recaudación** · `{vista}`"
        f"{f' · usuario `{user}`' if user else ''}\n\n"
    )
    if isinstance(fa, dict) and fa:
        fd = fa.get("fecha_recaudacion_desde", "")
        fh = fa.get("fecha_recaudacion_hasta", "")
        intro += f"**Recaudación (filtro):** {fd} a {fh}"
        if fa.get("estado_deposito"):
            intro += f" · **Estado:** {fa.get('estado_deposito')}"
        if fa.get("branch_office_id") is not None:
            intro += f" · **Sucursal id:** {fa.get('branch_office_id')}"
        if fa.get("sucursal_contiene"):
            intro += f" · **Sucursal contiene:** {fa.get('sucursal_contiene')}"
        if fa.get("supervisor_contiene"):
            intro += f" · **Supervisor contiene:** {fa.get('supervisor_contiene')}"
        excl = fa.get("excluir_sucursal_oficina", True)
        intro += f" · **Excl. OFICINA:** {'sí' if excl else 'no'}"
        intro += "\n\n"
    if not rows:
        return intro + "No hay filas para ese criterio."

    headers = [
        "F. recaudación",
        "F. depósito",
        "ID",
        "Sucursal",
        "Supervisor",
        "Recaudado",
        "Depositado",
        "Diferencia",
        "Latencia",
        "Estado",
        "Est. dif.",
    ]
    keys = [
        "Fecha_Recaudacion",
        "Fecha_Deposito",
        "branch_office_id",
        "Sucursal",
        "Supervisor",
        "Monto_Recaudado",
        "Monto_Depositado",
        "Diferencia",
        "Dias_Latencia",
        "Estado_Deposito",
        "Estado_Diferencia",
    ]
    show = rows[:_MAX_DEPOSITOS_TABLA]
    table_trunc = len(rows) > _MAX_DEPOSITOS_TABLA
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    head = "| " + " | ".join(headers) + " |"
    lines = [intro, head, sep]
    for r in show:
        if not isinstance(r, dict):
            continue
        lines.append("| " + " | ".join(_md_cell(r.get(k)) for k in keys) + " |")
    out = "\n".join(lines)
    if table_trunc:
        out += f"\n\n*Se muestran {_MAX_DEPOSITOS_TABLA} de {len(rows)} filas.*"
    if trunc:
        out += "\n\n*La consulta alcanzó el límite máximo de filas devueltas; puede haber más en la base.*"
    return out


def _format_depositos_resumen_es(payload: dict[str, Any]) -> str:
    vista = payload.get("tabla_o_vista", "QRY_REPORTE_DEPOSITOS")
    user = payload.get("mysql_user", "")
    y = int(payload.get("year", 0))
    m = int(payload.get("month", 0))
    mes_txt = _MESES_ES[m] if 1 <= m <= 12 else str(m)
    excl = payload.get("excluir_sucursal_oficina", True)
    fd = payload.get("fecha_recaudacion_desde", "")
    fh = payload.get("fecha_recaudacion_hasta", "")
    por_mes = bool(payload.get("periodo_por_mes_calendario", True))
    periodo_line = (
        f"**Mes recaudación:** {mes_txt} {y}" if por_mes and y and m else f"**Recaudación:** {fd} a {fh}"
    )
    fa = payload.get("filtros_aplicados") or {}
    filtros_extra = ""
    if isinstance(fa, dict):
        bits: list[str] = []
        if fa.get("estado_deposito"):
            bits.append(f"estado **{fa.get('estado_deposito')}**")
        if fa.get("branch_office_id") is not None:
            bits.append(f"sucursal id **{fa.get('branch_office_id')}**")
        if fa.get("sucursal_contiene"):
            bits.append(f"sucursal contiene «{fa.get('sucursal_contiene')}»")
        if fa.get("supervisor_contiene"):
            bits.append(f"supervisor «{fa.get('supervisor_contiene')}»")
        if fa.get("responsable_contiene"):
            bits.append(f"responsable «{fa.get('responsable_contiene')}»")
        if bits:
            filtros_extra = " · Filtros: " + ", ".join(bits)
    intro = (
        f"**Resumen de depósitos** · `{vista}`"
        f"{f' · usuario `{user}`' if user else ''}\n\n"
        f"{periodo_line} · **Excl. sucursales con OFICINA en el nombre:** "
        f"{'sí' if excl else 'no'}{filtros_extra}\n\n"
    )
    tot = int(payload.get("total_registros", 0))
    sd = payload.get("suma_diferencia")
    sr = payload.get("suma_monto_recaudado")
    sdep = payload.get("suma_monto_depositado")
    lat = payload.get("promedio_dias_latencia")
    lat_seg = payload.get("promedio_dias_latencia_seguimiento")
    intro += (
        f"- **Registros:** {tot}\n"
        f"- **Suma recaudado:** {_md_cell(sr)}\n"
        f"- **Suma depositado:** {_md_cell(sdep)}\n"
        f"- **Suma diferencia:** {_md_cell(sd)}\n"
        f"- **Promedio días latencia (todos los estados):** {_md_cell(lat)}\n"
        f"- **Promedio días latencia (seguimiento, excl. correcto y a favor):** {_md_cell(lat_seg)}\n\n"
    )
    por = payload.get("por_estado") or []
    if not isinstance(por, list) or not por:
        return intro + "*Sin desglose por estado.*"
    head = "| Estado | Cantidad |"
    sep = "| --- | ---: |"
    lines = [intro + "**Por estado**\n\n", head, sep]
    for r in por:
        if not isinstance(r, dict):
            continue
        lines.append(f"| {_md_cell(r.get('estado'))} | {_md_cell(r.get('cantidad'))} |")
    return "\n".join(lines)


def _format_abonados_listado_es(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        rows = []
    vista = payload.get("tabla_o_vista", "CABECERA_ABONADOS")
    user = payload.get("mysql_user", "")
    fa = payload.get("filtros_aplicados") or {}
    trunc = bool(payload.get("truncated"))
    intro = f"**Abonados / DTEs** · `{vista}`{f' · usuario `{user}`' if user else ''}\n\n"
    if isinstance(fa, dict) and fa:
        intro += f"**Documento (fecha):** {fa.get('fecha_documento_desde', '')} a {fa.get('fecha_documento_hasta', '')}"
        if fa.get("status_id") is not None:
            intro += f" · **status_id:** {fa.get('status_id')}"
        if fa.get("imputada_por_pagar"):
            intro += " · **solo imputada por pagar**"
        if fa.get("branch_office_id") is not None:
            intro += f" · **Sucursal id:** {fa.get('branch_office_id')}"
        if fa.get("sucursal_contiene"):
            intro += f" · **Sucursal:** «{fa.get('sucursal_contiene')}»"
        if fa.get("responsable_sucursal_contiene"):
            intro += f" · **Responsable sucursal:** «{fa.get('responsable_sucursal_contiene')}»"
        if fa.get("rut_contiene"):
            intro += f" · **RUT:** «{fa.get('rut_contiene')}»"
        if fa.get("cliente_contiene"):
            intro += f" · **Cliente:** «{fa.get('cliente_contiene')}»"
        if fa.get("dte_type_id") is not None:
            intro += f" · **dte_type_id:** {fa.get('dte_type_id')}"
        if fa.get("folio") is not None:
            intro += f" · **folio:** {fa.get('folio')}"
        intro += "\n\n"
    if not rows:
        return intro + "No hay filas para ese criterio."

    headers = [
        "Fecha",
        "Folio",
        "Tipo",
        "RUT",
        "Cliente",
        "Sucursal",
        "Resp. suc.",
        "Status",
        "Subtotal",
        "Total",
        "Pago",
    ]
    keys = [
        "date",
        "folio",
        "document_type",
        "rut",
        "cliente",
        "sucursal_nombre",
        "responsable_sucursal",
        "status",
        "subtotal",
        "total",
        "payment_date",
    ]
    show = rows[:_MAX_ABONADOS_TABLA]
    table_trunc = len(rows) > _MAX_ABONADOS_TABLA
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    head = "| " + " | ".join(headers) + " |"
    lines_md = [intro, head, sep]
    for r in show:
        if not isinstance(r, dict):
            continue
        lines_md.append("| " + " | ".join(_md_cell(r.get(k)) for k in keys) + " |")
    out = "\n".join(lines_md)
    if table_trunc:
        out += f"\n\n*Se muestran {_MAX_ABONADOS_TABLA} de {len(rows)} filas.*"
    if trunc:
        out += "\n\n*La consulta alcanzó el límite máximo de filas devueltas; puede haber más en la base.*"
    return out


def _format_abonados_resumen_es(payload: dict[str, Any]) -> str:
    vista = payload.get("tabla_o_vista", "CABECERA_ABONADOS")
    user = payload.get("mysql_user", "")
    fd = payload.get("fecha_documento_desde", "")
    fh = payload.get("fecha_documento_hasta", "")
    por_mes = bool(payload.get("periodo_por_mes_calendario", True))
    y = int(payload.get("year", 0))
    m = int(payload.get("month", 0))
    mes_txt = _MESES_ES[m] if 1 <= m <= 12 else str(m)
    periodo_line = (
        f"**Mes documento:** {mes_txt} {y}" if por_mes and y and m else f"**Fechas documento:** {fd} a {fh}"
    )
    fa = payload.get("filtros_aplicados") or {}
    filtros_extra = ""
    if isinstance(fa, dict):
        bits: list[str] = []
        if fa.get("status_id") is not None:
            bits.append(f"status_id **{fa.get('status_id')}**")
        if fa.get("imputada_por_pagar"):
            bits.append("solo **imputada por pagar**")
        if fa.get("branch_office_id") is not None:
            bits.append(f"sucursal id **{fa.get('branch_office_id')}**")
        if fa.get("sucursal_contiene"):
            bits.append(f"sucursal «{fa.get('sucursal_contiene')}»")
        if fa.get("responsable_sucursal_contiene"):
            bits.append(f"responsable «{fa.get('responsable_sucursal_contiene')}»")
        if bits:
            filtros_extra = " · " + ", ".join(bits)
    intro = (
        f"**Resumen abonados / DTEs** · `{vista}`"
        f"{f' · usuario `{user}`' if user else ''}\n\n"
        f"{periodo_line}{filtros_extra}\n\n"
    )
    intro += (
        f"- **Registros:** {int(payload.get('total_registros', 0))}\n"
        f"- **Suma subtotal:** {_md_cell(payload.get('suma_subtotal'))}\n"
        f"- **Suma total:** {_md_cell(payload.get('suma_total'))}\n\n"
    )
    kpi = payload.get("kpi_dtes_pendientes") or {}
    imp = payload.get("imputada_por_pagar") or {}
    if isinstance(kpi, dict):
        intro += (
            f"**KPI DTE pendientes (status_id=4, como /kpi/dtes/resumen):** "
            f"{int(kpi.get('cantidad', 0))} docs · "
            f"monto subtotal {_md_cell(kpi.get('monto_subtotal'))}\n\n"
        )
    if isinstance(imp, dict):
        intro += (
            f"**Imputada por pagar:** "
            f"{int(imp.get('cantidad', 0))} docs · "
            f"monto subtotal {_md_cell(imp.get('monto_subtotal'))}\n\n"
        )
    por = payload.get("por_status") or []
    if not isinstance(por, list) or not por:
        return intro + "*Sin desglose por status.*"
    head = "| Status | Cantidad | Suma subtotal |"
    sep = "| --- | ---: | ---: |"
    lines = [intro + "**Por status**\n\n", head, sep]
    for r in por:
        if not isinstance(r, dict):
            continue
        lines.append(
            f"| {_md_cell(r.get('status'))} | {_md_cell(r.get('cantidad'))} | "
            f"{_md_cell(r.get('suma_subtotal'))} |"
        )
    return "\n".join(lines)


def _format_informe_ventas_comparativo_es(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        rows = []
    ag = str(payload.get("agrupacion", "total"))
    y = int(payload.get("year", 0))
    yp = int(payload.get("year_anterior", y - 1))
    m = int(payload.get("month", 0))
    mes_txt = _MESES_ES[m] if 1 <= m <= 12 else str(m)
    p = payload.get("periodo", "")
    alc = str(payload.get("alcance_temporal", "mes"))
    vista = payload.get("tabla_o_vista", "KPI")
    user = payload.get("mysql_user", "")
    intro = (
        f"**Informe de ventas** · `{vista}`"
        f"{f' · usuario `{user}`' if user else ''}\n\n"
        f"**Años:** {y} vs {yp} · **Mes referencia:** {mes_txt} · **Alcance:** {alc} "
        f"({'acumulado ene.–' + mes_txt if alc == 'ytd' else 'solo este mes'}) · "
        f"**Periodo KPI:** {p} · **Agrupación:** {ag}\n\n"
    )
    if payload.get("branch_office_id") is not None:
        intro += f"**Filtro sucursal id:** {payload.get('branch_office_id')}\n\n"
    rc = payload.get("responsable_contiene")
    if rc:
        intro += f"**Filtro responsable (contiene):** {rc}\n\n"
    nota = payload.get("nota")
    if isinstance(nota, str) and nota.strip():
        intro += f"*{nota.strip()}*\n\n"
    if not rows:
        return intro + "Sin filas para ese criterio."

    def pct_cell(v: Any) -> str:
        if v is None:
            return "—"
        try:
            return f"{float(v):.2f}%"
        except (TypeError, ValueError):
            return "—"

    if ag == "total":
        r = rows[0] if rows and isinstance(rows[0], dict) else {}
        if not isinstance(r, dict):
            return intro + "Sin datos agregados."
        bullets = [
            f"- **Ingresos {y} (periodo actual):** {_md_cell(r.get('ingresos_proxy_año_actual'))}",
            f"- **Ingresos {yp} (periodo anterior):** {_md_cell(r.get('ingresos_proxy_año_anterior'))}",
            f"- **Presupuesto / meta {y}:** {_md_cell(r.get('presupuesto_año_actual'))}",
            f"- **Sucursales (en filtro):** {_md_cell(r.get('sucursales_en_filtro'))}",
            f"- **Var % vs año ant. (crecimiento):** {pct_cell(r.get('var_pct_ingresos_yoy'))}",
            f"- **Desv % vs PPTO (cumplimiento):** {pct_cell(r.get('desv_pct_ingresos_vs_presupuesto'))}",
            f"- **Ticket promedio {y}:** {_md_cell(r.get('ticket_promedio_año_actual'))}",
            f"- **Tickets {y} / {yp}:** {_md_cell(r.get('tickets_año_actual'))} / {_md_cell(r.get('tickets_año_anterior'))}",
        ]
        return intro + "**Resumen general (tarjetas KPI)**\n\n" + "\n".join(bullets)

    var_keys = {"var_pct_ingresos_yoy", "desv_pct_ingresos_vs_presupuesto"}

    if ag == "sucursal":
        headers = [
            "#",
            "ID",
            "Sucursal",
            "Resp.",
            f"Ing. {y}",
            f"Ing. {yp}",
            "Var %",
            "Ppto",
            "Desv %",
            f"Tick. {y}",
            f"Tick. {yp}",
            "T. prom.",
        ]
        keys_row = [
            "branch_office_id",
            "branch_office",
            "responsable",
            "ingresos_proxy_año_actual",
            "ingresos_proxy_año_anterior",
            "var_pct_ingresos_yoy",
            "presupuesto_año_actual",
            "desv_pct_ingresos_vs_presupuesto",
            "tickets_año_actual",
            "tickets_año_anterior",
            "ticket_promedio_año_actual",
        ]
    else:
        headers = [
            "#",
            "Responsable",
            f"Ing. {y}",
            f"Ing. {yp}",
            "Var %",
            "Ppto",
            "Desv %",
            f"Tick. {y}",
            f"Tick. {yp}",
            "T. prom.",
        ]
        keys_row = [
            "grupo",
            "ingresos_proxy_año_actual",
            "ingresos_proxy_año_anterior",
            "var_pct_ingresos_yoy",
            "presupuesto_año_actual",
            "desv_pct_ingresos_vs_presupuesto",
            "tickets_año_actual",
            "tickets_año_anterior",
            "ticket_promedio_año_actual",
        ]

    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    head = "| " + " | ".join(headers) + " |"
    lines: list[str] = [intro, head, sep]
    for i, r in enumerate(rows, start=1):
        if not isinstance(r, dict):
            continue
        row_cells: list[str] = [str(i)]
        for k in keys_row:
            v = r.get(k)
            if k in var_keys:
                row_cells.append(pct_cell(v))
            else:
                row_cells.append(_md_cell(v))
        lines.append("| " + " | ".join(row_cells) + " |")
    out = "\n".join(lines)
    if payload.get("truncated"):
        out += f"\n\n*Tabla limitada a {len(rows)} fila(s); hay más grupos en la base.*"
    return out


def _format_consultar_kpi_es(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        rows = []
    vista = payload.get("tabla_o_vista", "KPI")
    user = payload.get("mysql_user", "")
    periodo = payload.get("periodo", "")
    n = int(payload.get("count", len(rows)))
    trunc = bool(payload.get("truncated"))
    intro = (
        f"**Detalle KPI ingresos** · `{vista}`"
        f"{f' · usuario `{user}`' if user else ''}\n\n"
        f"**Periodo:** {periodo} · **Filas (devueltas):** {len(rows)}"
        f"{f' de {n} totales' if trunc else ''}\n\n"
    )
    if not rows:
        return intro + "Sin filas."

    preferred = [
        "branch_office_id",
        "date",
        "año",
        "periodo",
        "metrica",
        "cash_amount",
        "cash_net_amount",
        "card_amount",
        "card_net_amount",
        "subscribers",
        "ticket_number",
    ]
    first = rows[0]
    if not isinstance(first, dict):
        return intro + "Datos no tabulares."
    rest = sorted(k for k in first if k not in preferred)
    keys = [k for k in preferred if k in first] + rest[: max(0, 12 - len(preferred))]
    keys = keys[:12]

    headers = [k.replace("_", " ") for k in keys]
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    head = "| " + " | ".join(headers) + " |"
    lines = [intro, head, sep]
    for r in rows:
        if not isinstance(r, dict):
            continue
        lines.append("| " + " | ".join(_md_cell(r.get(k)) for k in keys) + " |")
    out = "\n".join(lines)
    if trunc:
        out += f"\n\n*Tabla truncada a {len(rows)} filas; hay más en la base.*"
    return out


def _format_distribucion_sucursales_es(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        rows = []
    total = int(payload.get("total_sucursales", 0))
    dim_label = str(payload.get("dimension_etiqueta") or "Grupo")
    vista = payload.get("tabla_o_vista", "QRY_BRANCH_OFFICES")
    user = payload.get("mysql_user", "")
    solo_act = payload.get("solo_activas", True)
    act_txt = "activas (status_id = 7)" if solo_act else "todas las filas de la vista"
    intro = (
        f"**MySQL** · vista `{vista}` · agrupado por **{dim_label}**"
        f"{f' · usuario `{user}`' if user else ''}.\n\n"
        f"**Total de sucursales ({act_txt}):** {total}.\n\n"
    )
    if not rows or total == 0:
        return intro + "No hay datos para mostrar la distribución."

    head = f"| {dim_label} | Cantidad | % del total |"
    sep = "| --- | ---: | ---: |"
    lines = [intro, head, sep]
    for r in rows:
        if not isinstance(r, dict):
            continue
        g = _md_cell(r.get("grupo"))
        c = r.get("cantidad", 0)
        pct = r.get("porcentaje", 0)
        lines.append(f"| {g} | {c} | {pct} % |")
    lines.append("")
    lines.append("*Los porcentajes suman 100 % sobre el total indicado (redondeo a 2 decimales).*")
    return "\n".join(lines)


def _format_sucursales_solo_conteo(payload: dict[str, Any]) -> str:
    rows = payload.get("data") or []
    if not isinstance(rows, list):
        rows = []
    count = int(payload.get("count", len(rows)))
    vista = payload.get("tabla_o_vista", "QRY_BRANCH_OFFICES")
    filtro = payload.get("filtro", "")
    solo_act = payload.get("solo_activas", True)
    user = payload.get("mysql_user", "")
    act_txt = "activas (status_id = 7)" if solo_act else "que cumplen el filtro (incluye no activas si aplica)"
    base = (
        f"**MySQL** · vista `{vista}`"
        f"{f' · usuario `{user}`' if user else ''}.\n\n"
    )
    if count == 0:
        msg = base + f"No hay sucursales {act_txt} con los criterios indicados."
        fa = payload.get("filtros_aplicados") or {}
        if isinstance(fa, dict) and fa.get("responsable_contiene"):
            msg += (
                "\n\n*Sugerencia:* prueba una sola palabra del apellido o sin tilde (Gomez/Gómez), "
                "según cómo esté en la base."
            )
        if filtro:
            msg += f"\n\n*Filtro aplicado:* {filtro}"
        return msg
    msg = base + f"**Total: {count}** sucursales {act_txt}."
    if filtro:
        msg += f"\n\n*Criterios:* {filtro}"
    return msg


def _format_sucursales_respuesta_es(payload: dict[str, Any]) -> str:
    modo = str(payload.get("modo_respuesta") or "listar").strip().lower()
    if modo == "contar":
        return _format_sucursales_solo_conteo(payload)

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
    if count == 1 and rows and isinstance(rows[0], dict):
        r0 = rows[0]
        intro += (
            f"**Resumen:** ID sucursal (`branch_office_id`) = {_md_cell(r0.get('branch_office_id'))}, "
            f"código DTE (`dte_code`) = {_md_cell(r0.get('dte_code'))}, "
            f"nombre (`branch_office`) = {_md_cell(r0.get('branch_office'))}.\n\n"
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
            pr = (fa.get("principal_contiene") or fa.get("marca_contiene") or "").strip()
            suc = (fa.get("sucursal_contiene") or fa.get("nombre_sucursal_contiene") or "").strip()
            loc = (fa.get("local_marca_o_comuna_contiene") or "").strip()
            if pr and not suc and not loc:
                msg += (
                    "\n\n*Si el texto era el nombre del local (columna branch_office), vuelve a consultar con "
                    "**sucursal_contiene**, no con marca.*"
                )
        return msg

    show = rows[:_MAX_SUCURSALES_TABLA]
    truncated = len(rows) > _MAX_SUCURSALES_TABLA
    headers = [
        "ID",
        "Nombre",
        "Responsable",
        "DTE",
        "Dirección",
        "Región",
        "Comuna",
        "Marca",
        "Zona",
        "Segmento",
        "Vis.",
        "Estado",
    ]
    keys: list[str] = [
        "branch_office_id",
        "branch_office",
        "responsable",
        "dte_code",
        "direccion",
        "region",
        "commune",
        "marca",
        "zona",
        "segmento",
        "visibility_id",
        "status_id",
    ]
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
    """Tras ejecutar tools: respuesta fija desde MySQL (sin segunda pasada LLM; evita bucles con Ollama)."""
    last = state["messages"][-1]
    if not isinstance(last, ToolMessage):
        return {}
    try:
        payload = json.loads(last.content) if isinstance(last.content, str) else json.loads(str(last.content))
    except (json.JSONDecodeError, TypeError):
        return {}
    if not isinstance(payload, dict):
        return {}

    tname = getattr(last, "name", None) or ""

    def _err_ai(msg: str) -> dict[str, list[AIMessage]]:
        return {"messages": [AIMessage(content=f"**{tname or 'Consulta'}:** {msg}")]}

    if payload.get("success") is False:
        err = payload.get("error", "No se pudo completar la consulta.")
        if tname == _INFORME_VENTAS_TOOL or (
            _tool_is_ranking_sucursales(last)
            or _tool_is_resumen_ejecutivo(last)
            or _tool_is_evolucion_temporal(last)
            or _tool_is_consultar_kpi(last)
            or _tool_is_ventas_diarias(last)
            or _tool_is_depositos_listado(last)
            or _tool_is_depositos_resumen(last)
            or _tool_is_abonados_listado(last)
            or _tool_is_abonados_resumen(last)
        ):
            return _err_ai(str(err))
        return {}

    if not payload.get("success"):
        return {}

    if _tool_is_distribucion_sucursales(last):
        text = _format_distribucion_sucursales_es(payload)
        return {"messages": [AIMessage(content=text)]}
    if _tool_is_listar_sucursales(last):
        text = _format_sucursales_respuesta_es(payload)
        return {"messages": [AIMessage(content=text)]}
    if _tool_is_ranking_sucursales(last):
        return {"messages": [AIMessage(content=_format_ranking_sucursales_es(payload))]}
    if _tool_is_resumen_ejecutivo(last):
        return {"messages": [AIMessage(content=_format_resumen_ejecutivo_es(payload))]}
    if _tool_is_evolucion_temporal(last):
        return {"messages": [AIMessage(content=_format_evolucion_temporal_es(payload))]}
    if _tool_is_informe_ventas_comparativo(last):
        return {"messages": [AIMessage(content=_format_informe_ventas_comparativo_es(payload))]}
    if _tool_is_consultar_kpi(last):
        return {"messages": [AIMessage(content=_format_consultar_kpi_es(payload))]}
    if _tool_is_ventas_diarias(last):
        return {"messages": [AIMessage(content=_format_ventas_diarias_es(payload))]}
    if _tool_is_depositos_listado(last):
        return {"messages": [AIMessage(content=_format_depositos_listado_es(payload))]}
    if _tool_is_depositos_resumen(last):
        return {"messages": [AIMessage(content=_format_depositos_resumen_es(payload))]}
    if _tool_is_abonados_listado(last):
        return {"messages": [AIMessage(content=_format_abonados_listado_es(payload))]}
    if _tool_is_abonados_resumen(last):
        return {"messages": [AIMessage(content=_format_abonados_resumen_es(payload))]}
    return {}


def route_after_tools(state: AgentState) -> Literal["model", "end"]:
    """Si after_tools insertó un AIMessage de respuesta fija, terminar (no volver al LLM)."""
    msgs = state["messages"]
    if len(msgs) < 2:
        return "model"
    last, prev = msgs[-1], msgs[-2]
    if isinstance(last, AIMessage) and not (last.tool_calls or []) and isinstance(prev, ToolMessage):
        return "end"
    return "model"


def coerce_ollama_text_tool_calls(message: AIMessage) -> AIMessage:
    """Ollama/Qwen a veces devuelve la invocación como texto JSON sin rellenar tool_calls."""
    if message.tool_calls:
        return message
    raw = message.content
    if not isinstance(raw, str) or not raw.strip():
        return message

    def _decode_candidate(candidate: str) -> Any | None:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return _first_json_value(candidate)

    for candidate in _json_candidates_from_text(raw):
        data = _decode_candidate(candidate)
        if data is None:
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
