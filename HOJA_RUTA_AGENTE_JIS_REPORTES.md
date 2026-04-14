# Hoja de ruta — Agente JIS Reportes (MySQL + Streamlit)

Documento vivo para alinear sesiones de desarrollo: qué ya está hecho, qué falta y cómo extender el patrón de **sucursales** al resto de reportes.

**Rutina:** al terminar una sesión de trabajo en el agente o Streamlit, añadir un bloque **Avances — sesión YYYY-MM-DD** y actualizar **Pendiente para próxima sesión** + pie de **Última actualización**.

---

## Propósito

- **Objetivo del agente:** responder con datos reales desde MySQL (misma línea que Navicat con `reader_user`), en español, sin inventar filas ni cifras.
- **Objetivo de producto:** que el usuario pueda preguntar en lenguaje natural (listar, filtrar, contar, KPIs) y reciba respuestas **correctas** y, cuando corresponda, **concisas**.

---

## Avances — sesión 2026-04-08

### Conectividad y entorno

- Alineación de variables entre raíz del repo y `framework/agent-service-toolkit/.env` (MySQL vía túnel, Ollama, etc.).
- Scripts de arranque: `scripts/run_agent_service.ps1`, `scripts/run_streamlit.ps1`.
- Verificación: `scripts/verify_connectivity.py` (incluye comprobaciones útiles contra el servicio cuando está levantado).
- Pin de **`aiosqlite>=0.20,<0.22`** por compatibilidad con checkpoint SQLite de LangGraph.

### Agente `jis-reports` y herramientas MySQL

- Tool **`jis_listar_sucursales`** sobre la vista **`QRY_BRANCH_OFFICES`**: filtros opcionales mapeados desde español a columnas reales, `solo_activas` / `status_id`, metadatos en JSON (`count`, `data`, `filtros_aplicados`, etc.).
- **Responsable / nombre:** reglas 3+ / 2 / 1 palabra para `LIKE` (alineado Navicat).
- **Anti-alucinación (inicial):** nodo **`after_tools`** para listado y distribución de sucursales: respuesta determinista en markdown, sin segundo pase del LLM.
- **Ollama / tools en texto:** `coerce_ollama_text_tool_calls` con soporte para bloques y tags `<tool_response>`, `<tool_call>`.

### Documentación y DX

- Ajustes en `README.md`, `PLAN_DESARROLLO_JIS_2.0.md`, `.env.example`, docs del toolkit.
- `PLAN_CATALOGO_DB_Y_HERRAMIENTAS.md`, `JIS_DB_MAP.md`, `docs/CASOS_PRUEBA_SUCURSALES.md`.

---

## Avances — sesión 2026-04-09

### Scripts PowerShell (Windows)

- **`run_streamlit.ps1`:** reemplazo de guión Unicode (em dash) que rompía el parser; invocación **`.\venv\Scripts\python.exe -m streamlit run`** para no depender del PATH si el venv no está activado; parámetro **`-SkipTunnel`** (ya existente) documentado en flujo con `run_dev.ps1`.
- **`create_venv.ps1`:** mismo ajuste de carácter ASCII en un mensaje.
- **UTF-8 con BOM** en todos los `scripts/*.ps1` para que mensajes con tildes (ej. `[túneles]`) no salgan como `[tÃºneles]` en PowerShell 5.1.

### Búsqueda por nombre de sucursal vs marca (`jis_tools.py` + prompt)

- Si **`marca_contiene` / `principal_contiene`** tiene **2+ palabras** (ej. «LIDER CORDILLERA»), el filtro pasa a **`(principal LIKE … OR branch_office LIKE …)`** porque el nombre del local suele estar en **`branch_office`** y la marca corta en **`principal`**.
- Prompt del agente: **regla de oro** — el texto que da el usuario casi siempre es **`branch_office`**; para **id**, **dte_code**, **código de local** usar **`sucursal_contiene`**; **`codigo_dte_contiene`** solo cuando el usuario trae trozos del código DTE, no el nombre del local.
- **Una fila** en listado: bloque **Resumen** con `branch_office_id`, `dte_code`, `branch_office`.
- **Cero resultados** filtrando solo por marca: sugerencia de reintentar con **`sucursal_contiene`**.

### Ollama — JSON de tool repetido / concatenado

- **`_first_json_value`:** usa `json.JSONDecoder().raw_decode` para tomar el **primer objeto JSON** cuando el modelo pega varios `{...}{...}` sin separador (antes fallaba `json.loads` y no se ejecutaba la tool).
- **Instrucciones del agente:** una sola invocación por turno; no volcar JSON de herramienta en el texto.
- **Streamlit:** para el agente **`jis-reports`**, **`stream_tokens=False`** en `astream` para no inundar la UI con tokens que son JSON de tool.

### Bucle infinito `model ↔ tools` (ranking / KPI)

- **Causa:** tras tools como **`jis_ranking_sucursales`**, el grafo volvía al LLM; Ollama/Qwen **re-disparaba** la misma tool muchas veces.
- **Solución:** extender **`after_tools`** con formato fijo en español (markdown) para:
  - `jis_ranking_sucursales`
  - `jis_obtener_resumen_ejecutivo`
  - `jis_obtener_evolucion_temporal`
  - `jis_consultar_kpi_ingresos`
- En **`success: false`** en esas herramientas, **`after_tools`** devuelve un **`AIMessage`** con el error (evita reintentos ciegos del modelo).
- **`route_after_tools`:** si el último mensaje es **`AIMessage` sin `tool_calls`** y el anterior es **`ToolMessage`**, ir a **`END`** (respuesta generada en `after_tools`, sin segunda pasada LLM).
- **`agent.compile(recursion_limit=…)`** se **revirtió**: la versión instalada de LangGraph **no acepta** ese argumento en `compile()`; el tope de recursión habría que documentarlo al **upgrade** del paquete o pasarlo en **`invoke`** si la API lo permite.

---

## Estado actual (archivos clave)

| Área | Ruta principal |
|------|----------------|
| Grafo, prompt, coerción Ollama, formateo post-tool (sucursales, KPI, ventas, depósitos) | `framework/agent-service-toolkit/src/agents/jis_reports_agent.py` |
| Tools MySQL | `framework/agent-service-toolkit/src/agents/jis_tools.py` |
| Registro del agente | `framework/agent-service-toolkit/src/agents/agents.py` |
| LLM / Ollama | `framework/agent-service-toolkit/src/core/llm.py`, `settings.py` |
| API + streaming SSE | `framework/agent-service-toolkit/src/service/service.py` |
| UI chat (stream_tokens off para `jis-reports`) | `framework/agent-service-toolkit/src/streamlit_app.py` |
| Informe ventas en Streamlit (tabla con formato moneda) | `framework/agent-service-toolkit/src/streamlit_jis_informe_ventas.py` |
| Scripts arranque Windows | `scripts/*.ps1` |
| Frases de prueba / demos (chat) | `docs/PREGUNTAS_CHATBOT_REVISADAS.md` |
| RAG JIS (Chroma + embeddings Ollama + tool + síntesis) | `framework/agent-service-toolkit/src/agents/jis_rag_tools.py`, `jis_reports_agent.py` (nodos `rag_synthesize`, heurísticas `_RAG_*`) |
| Ingesta índice vectorial | `framework/agent-service-toolkit/scripts/build_jisparking_rag.py`, `scripts/run_build_jisparking_rag.ps1` |
| OCR opcional imagen → `.txt` corpus | `framework/agent-service-toolkit/scripts/image_to_jisparking_knowledge.py` (grupo `rag_ocr` en `pyproject.toml`) |
| Corpus documental (Markdown/PDF) | `framework/agent-service-toolkit/data/jisparking_knowledge/` |

---

## Avances — sesión 2026-04-13 (RAG conocimiento JIS + protocolos)

### Objetivo de producto

- Complementar MySQL con **conocimiento documental** (reglamento interno, **PROT-SC-001**, formularios **FORM-SC-001** / **FORM-SC-002**) para preguntas conceptuales o procedimentales sin cifras de BD.

### Implementación técnica (toolkit)

- **`jis_rag_tools.py`:** tool **`jis_buscar_conocimiento_jisparking`** — Chroma persistente (`JIS_RAG_CHROMA_PATH`, por defecto `chroma_jisparking/` junto al toolkit), **`OllamaEmbeddings`** con `OLLAMA_EMBED_MODEL` (default `nomic-embed-text`) y mismo **`OLLAMA_BASE_URL`** que el chat.
- **`settings.py`:** `OLLAMA_EMBED_MODEL`, `JIS_RAG_CHROMA_PATH`, `JIS_RAG_TOP_K`.
- **`build_jisparking_rag.py`:** ingesta `.md`, `.txt`, `.pdf`, `.docx`; `load_dotenv` opcional; **preflight** `embed_query("ping")` **antes** de borrar Chroma; nota sobre imágenes → OCR.
- **`run_build_jisparking_rag.ps1`:** crea/uso de `.venv` en el toolkit, `pip install -e .`, ejecuta el build (mensaje de requisitos Ollama).
- **`smoke_test_jisparking_rag.py`:** prueba rápida del índice sin cargar `Settings` del servicio completo.
- **`agents.py`:** descripción de **`jis-reports`** ampliada (MySQL + RAG documental).

### Grafo `jis_reports_agent` (Ollama + anti-bucle RAG)

- **Inyección heurística** cuando el modelo no emite `tool_calls`: patrón **`_RAG_DOC_LEX`** (reglamento, documentación indexada, **PROT-SC-001**, protocolo de atención, patio / inicio de jornada, centro de pago, cajero, pérdida de ticket, siniestro, cámaras, formularios SC, etc.); **`_RAG_SKIP_LEX`** evita mezclar con intenciones típicas SQL.
- **`_rag_tool_ran_after_last_human`:** evita **re-inyectar** la misma tool RAG en cada pasada al modelo (causa de bucles repetidos en Streamlit).
- **`after_tools`:** para la tool RAG **no** devuelve markdown crudo hacia `END` directo: **`route_after_tools`** deriva a nodo **`rag_synthesize`**.
- **`rag_synthesize`:** segunda pasada **LLM sin `bind_tools`** — resume extractos en prosa (español Chile/neutro, sin voseo rioplatense en el system prompt); fallback a extractos con encabezado si falla el modelo.
- **Instrucciones del agente:** reglas RAG vs SQL; anti-negación si ya hay fragmentos; ajuste de redacción interna del prompt (menos voseo en imperativos hacia el modelo).

### Documentación y datos en repo

- **`docs/PREGUNTAS_CHATBOT_REVISADAS.md`:** bloque **Streamlit local** (API + `AGENT_URL`, agente `jis-reports`); sección **§8** ampliada (reglamento, protocolos, formularios, cruces); checklist con filas RAG; nota de palabras clave que disparan RAG sin decir «reglamento».
- **`.env.example` del toolkit:** variables RAG / embeddings comentadas.
- **Corpus:** reglamento PDF + `servicio_cliente_protocolos_atencion.md`, `servicio_cliente_formulario_perdida_ticket.md`, `servicio_cliente_formulario_siniestro.md` (sincronizados desde CEREBRO_JIS hacia `data/jisparking_knowledge/`); índice de referencia **268 chunks** tras último build documentado por el equipo.

### Criterios de “hecho” ampliados (esta sesión)

- [x] RAG consultable desde Streamlit con **una** invocación de tool y respuesta **sintetizada** (sin bucles).
- [x] Preguntas operativas de protocolo (**patio**, **inicio de jornada**) cubiertas por heurística si el LLM no llama la tool.

---

## Patrón a replicar (checklist por nuevo reporte)

1. **Vista o consulta SQL acotada** en MySQL (solo columnas necesarias, `reader_user` con permisos de lectura).
2. **Tool dedicada** en `jis_tools.py`: argumentos claros, validación, límite razonable de filas, JSON con `success`, `count`, `data`, `error`, `tabla_o_vista`, metadatos útiles.
3. **Registro** en `tools` del agente y en **`_TOOL_NAMES`** / **`_tool_calls_from_json_obj`** si el nombre es nuevo.
4. **Prompt:** cuándo usar la tool, mapeo español → argumentos, anti-alucinación.
5. **Recomendación fuerte (JIS + Ollama):** si el resultado es tabular y estable, añadir **formatter en `after_tools`** + que **`route_after_tools`** cierre en **`END`** para no depender del LLM en el segundo paso.
6. **Pruebas:** misma consulta en Navicat vs agente (conteo y muestra).

---

## Criterios de “hecho” para cerrar una fase

- [ ] Paridad conteo/filas con Navicat en casos de referencia acordados.
- [ ] Sin JSON de tool visible como respuesta final (salvo depuración explícita).
- [ ] Respuesta en español; números y nombres coinciden con el JSON de la tool.
- [ ] Sin bucles de invocación de la misma tool en un solo turno (Ollama).
- [ ] Comportamiento definido para **listar** vs **contar** cuando el usuario lo pide explícitamente.
- [ ] Preguntas RAG típicas (reglamento, protocolos SC) responden con **base en documentos indexados**, sin negar acceso si el índice existe.

---

## Notas

- Rotar credenciales si en algún momento se compartieron `.env` en chat o capturas.
- Tras cambios en Python del toolkit, **reiniciar** el servicio FastAPI del agente (y Streamlit) para cargar código nuevo.
- Tras agregar o editar archivos en **`data/jisparking_knowledge/`**, ejecutar **`run_build_jisparking_rag.ps1`** y reiniciar el API; embeddings deben coincidir (**`OLLAMA_EMBED_MODEL`** / **`OLLAMA_BASE_URL`**) entre build y runtime.
- Los códigos ANSI (`←[32m`) en consola Windows son normales; para log limpio se puede usar `NO_COLOR` o política de logging de uvicorn.

---

## Avances — sesión 2026-04-10 (informes de ventas)

- Nueva tool **`jis_consultar_ventas_diarias`**: consulta **`KPI_INGRESOS_DIARIO`** (periodo `Diario`) con join a **`QRY_BRANCH_OFFICES`**, rango `fecha_desde` / `fecha_hasta` (máx. 93 días), `metrica` `ingresos` o `ppto`, filtro opcional por sucursal (id o nombre).
- Prompt del agente: sección **“Informes de ventas”** y filas en la matriz decisión (mensual vs diario vs presupuesto).
- **`after_tools`**: formateo fijo + cierre en `END` para ventas diarias (mismo patrón anti-bucle Ollama).
- **`jis_consultar_kpi_ingresos`**: si faltan vars de entorno, JSON con **`success: false`** (antes solo `error`).
- **`jis_informe_ventas_comparativo`**: mismo mes, años **N** y **N−1**, métricas **ingresos** (proxy efectivo+tarjeta+abonados) y **ppto**; agrupación **total** / **sucursal** / **responsable**; `after_tools` con tabla markdown (anti-bucle).
- Consultas mensuales que filtraban **`k.año IN (y, y−1)`** con un solo **MONTH** pasan a **`k.año = año consultado`** en resumen, ranking, KPI detalle y evolución (evita mezclar años en un mismo agregado).

### Pendiente relacionado (ventas; sigue abierto)

- [ ] Casos de prueba en `docs/` para ventas diarias y cuadro comparativo (Navicat vs agente).
- [ ] Si hace falta **QRY_PPTO_DIA** explícito además del mensual comparativo, valorar tool o argumentos extra.

---

## Avances — sesión 2026-04-16

### Streamlit — legibilidad del informe de ventas

- En **`streamlit_jis_informe_ventas.py`**: columnas de montos (**Ingresos**, **Presupuesto**, **T. prom.**) y tickets con formato legible; **Var %** / **Desv %** con manejo de `NaN`/`None` como «—».
- Nota de producto: al formatear como texto, el orden al clicar columnas en `st.dataframe` es lexicográfico (documentado en conversación; alternativa futura: `column_config` numérico).

### Documentación de producto / QA

- Nuevo **`docs/PREGUNTAS_CHATBOT_REVISADAS.md`**: frases listas para copiar (sucursales, informe de ventas, ventas diarias, otras tools, **depósitos**), notas de criterios (ranking bruto vs informe neto, exclusión OFICINA en depósitos).
- Checklist de demo ampliado (incluye fila depósitos).

### Dominio depósitos (MySQL + agente)

- **`jis_consultar_depositos`**: listado sobre **`QRY_REPORTE_DEPOSITOS`**, filtro por **Fecha_Recaudacion** (rango ISO o `year`+`month`), estado literal, `branch_office_id`, `sucursal_contiene`, `supervisor_contiene`, exclusión **OFICINA** por defecto, límites de filas y de rango de días.
- **`jis_resumen_depositos`**: agregados del mes (totales, suma **Diferencia**, promedio **Dias_Latencia**, conteo por **Estado_Deposito**).
- **`jis_reports_agent.py`**: tools registradas, prompt (matriz + sección depósitos), **`after_tools`** con tablas markdown y errores (`success: false`) para cierre en **`END`**.
- **`agents.py`**: descripción del agente `jis-reports` actualizada.

### Corrección MySQL 1267 (collations)

- En comparaciones de strings de la vista de depósitos: uso explícito de **`utf8mb4_unicode_ci`** alineado a la conexión (`_DEPOSITOS_STRING_COLLATE`), para evitar **Illegal mix of collations** (`utf8mb4_0900_ai_ci` vs `utf8mb4_unicode_ci`) en `=`, `LIKE`, exclusión OFICINA, `ORDER BY` y `GROUP BY` del resumen.

---

## Decisión — producción (2026-04-10)

- **Dónde corre el servicio:** **JIS Lab** (agente FastAPI + acceso a **Ollama** en el mismo entorno, sin depender de un túnel hacia el modelo).
- **MySQL:** sigue en el **VPS**; desde JIS Lab solo hace falta **túnel SSH** (o VPN cuando la tengan) hacia el puerto de la base.
- **Próxima tarea de infra:** empaquetar y levantar en **Docker** en JIS Lab (compose, `.env`, túnel persistente o equivalente, healthchecks) y dejar **runbook** de deploy. Ver checklist **E** abajo.

---

## Pendiente para próxima sesión (priorizado)

### A. Operación y DX

- [ ] **Documentar en README / `instrucciones.txt`:** orden típico (túneles → API :8080 → Streamlit), `AGENT_URL`, y que **`jis-reports` no usa stream de tokens** por defecto en Streamlit (y cómo reactivarlo si en el futuro hay toggle). *(Parcial: flujo Streamlit + RAG descrito en `docs/PREGUNTAS_CHATBOT_REVISADAS.md` y en esta hoja, sesión 2026-04-13.)*
- [ ] **Opcional:** enlace desde README a **`docs/PREGUNTAS_CHATBOT_REVISADAS.md`** para demos y regresión.
- [ ] **Opcional:** toggle en Streamlit “Stream de tokens (experimental; Ollama puede mostrar JSON)” solo cuando no sea `jis-reports`, o siempre con aviso.
- [ ] **Safeguard:** con `GROQ_API_KEY` vacío el log dice *skipping Safeguard* — decidir si se acepta en dev, si se usa otro proveedor, o si se silencia el mensaje en producción.

### B. Robustez del agente y tests

- [ ] **Tests unitarios:** `_first_json_value`, detección `_tool_is_*`, y al menos un formatter (ranking o depósitos) con JSON de ejemplo.
- [ ] **LangGraph:** tras actualizar dependencias, revisar si **`compile(recursion_limit=…)`** o equivalente en `invoke` aplica; fijar un tope razonable anti-bucle como red de respaldo.

### C. Producto y datos

- [ ] **RAG — más corpus:** copiar nuevos `.md`/`.pdf` a `data/jisparking_knowledge/` y re-ejecutar `run_build_jisparking_rag.ps1`; para **solo imagen** usar `image_to_jisparking_knowledge.py` + Tesseract o transcripción manual. Valorar **`servicio_cliente_siniestros_registro_procedimiento.md`** si se quiere paridad con enlaces del protocolo.
- [ ] **RAG — calidad:** regresión automática o script que compare preguntas §8 vs fragmentos mínimos esperados (sin depender solo de demos manuales).
- [ ] **`docs/CASOS_PRUEBA_DEPOSITOS.md`** (o sección en PREGUNTAS): matrices Navicat vs agente — pendientes, filtro sucursal, resumen mensual, con/sin OFICINA.
- [ ] **Validar en BD real** que los literales de **`Estado_Deposito`** coinciden con **`_ESTADOS_DEPOSITO_CANON`**; ajustar constantes si la vista usa variantes.
- [ ] **Actualizar `docs/CASOS_PRUEBA_SUCURSALES.md`** (o doc KPI): ranking top N, resumen mes, evolución una sucursal; criterio = una tool + respuesta final sin bucles.
- [ ] **Siguiente dominio** según `PLAN_CATALOGO_DB_Y_HERRAMIENTAS.md`: **abonados / DTE** (`CABECERA_ABONADOS` + joins) o **rendiciones** — misma receta: tool + JSON + prompt + `after_tools` si aplica.
- [ ] Revisión fina **`jis_consultar_kpi_ingresos`:** columnas mostradas en markdown (subset de 12); ampliar o documentar truncamiento si usuarios piden más campos.
- [ ] **Opcional UX:** componente Streamlit rico para depósitos (similar al informe de ventas) si el markdown en chat no alcanza para gerencia.

### D. QA continuo

- [ ] Casos **ventas diarias** e **informe comparativo** en `docs/` (Navicat vs agente) — pendiente desde sesión 2026-04-10.
- [ ] **`modo_respuesta="contar"`** en `jis_listar_sucursales` — validar que el modelo lo use en “¿cuántas…?”.
- [ ] **Túnel MySQL / Ollama:** sin túnel, fallos 10061; mantener mensajes claros en `verify_connectivity.py` y en UI si se desea.

### E. Deploy JIS Lab (Docker + producción)

- [ ] **Docker en JIS Lab:** imagen(es) o `docker compose` para el **servicio del agente** (puerto API, p. ej. 8080); opcional **Streamlit** en el mismo compose o detrás de reverse proxy según producto.
- [ ] **Variables y red:** `.env` en el host o vía secrets; `DB_HOST`/`DB_PORT` apuntando al **extremo local del túnel** hacia MySQL en el VPS; documentar mismo criterio que `instrucciones.txt` (sin túnel → errores tipo 10061).
- [ ] **Persistencia del túnel:** `autossh`, unidad **systemd**, o `restart: always` en un contenedor sidecar que mantenga el forward; reconexión ante caída de red.
- [ ] **Runbook corto:** orden de arranque (túnel → API → UI), healthcheck HTTP, y **prueba de humo** con `docs/PREGUNTAS_CHATBOT_REVISADAS.md`.

---

## Pendiente resuelto (referencia rápida)

| Tema | Dónde / cuándo |
|------|----------------|
| `jis_consultar_kpi_ingresos` sin `success: false` si faltan vars entorno | Corregido sesión 2026-04-10 |
| Herramientas **depósitos** + anti-bucle `after_tools` | Sesión 2026-04-16 |
| Collation mix en `QRY_REPORTE_DEPOSITOS` | Sesión 2026-04-16 (`_DEPOSITOS_STRING_COLLATE`) |
| **RAG** Chroma + Ollama embeddings + tool + síntesis sin bucles | Sesión 2026-04-13 |
| Heurística RAG para **protocolo / patio / ticket / siniestro** sin palabra «reglamento» | Sesión 2026-04-13 |

---

*Última actualización: 2026-04-13. Mantener este archivo al cierre de cada sesión de trabajo en el agente / Streamlit.*
