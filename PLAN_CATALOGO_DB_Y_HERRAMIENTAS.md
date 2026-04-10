# Plan detallado — Catálogo MySQL, herramientas y agente JIS Reportes 2.0

Este documento describe **cómo** llevar a cabo la actividad de mapear la base, diseñar herramientas por categoría y actualizar el flujo LangGraph + FastAPI + Streamlit. Complementa `HOJA_RUTA_AGENTE_JIS_REPORTES.md`.

---

## Objetivo

1. Tener un **inventario fiel** de schemas, tablas, vistas, columnas, índices y FKs (solo metadatos, sin volcar datos).
2. A partir de ese inventario, definir **qué preguntas** puede responder el sistema y con **qué tools**.
3. Organizar las tools en **tres familias** (inventario, resumen ejecutivo, ranking/tendencias).
4. Incorporar una **matriz de decisión** en las instrucciones del agente y en la lista `tools` de `jis_reports_agent.py`.
5. **Alinear JIS Reportes 2.0 con jisreportes.com:** mismas tablas/vistas y mismas reglas de negocio (filtros, estados, joins) para que respuestas del agente sean **comparables** con el dashboard y los PDFs actuales.

---

## Fuente de verdad — Datos que usa hoy jisreportes.com

Esta sección es la **referencia funcional** para diseñar `jis_tools.py` y el prompt del agente. El catálogo técnico sigue siendo `JIS_DB_MAP.md` (introspección MySQL). Si hay divergencia entre nombres en código legacy y objetos en BD, **validar en MySQL** antes de fijar el SQL de una tool.

### Maestro común (todos los reportes)

| Objeto | Uso en jisreportes | Implicación JIS 2.0 |
|--------|-------------------|----------------------|
| **`QRY_BRANCH_OFFICES`** | Catálogo sucursales activas (`status_id = 7`): id, nombre, responsable, `dte_code`, marca/principal, zona, segmento, dirección, región, comuna; usada en GET `/sucursales`, login (sucursales accesibles), joins en ventas, abonados, depósitos y filtros por rol. | Ya cubierto por **`jis_listar_sucursales`**. Mantener criterio `status_id = 7` para “activas”; `solo_activas=false` cuando el negocio pida histórico/no activas. |
| **`users` + `branch_offices`** | Solo en GET `/sucursales_rut`: cruce usuario ↔ sucursal por supervisor (`principal_supervisor`). | Si el agente debe replicar “mis sucursales como usuario logueado”, hará falta **identidad** (user id / RUT) en el request o una tool que reciba `principal_supervisor` / lista de ids — hoy el chat anónimo no tiene sesión jisreportes; documentar como mejora futura. |
| Filtros típicos en reportes por responsable | Lista de `branch_office_id` del responsable vía **`QRY_BRANCH_OFFICES`** con `visibility_id = 1` y `status_id = 7`. | Cualquier tool de ventas/abonados/depósitos “por responsable” debe poder **restringir por ids de sucursal** derivados de la misma lógica que el legacy (o por nombre de responsable → ids). |

**Columnas `QRY_BRANCH_OFFICES` usadas explícitamente en API legacy (referencia):**

| Columna | Rol |
|---------|-----|
| `id` | ID sucursal (a menudo `branch_office_id` en APIs) |
| `branch_office` | Nombre |
| `responsable` | Supervisor comercial |
| `dte_code` | Código DTE |
| `principal` | Marca (API: marca) |
| `zone` | Zona (API: zona) |
| `segment` | Segmento (API: segmento) |
| `address` | Dirección (API: direccion) |
| `region` | Región |
| `commune` | Comuna |
| `status_id` | Típico `= 7` activas en reportes |
| `visibility_id` | Típico `= 1` en reportes filtrados por responsable |

---

### Reportes de ventas

| Objeto | Qué entrega / para qué sirve | Endpoints / pantallas legacy (referencia) | Tool JIS 2.0 (estado / propuesta) |
|--------|------------------------------|-------------------------------------------|-----------------------------------|
| **`KPI_INGRESOS_IMG_MES`** | Filas por fecha, año, `branch_office_id`, `periodo` (Mensual / Acumulado), `metrica` (`ingresos` / `ppto`), montos efectivo/tarjeta neto-bruto, `subscribers`, `ticket_number`, `ppto`, `clave`, `ind`, etc. | GET `/kpis/ingresos`, `/kpis/presupuesto`, POST `/kpis/evolucion_anual`, dashboard ejecutivo, GET `/kpi/*`. | **`jis_consultar_kpi_ingresos`** (parcial): ya usa esta tabla + join sucursales activas. Extender si se necesita **ppto** explícito o evolución anual como tool dedicada. |
| **`KPI_INGRESOS_DIARIO`** | Detalle día × sucursal; mismas familias de montos; `periodo = 'Diario'`; `metrica` ingresos/ppto. | GET `/ventas_diarias`, `/ventas_diarias/ingresos`, POST `/ventas_diarias/evolucion_diaria`. | **Nueva:** p. ej. `jis_consultar_ventas_diarias` (rango fechas, opcional sucursal, métrica). |
| **`QRY_PPTO_DIA`** | Presupuesto diario: `date`, `branch_office_id`, `ppto`. | GET `/ventas_diarias/ppto_diario`; meta diaria en ventas vs meta. | **Nueva:** o integrada en tool de ventas diarias / “real vs meta”. |
| **`CABECERA_TRANSACCIONES`** (tabla hechos; en el legacy se usa esta tabla para ETL y lecturas directas) | Hechos venta agregados día × sucursal: efectivo, tarjeta, abonados, tickets. Alimenta ETL hacia `KPI_INGRESOS_*`; lectura en proyección ML, ventas_vs_meta, `services.py`. | Flujos internos + análisis. | **Solo si** hace falta paridad con consultas que el legacy no pasó a KPI; preferir **KPI_*** para el agente salvo requisito explícito. |
| **`QRY_CABECERA_TRANSACCIONES`** | Vista en MySQL (aparece en `JIS_DB_MAP.md`): similar granularidad “cabecera” con dimensiones de sucursal. | Puede solaparse con tabla + joins. | Decidir una **única fuente** por tipo de pregunta tras validar con negocio. |
| **`PPTO_DIARIO`** | ETL hacia KPIs; en proyección se usa `cash_amount` agregado como ppto por día. | ETL / ML. | Baja prioridad para chat salvo tool de proyección. |
| **`QRY_IND_SSS`** | Join en ETL: clave mes/sucursal → campo `ind` en KPIs. | ETL. | No suele hacer falta exponer al agente; documentado para entender `ind` en `KPI_*`. |
| **`CALENDARIO_EVENTOS`** | Feriados (`categoria = 'Feriado'`) para modelo de proyección. | Proyección ventas. | Opcional: tool “feriados en rango” si se preguntan calendarios de negocio. |

**Columnas clave `KPI_INGRESOS_IMG_MES` (consumo SELECT típico):**

| Columna | Rol |
|---------|-----|
| `date` | Fecha referencia período |
| `periodo` | `Mensual` / `Acumulado` |
| `año` | Año calendario |
| `branch_office_id` | Sucursal |
| `clave` | Clave interna (sucursal + YYYYMM) |
| `ind` | Desde `QRY_IND_SSS` |
| `cash_amount` / `cash_net_amount` | Efectivo bruto / neto |
| `card_amount` / `card_net_amount` | Tarjeta bruta / neta |
| `subscribers` | Abonados ($) |
| `ticket_number` | Cantidad tickets/transacciones |
| `ppto` | Presupuesto cuando `metrica = 'ppto'` |
| `metrica` | `ingresos` o `ppto` |

**Responsable en pantalla:** no está en `KPI_*`; se obtiene por **join** con `QRY_BRANCH_OFFICES` (igual que debe hacer cualquier ranking “por supervisor”).

**Columnas clave `KPI_INGRESOS_DIARIO`:** `date`, `periodo` (= Diario), `año`, `branch_office_id`, `clave`, montos como arriba, `ppto`, `metrica`.

---

### Reporte de abonados (track DTEs / pendientes)

| Objeto | Uso | Implicación JIS 2.0 |
|--------|-----|----------------------|
| **`CABECERA_ABONADOS`** | Documentos abonados: fechas, folio, RUT, cliente, `branch_office_id`, `dte_type_id`, status / `status_id`, montos, period, comment, `payment_date`, etc. | **Nueva tool** listado/resumen abonados con filtros acotados (fecha, sucursal, estado). |
| **`dte_types`** | Catálogo tipo DTE; LEFT JOIN para nombre `document_type`. | Incluir en queries de abonados como en GET `/abonados`. |
| **`QRY_BRANCH_OFFICES`** | Join nombre sucursal; filtro por responsable / ids. | Reutilizar ids de sucursal del maestro. |

**Criterios útiles (replicar en tools / prompt):**

- Pendientes de pago (PDF/mes): `status = 'Imputada por pagar'`.
- Resumen DTE pendientes (`/kpi/dtes/resumen`): `status_id = 4`.
- Dashboard inicio (`get_kpi_dtes_resumen`): `LOWER(status) = 'imputada por pagar'` mes actual.

---

### Reporte de depósitos

**Fuente principal de negocio en BD para la mayoría de pantallas:** vista **`QRY_REPORTE_DEPOSITOS`**.

| Uso legacy | Comportamiento | Columnas / lógica |
|------------|----------------|-------------------|
| GET `/operations/deposit_report` | Agregación día × sucursal; **estado derivado** (Pendiente, Depositado con Diferencia, Depositado a Favor, Depositado Correcto); foco en filas “problemáticas”. | `Fecha_Recaudacion`, `Sucursal`, supervisor/responsable, montos, `Diferencia`, `Estado_Deposito`, `Dias_Latencia`, `branch_office_id`, … |
| GET `/kpi/depositos/resumen` | Conteo, suma diferencia, latencia promedio mes actual; alineado a dashboard; excluye OFICINA. | Misma vista; agregados en servicio. |
| GET `/reportes/depositos_pendientes` | Solo `Estado_Deposito = 'Pendiente'`. | |
| Reportes PDF / WhatsApp | Depósitos no “Depositado Correcto” ni “Depositado a Favor”; mes/año; sucursales del responsable. | |
| Filtro por responsable | **`QRY_BRANCH_OFFICES`**: `visibility_id = 1`, `status_id = 7` → lista `branch_office_id`. | |

**Tablas de soporte (ETL / hechos; no sustituyen la vista para el usuario final):**

- **`HECHOS_DEPOSITOS_DETALLE`**, **`DETALLE_DEPOSITOS_DIA`**, orígenes `deposits` / `collections` — documentadas para entender la vista; las tools del agente deberían preferir **`QRY_REPORTE_DEPOSITOS`** salvo necesidad de auditoría técnica.

---

### Mapa legacy → tools JIS 2.0 (hoja de ruta técnica)

| Dominio | Objetos BD | Herramienta objetivo (nombre sugerido) | Categoría taxonomía |
|---------|------------|----------------------------------------|---------------------|
| Sucursales | `QRY_BRANCH_OFFICES` | `jis_listar_sucursales` ✅ | Inventario |
| KPI ingresos/ppto mensual | `KPI_INGRESOS_IMG_MES` + BO | `jis_consultar_kpi_ingresos` ✅ (ampliar ppto/evolución si aplica) | Resumen / tendencia |
| Ventas diarias | `KPI_INGRESOS_DIARIO` | `jis_consultar_ventas_diarias` (nueva) | Inventario granular / tendencia |
| Meta diaria PPTO | `QRY_PPTO_DIA` | combinar con ventas diarias o tool `jis_consultar_ppto_diario` | Resumen |
| Depósitos | `QRY_REPORTE_DEPOSITOS` | `jis_consultar_depositos` (listado + filtros estado/fecha) | Inventario |
| KPI depósitos | misma vista + agregación | `jis_resumen_depositos` (nueva) o args en la anterior | Resumen ejecutivo |
| Abonados / DTEs | `CABECERA_ABONADOS` + `dte_types` + BO | `jis_listar_abonados` / `jis_resumen_abonados` (nuevas) | Inventario / resumen |
| Usuario ↔ sucursales | `users` + `branch_offices` | futura tool con contexto de usuario | Inventario |

---

### Coherencia con `JIS_DB_MAP.md`

- El mapper lista **todos** los objetos; este documento marca cuáles son **contrato de producto** con jisreportes.com.
- **`CABECERA_TRANSACCIONES`** vs **`QRY_CABECERA_TRANSACCIONES`:** el legacy en tu descripción usa la **tabla** para ETL y lecturas; el catálogo también muestra la **vista**. Al implementar una tool, elegir **un** origen y documentar en la firma de la tool.
- Reglas de estado (`status_id`, textos de `status`, estados de depósito) deben **copiarse literalmente** del legacy en SQL parametrizado (constantes en Python, no texto libre del LLM).

---

## Fase 0 — Prerrequisitos

| Paso | Acción |
|------|--------|
| 0.1 | `.env` en raíz y/o `framework/agent-service-toolkit/.env` con `DB_*` válidos (mismo criterio que `jis_tools.py`). |
| 0.2 | Túnel o acceso de red al MySQL si aplica. |
| 0.3 | Entorno Python con `mysql-connector-python` y `python-dotenv` (ya en `requirements.txt` / toolkit). |

Verificación rápida: `python scripts/verify_connectivity.py`.

---

## Fase 1 — Generar el catálogo (`JIS_DB_MAP.md`)

| Paso | Acción |
|------|--------|
| 1.1 | Ejecutar desde la raíz del repo: `python scripts/jis_db_mapper.py` |
| 1.2 | Por defecto se crea **`JIS_DB_MAP.md`** en la raíz. Opcional: `-o ruta/personalizada.md` |
| 1.3 | Si necesitas más de un schema: `python scripts/jis_db_mapper.py --schemas jisparking,otro_schema` |
| 1.4 | Revisar el archivo: priorizar vistas `QRY_*` o documentadas en legacy jisreportes. |
| 1.5 | **Git:** añadir `JIS_DB_MAP.md` al `.gitignore` si contiene nombres internos sensibles; si es aceptable para el equipo, versionarlo para que el equipo y el asistente compartan la misma referencia. |

**Qué incluye el script (solo lectura):**

- Tablas y vistas con tipo, motor, filas estimadas, comentarios de tabla.
- Columnas: nombre, tipo SQL, nulidad, key (PRI/MUL/UNI), default, extra, comentario.
- Claves foráneas salientes.
- Índices (nombre y columnas), útil para diseñar filtros eficientes.

**Qué no hace (por diseño):**

- No exporta filas ni muestras de datos (evita fugas y archivos enormes).
- No inventa significado de negocio: eso se documenta en Fase 2.

---

## Fase 2 — De catálogo a “diccionario de negocio”

Trabajo **humano + asistente** usando:

1. **Sección [Fuente de verdad — jisreportes.com](#fuente-de-verdad--datos-que-usa-hoy-jisreportescom)** (prioridad absoluta para paridad con dashboard/PDF).
2. **`JIS_DB_MAP.md`** (columnas e índices reales en el servidor).

| Paso | Acción |
|------|--------|
| 2.1 | Cruzar cada dominio (ventas, abonados, depósitos) con la tabla **Mapa legacy → tools** de arriba. |
| 2.2 | Por cada tool candidata, anotar: **pregunta de usuario**, **granularidad**, **riesgo** (RUT, montos, volumen), **constantes de negocio** (status, exclusiones tipo OFICINA). |
| 2.3 | Marcar objetos **fuera de alcance** del agente conversacional (ETL puro, ML, tablas masivas sin vista de reporte). |
| 2.4 | Mantener matriz “Pregunta → Objeto BD → Regla legacy → Tool” al implementar cada sprint. |

Resultado: lista priorizada de **nuevas tools** y extensiones a las existentes, **alineada a jisreportes.com**.

---

## Fase 3 — Categorías de herramientas (taxonomía)

### A) Inventario (lectura / “¿Qué tenemos?”)

- **Ejemplos:** sucursales, responsables, direcciones, estados, relaciones maestro-detalle legibles.
- **Patrón SQL:** `SELECT` con filtros opcionales, `LIMIT` defensivo, columnas explícitas.
- **Ejemplo actual:** `jis_listar_sucursales`.

### B) Resumen ejecutivo (cálculo / “¿Cuánto en total?”)

- **Ejemplos:** total de ingresos en un mes, suma por región, conteos agregados.
- **Patrón SQL:** `SUM`, `COUNT`, `AVG`, `GROUP BY` acotado, siempre con ventana de fechas o criterios obligatorios.
- **Tool ejemplo (a implementar):** `jis_obtener_resumen_ejecutivo` — definir args: métrica, dimensión opcional, rango de fechas, filtros de sucursal.

### C) Ranking y tendencias (comparación / “¿Quiénes destacan?” / “¿Sube o baja?”)

- **Ranking:** `ORDER BY` + `LIMIT`, mismos límites de seguridad que inventario.
- **Tendencia:** serie temporal (por día/semana/mes) con agregación; idealmente una vista o query revisada por negocio.
- **Tools ejemplo (a implementar):** `jis_ranking_sucursales`, `jis_obtener_evolucion_temporal`.

**Regla transversal:** cada tool devuelve JSON con `success`, `count` o métricas, `data`, `error`, `tabla_o_vista`, `filtros_aplicados` (como `jis_listar_sucursales`) para que `after_tools` o el LLM formateen sin inventar.

---

## Fase 4 — Matriz de decisión para el agente

Actualizar **`jis_reports_agent.py`**:

1. **Lista `tools`:** registrar solo tools ya implementadas; ir ampliando al cerrar cada tool en Fase 5.
2. **`instructions` (system prompt):** incluir tabla resumen **intención → herramienta → por qué**.

Plantilla (completar cuando existan las tools reales):

| Pregunta típica (usuario) | Herramienta | Categoría | Por qué |
|---------------------------|-------------|-----------|---------|
| ¿Quién es el responsable de la sucursal X? | `jis_listar_sucursales` | Inventario | Dato textual + filtro por nombre de sucursal. |
| ¿Cuántas sucursales tiene [persona]? | `jis_listar_sucursales` (+ modo contar cuando exista) | Inventario / agregado ligero | Conteo desde misma vista; evitar segunda tool hasta unificar criterios. |
| ¿Cuánto ganamos en total en enero? | `jis_obtener_resumen_ejecutivo` | Resumen | Agregados, no listar filas. |
| ¿Top 5 parkings por ventas? | `jis_ranking_sucursales` | Ranking | `ORDER BY` + `LIMIT`. |
| ¿Cómo le fue a Cerrillos este semestre? | `jis_obtener_evolucion_temporal` | Tendencia | Serie temporal + filtro geográfico/sucursal. |
| ¿Depósitos pendientes de mi cartera? | `jis_consultar_depositos` (futura) | Inventario | `QRY_REPORTE_DEPOSITOS` + filtro estado/sucursales vía BO. |
| ¿Resumen de diferencias en depósitos este mes? | `jis_resumen_depositos` (futura) | Resumen | Misma vista; agregados como `/kpi/depositos/resumen`. |
| ¿Abonados imputados por pagar? | `jis_listar_abonados` (futura) | Inventario | `CABECERA_ABONADOS` + criterios legacy de status. |
| ¿Ventas del 15 al 20 por sucursal X? | `jis_consultar_ventas_diarias` (futura) | Inventario / tendencia | `KPI_INGRESOS_DIARIO` + rango fechas. |

**Coerción Ollama:** mantener `coerce_ollama_text_tool_calls` y `_TOOL_NAMES` sincronizados con los nombres reales de las tools.

**Routing post-tool:** extender `after_tools` / `route_after_tools` solo cuando haya formatos deterministas nuevos (tablas KPI, series, rankings).

---

## Fase 5 — Implementación incremental de tools

Por cada tool nueva:

| Paso | Acción |
|------|--------|
| 5.1 | Definir firma en `jis_tools.py` (args con tipos claros, defaults seguros). |
| 5.2 | SQL revisado contra `JIS_DB_MAP.md` (columnas e índices). |
| 5.3 | Límites: `LIMIT`, timeouts de conexión, rechazar SQL dinámico arbitrario del LLM. |
| 5.4 | JSON de salida homogéneo. |
| 5.5 | Añadir a `tools` en el grafo y fila en la matriz de decisión del prompt. |
| 5.6 | Prueba manual: misma lógica en Navicat vs respuesta del agente. |

---

## Fase 6 — Integración FastAPI / Streamlit (sin cambios arquitectónicos)

- **FastAPI:** ya ejecuta el grafo; nuevas tools no requieren nuevos endpoints.
- **Streamlit:** seguirá mostrando tool calls y resultados; si una tool devuelve markdown fijo, reutilizar el patrón `after_tools`.

---

## Orden recomendado de trabajo (siguiente sprint)

Orden alineado a **impacto y paridad con jisreportes.com**:

1. **`jis_listar_sucursales`:** `modo=listar|contar` + respuesta corta en `after_tools` (UX inmediata).
2. **Ventas diarias:** tool sobre **`KPI_INGRESOS_DIARIO`** (rango de fechas, `metrica`, sucursal opcional); join a **`QRY_BRANCH_OFFICES`** si la pregunta pide responsable.
3. **Presupuesto diario:** tool o parámetro que use **`QRY_PPTO_DIA`** (paridad `/ventas_diarias/ppto_diario` y “real vs meta”).
4. **Depósitos:** tool sobre **`QRY_REPORTE_DEPOSITOS`** (listado con filtros de estado; segunda variante o args para KPI agregado mes actual, coherente con exclusión OFICINA donde aplique).
5. **Abonados:** tool sobre **`CABECERA_ABONADOS`** + **`dte_types`** con estados documentados (imputada por pagar, `status_id = 4`, etc.).
6. **Ranking / evolución:** top N sucursales y series temporales reutilizando `KPI_INGRESOS_IMG_MES` / diario con `ORDER BY` + `LIMIT` y fechas obligatorias.
7. **Contexto de usuario** (opcional): si 2.0 debe ver “solo mis sucursales”, diseñar paso de autenticación o parámetro `branch_office_ids` desde el cliente.

---

## Archivos tocados en el desarrollo (referencia)

| Archivo | Rol |
|---------|-----|
| `scripts/jis_db_mapper.py` | Genera `JIS_DB_MAP.md` |
| `JIS_DB_MAP.md` | Salida del mapper (catálogo) |
| `framework/agent-service-toolkit/src/agents/jis_tools.py` | Definición SQL + tools |
| `framework/agent-service-toolkit/src/agents/jis_reports_agent.py` | Grafo, `instructions`, `after_tools`, coerción |
| `HOJA_RUTA_AGENTE_JIS_REPORTES.md` | Roadmap vivo del proyecto |

---

*Última actualización: 2026-04-09 — incorporada fuente de verdad jisreportes.com (tablas, vistas, reglas y mapa hacia tools).*
