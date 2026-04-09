# Hoja de ruta — Agente JIS Reportes (MySQL + Streamlit)

Documento vivo para alinear sesiones de desarrollo: qué ya está hecho, qué falta y cómo extender el patrón de **sucursales** al resto de reportes.

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
- **Responsable / nombre:**
  - **3+ palabras significativas** → un solo `LIKE` con la frase completa (mismo criterio que Navicat: `'%nombre completo%'`).
  - **2 palabras** (ej. «david gomez») → ambas deben aparecer (`AND` de `LIKE` por token).
  - **1 palabra** → un `LIKE`.
- **Anti-alucinación:** nodo **`after_tools`**: tras listar sucursales con éxito, respuesta determinista en markdown desde el JSON (tabla + total), sin segundo pase del LLM para ese caso.
- **Ollama / modelos que escriben tools en texto:** `coerce_ollama_text_tool_calls` ahora entiende JSON dentro de `<tool_response>...</tool_response>` y `<tool_call>...</tool_call>`, de modo que la invocación se ejecuta de verdad y no se queda el JSON colgado en el chat.

### Documentación y DX

- Ajustes en `README.md`, `PLAN_DESARROLLO_JIS_2.0.md`, `.env.example`, temperatura Ollama en settings, mejoras menores en cliente Streamlit donde aplica.

### Verificación manual reciente (referencia)

- Consulta tipo Navicat: `status_id = 7` + responsable con frase completa → mismos conteos esperados (ej. **9** sucursales para «David Wilder Gomez Figueroa» al listar activas).

---

## Estado actual (archivos clave)

| Área | Ruta principal |
|------|----------------|
| Definición del grafo, prompt, coerción Ollama, formateo post-tool listado | `framework/agent-service-toolkit/src/agents/jis_reports_agent.py` |
| Tools MySQL (sucursales, KPI ingresos) | `framework/agent-service-toolkit/src/agents/jis_tools.py` |
| Registro del agente por defecto | `framework/agent-service-toolkit/src/agents/agents.py` |
| LLM / Ollama | `framework/agent-service-toolkit/src/core/llm.py`, `settings.py` |
| API + streaming SSE | `framework/agent-service-toolkit/src/service/service.py` |
| UI chat | `framework/agent-service-toolkit/src/streamlit_app.py` |

---

## Patrón a replicar (checklist por nuevo reporte)

Para cada nuevo tipo de dato (ventas, abonados, depósitos, rendiciones, etc.):

1. **Vista o consulta SQL acotada** en MySQL (solo columnas necesarias, `reader_user` con permisos de lectura).
2. **Tool dedicada** en `jis_tools.py`: argumentos claros, validación, límite razonable de filas, JSON con `success`, `count`, `data`, `error`, `tabla_o_vista`, `filtro` / `filtros_aplicados`.
3. **Registro en** `tools` del agente y en `_TOOL_NAMES` / `_tool_calls_from_json_obj` si se añaden nombres nuevos.
4. **Prompt** en `jis_reports_agent.py`: cuándo usar la tool, mapeo español → argumentos, reglas anti-alucinación.
5. **Opcional pero recomendable:** rama **`after_tools`** + **`route_after_tools`** para respuestas **deterministas** (tabla o resumen fijo) cuando el resultado sea estructurado y repetitivo.
6. **Pruebas:** misma consulta en Navicat vs respuesta del agente (conteo y muestra de filas).

---

## Próxima sesión — prioridades sugeridas

### 1. Respuestas concisas cuando solo piden un conteo

**Problema:** Hoy, tras «lista sucursales de X», la UI muestra tabla completa (correcto para «lista»). Si el usuario dice **«¿cuántas sucursales tiene David?»**, lo deseable es algo como: *«David Wilder Gomez Figueroa tiene 9 sucursales activas (status_id = 7).»* sin tabla obligatoria.

**Enfoque posible:**

- Detectar intención de **solo conteo** (prompt +/o parámetro explícito en la tool, ej. `solo_resumen: bool` o `modo: "listar" | "contar"`).
- En **`after_tools`** (o nodo hermano): si `modo=contar`, generar **solo** párrafo con `count` y filtros; si `modo=listar`, mantener tabla actual.
- Alternativa: dejar que el LLM resuma solo cuando `count` es pequeño — **menos determinista**; preferir camino estructurado si queremos cero desvíos.

### 2. Nuevos reportes (mismo estándar que sucursales)

Definir con negocio las **vistas o queries** y replicar el patrón:

- Ventas (agregados / detalle por periodo y sucursal).
- Abonados.
- Depósitos.
- Rendiciones.
- (Otros que definan en `PLAN_DESARROLLO_JIS_2.0.md`.)

Para cada uno: tool + JSON + prompt + (opcional) formateo fijo post-tool.

### 3. Depuración fina

- Revisar **`jis_consultar_kpi_ingresos`**: mismo rigor de metadatos y, si aplica, respuesta determinista para tablas KPI.
- Unificar criterios de **activo / histórico** (`solo_activas`, `status_id`) en el prompt para que el modelo no contradiga la tool.
- Pruebas automáticas mínimas (mock MySQL o BD de prueba) para `_append_responsable_filters` y para la extracción `<tool_response>`.

### 4. UX streaming

- Con streaming activo puede verse un instante el texto crudo antes de ejecutar tools; valorar `stream_tokens=false` por defecto para este agente o filtrado de tokens que sean solo marcadores de tool.

---

## Criterios de “hecho” para cerrar una fase

- [ ] Paridad conteo/filas con Navicat en casos de referencia acordados.
- [ ] Sin JSON de tool visible como respuesta final (salvo depuración explícita).
- [ ] Respuesta en español; números y nombres coinciden con el JSON de la tool.
- [ ] Comportamiento definido para **listar** vs **contar** (cuando se implemente).

---

## Notas

- Rotar credenciales si en algún momento se compartieron `.env` en chat o capturas.
- Tras cambios en Python del toolkit, **reiniciar** el servicio FastAPI del agente (y Streamlit) para cargar código nuevo.

---

*Última actualización: 2026-04-08.*
