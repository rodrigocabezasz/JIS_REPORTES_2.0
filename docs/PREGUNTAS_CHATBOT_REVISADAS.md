# Preguntas revisadas para el chatbot JIS (Streamlit)

Frases en español **listas para copiar y pegar** en el chat, alineadas a las herramientas **MySQL** del agente y al **RAG** (documentación en `data/jisparking_knowledge/`). Sirven para demos, regresión manual o entrenamiento de usuarios.

**Notas rápidas**

- **Informe de ventas comparativo** (`jis_informe_ventas_comparativo`): mismos criterios que el informe gerencial en jisreportes.com — **ingresos = efectivo neto + tarjeta neta + abonados**; incluye presupuesto, variación YoY y desviación vs meta. En Streamlit, el detalle por sucursal/responsable muestra montos con **formato de moneda**.
- **Ranking / top sucursales** (`jis_ranking_sucursales`): ordena por volumen con criterio **bruto** (no es el mismo número que el informe comparativo).
- **Venta vs meta** (`jis_consultar_ventas_vs_meta`): un **mes calendario**, día a día, venta **bruta** (CABECERA_TRANSACCIONES) vs meta (**QRY_PPTO_DIA**), como el dashboard legacy **Venta vs Meta**. No es el informe comparativo (ingresos **netos** + YoY).
- **Depósitos** (`jis_consultar_depositos`, `jis_resumen_depositos`): vista **`QRY_REPORTE_DEPOSITOS`**; el filtro de fechas usa **fecha de recaudación**. Por defecto se excluyen filas cuyo nombre de sucursal contiene **OFICINA** (como el KPI legacy). Listado: columnas recaudado / depositado / diferencia / días latencia. Resumen: mismas sumas agregadas, promedio de latencia total y promedio excluyendo “Depositado Correcto” y “Depositado a Favor” (seguimiento). Filtros opcionales en el resumen: sucursal, supervisor o **responsable_contiene**, estado.
- **Abonados / DTEs** (`jis_consultar_abonados`, `jis_resumen_abonados`): tabla **`CABECERA_ABONADOS`** + tipo en **`dte_types`**; fecha de filtro = **date** del documento (no confundir con depósitos). **status_id=4** alinea el bloque KPI con **`/kpi/dtes/resumen`**. **imputada_por_pagar** replica el corte del dashboard Track (texto «imputada por pagar»). Sin sesión no hay filtro por “mis sucursales” del usuario.
- Para matrices de prueba técnicas de sucursales (argumentos esperados por herramienta), ver también [`CASOS_PRUEBA_SUCURSALES.md`](./CASOS_PRUEBA_SUCURSALES.md).
- **Conocimiento documental (RAG)** (`jis_buscar_conocimiento_jisparking`): respuestas basadas en textos indexados en **Chroma** (reglamento interno en PDF; protocolos **PROT-SC-001**; formularios **FORM-SC-001** y **FORM-SC-002** en Markdown). **No** sustituye MySQL: montos, listados y KPIs siguen yendo por las herramientas `jis_*` de base de datos. El índice se genera con `framework/agent-service-toolkit/scripts/run_build_jisparking_rag.ps1` y queda en `framework/agent-service-toolkit/chroma_jisparking/`. **Misma URL y modelo de embeddings** que al construir (`OLLAMA_BASE_URL`, `OLLAMA_EMBED_MODEL`, por defecto `nomic-embed-text`).

### Cómo probar desde Streamlit en tu PC (MySQL + RAG)

El chat de Streamlit **no** ejecuta SQL ni el RAG por sí solo: habla con el **API FastAPI** del agente. En local son **dos procesos**.

1. **Requisitos**
   - **Ollama** en ejecución (app en bandeja o `ollama serve`).
   - Mismo **`.env`** coherente en la **raíz del repo** y en `framework/agent-service-toolkit/.env` (o al menos variables críticas copiadas): `OLLAMA_MODEL`, `OLLAMA_BASE_URL` si aplica, credenciales **MySQL**, `DEFAULT_MODEL` si usa Ollama.
   - **Índice RAG** ya construido (mensaje tipo “Listo: N chunks” al correr el script de build). Si movés la carpeta del repo, el índice viaja con `chroma_jisparking/`.

2. **Terminal 1 — API del agente** (debe quedar escuchando, por defecto puerto **8080**)

   Desde la raíz `C:\JIS_REPORTES_2.0`:

   ```powershell
   .\scripts\run_agent_service.ps1
   ```

   Eso deja el directorio actual en el **toolkit** y ejecuta `python src\run_service.py` (carga el `.env` del toolkit). Si preferís manual:

   ```powershell
   cd C:\JIS_REPORTES_2.0\framework\agent-service-toolkit
   .\.venv\Scripts\Activate.ps1   # si usa el venv solo del toolkit
   python src\run_service.py
   ```

3. **Terminal 2 — Streamlit**

   ```powershell
   cd C:\JIS_REPORTES_2.0
   .\.venv\Scripts\Activate.ps1
   .\scripts\run_streamlit.ps1 -SkipTunnel
   ```

   (`-SkipTunnel` si no necesita túneles SSH en esa sesión.) El script usa el `.venv` de la **raíz** del repo.

4. **Variables para que Streamlit encuentre el API**

   En el `.env` de la **raíz** (donde Streamlit hace `load_dotenv` al arrancar), puede definir por ejemplo:

   ```env
   AGENT_URL=http://127.0.0.1:8080
   ```

   Si el API está en otro host/puerto, ajustá la URL. Si ves error de conexión (**10061**, etc.), el paso 2 no está corriendo o el puerto no coincide.

5. **En la UI de Streamlit**

   - **Settings** (barra lateral) → **Agent to use** → elegí **`jis-reports`** (es el que tiene herramientas MySQL + RAG).
   - El streaming para este agente va por **mensajes** (no tokens), para evitar que Ollama mezcle JSON de herramientas en el chat.

6. **Orden sugerido de prueba**

   - Una pregunta **solo RAG** (sección 8) → debería llamar a búsqueda en conocimiento documental.
   - Una pregunta **solo MySQL** (ej. sucursales) → sin depender del PDF.

---

## 1. Dominio: sucursales

Vista `QRY_BRANCH_OFFICES`: listado, conteos y distribuciones. Por defecto el agente suele filtrar **solo activas** (`status_id = 7`).

### 1.1 Listado general y conteos

- “Lista todas las sucursales activas.”
- “¿Cuántas sucursales activas hay en total?”
- “¿Cuántas sucursales hay en la comuna de Providencia?”
- “¿Cuántas sucursales hay en la Región Metropolitana?”
- “Lista las sucursales de la comuna Santiago.”

### 1.2 Por responsable, nombre de local y marca

- “Sucursales del responsable David Gómez.”
- “Locales cuyo nombre contenga Lider Tobalaba.”
- “Sucursales Tottus en San Bernardo.”
- “Busca sucursales donde diga Sta Isabel o Santa Isabel en el nombre, marca o comuna.”

### 1.3 Región, zona, segmento, dirección

- “Sucursales en zona Centro.”
- “Locales de segmento supermercado.”
- “Sucursales de segmento MALL en la Región Metropolitana.”
- “Marca LIDER en comuna Lo Prado.”
- “Sucursales en calle Matucana.”

### 1.4 ID, código DTE y supervisor

- “Datos de la sucursal con id 42.”
- “¿Qué código DTE tiene el local que contiene 76160 en el código?”
- “Sucursales cuyo supervisor tenga en el RUT el fragmento que te paso: …”

### 1.5 Distribución y porcentajes (sin listar cada local)

- “¿Qué porcentaje de sucursales hay por segmento?”
- “Distribución de sucursales por zona.”
- “Cuántas y qué % de sucursales por región.”
- “Desglose por comuna: cantidad y porcentaje de sucursales activas.”
- “¿Cómo se distribuyen las sucursales por marca (principal)?”

### 1.6 Visibilidad legacy e inactivas

- “Solo sucursales que entran en reportes por responsable (visibilidad legacy).”
- “Incluye también sucursales no activas asignadas al responsable [nombre].”

---

## 2. Dominio: informe de ventas (comparativo)

Una misma herramienta cubre **resumen tipo tarjetas** (total) y **tablas** (por sucursal o por responsable), con comparación **año actual vs año anterior** y **presupuesto**.

Sustituí libremente **mes y año** (ej. marzo 2026). Si pedís “acumulado ene.–marzo”, el agente debe usar alcance **YTD** hasta ese mes.

### 2.1 Resumen general — un solo mes (tarjetas)

- “Dame el resumen general de ventas de marzo 2026: ingresos vs año anterior, presupuesto, variación %, desviación vs presupuesto, ticket promedio y cuántas sucursales.”
- “Resumen de ventas de febrero 2026 comparado con 2025, con cumplimiento vs meta y tickets.”

### 2.2 Resumen acumulado año a la fecha (ene.–mes)

- “Resumen de ventas acumulado de enero a marzo 2026 comparado con el mismo periodo del año pasado, con presupuesto y cumplimiento vs meta.”
- “Ventas YTD hasta junio 2026 vs el mismo acumulado de 2025, con presupuesto y variación.”

### 2.3 Informe gerencial — tabla por sucursal

- “Informe gerencial de ventas por sucursal para marzo 2026: ingresos 2026 y 2025, variación %, presupuesto, desviación vs presupuesto, tickets y ticket promedio.”
- “Tabla de ventas por parking en abril 2026 con comparación al año anterior y presupuesto.”

### 2.4 Informe — tabla por responsable

- “Ventas por responsable en marzo 2026 con comparación al año anterior y presupuesto.”
- “Desglose por responsable comercial de mayo 2026: ingresos, presupuesto, variación y desviación vs ppto.”

### 2.5 Filtros sobre el informe

- “Lo mismo pero solo para el responsable que contenga Gómez.”
- “Informe por sucursal de marzo 2026 solo para locales del responsable que contenga Pérez.”
- “Resumen total de ventas de enero 2026 solo para la sucursal id [número].” *(Si no tenés el id, primero pedí listar sucursales por nombre.)*

### 2.6 Matices de periodo KPI (cuando haga falta ser explícitos)

En **un solo mes**, el dashboard distingue vista **mensual** vs **acumulada** del mes en KPI; si el modelo no infiere bien, podés guiar con frases como:

- “Ventas de marzo 2026 en **vista mensual** del KPI (solo ese mes), comparadas con 2025.”
- “Ventas de marzo 2026 en **vista acumulada** del KPI para ese mes, comparadas con 2025.”

### 2.7 Venta real vs meta del mes (dashboard)

- “Venta vs meta de marzo 2026 para toda la empresa, día a día.”
- “Real vs presupuesto diario de enero 2026 para el local que contenga Quilicura.”
- “Cumplimiento vs meta por día en abril 2026, sucursal id [número].”

---

## 3. Ventas diarias (otra herramienta)

Serie **día a día** desde `KPI_INGRESOS_DIARIO`. El rango máximo por consulta es **93 días**; si pide más, conviene acortar o dividir la pregunta.

### 3.1 Red global o por local

- “Ventas día a día del 1 al 15 de marzo 2026.”
- “Desglose diario de ingresos del 2026-03-01 al 2026-03-31 para toda la red.”
- “Ventas diarias del 1 al 7 de abril 2026 solo para la sucursal que se llama [fragmento del nombre del local].”

### 3.2 Presupuesto diario (cuando aplique)

- “Presupuesto día a día del 10 al 20 de marzo 2026.”
- “Evolución diaria de la meta (ppto) en enero 2026 para la sucursal id [número].”

---

## 4. Otras consultas útiles (mismo agente)

Frases cortas; el modelo elige la herramienta según el texto.

### 4.1 Totales del mes sin comparar año anterior

- “Suma total de ingresos y tickets de marzo 2026 (todas las sucursales activas).”
- “Mismo resumen pero solo para la sucursal id [número].” *(En **un solo turno** sin mes en la frase, el agente aplica una heurística de demo **marzo 2026** para no quedar sin `year`/`month`; en producción conviene repetir el periodo explícito o usar el mismo hilo de chat tras la pregunta anterior.)*

### 4.2 Top por volumen (criterio distinto al informe comparativo)

- “Top 10 sucursales por ventas en marzo 2026.”
- “Las 5 sucursales con más ingresos en junio 2026, vista acumulada del KPI.”

### 4.3 Serie mensual por un local

- “Evolución mes a mes de ingresos de 2026 para la sucursal [nombre o id].”
- “Primer semestre 2026, ventas por mes del local que contenga Florida en el nombre.”

### 4.4 Filas detalle KPI (avanzado)

- “Trae las filas de KPI de ingresos mensual de marzo 2026 para revisar en bruto.”
- “KPI acumulado hasta marzo 2026 para la sucursal id [número].”

---

## 5. Dominio: depósitos y recaudación

Vista **`QRY_REPORTE_DEPOSITOS`**. Estados posibles en la base (literales): **Pendiente**, **Depositado con Diferencia**, **Depositado a Favor**, **Depositado Correcto**.

### 5.1 Resumen del mes (KPI agregado)

- “Resumen de depósitos de marzo 2026: cuántos registros, suma de diferencias, latencia promedio y cantidad por estado.”
- “KPI de depósitos del mes actual: totales y desglose por estado de depósito.”

### 5.2 Listados por periodo de recaudación

- “Lista de depósitos con fecha de recaudación entre el 2026-03-01 y el 2026-03-31.”
- “Todos los movimientos de recaudación/de depósitos de febrero 2026.” *(El modelo puede usar `year` + `month`.)*

### 5.3 Pendientes y problemáticos

- “Depósitos pendientes de marzo 2026.”
- “Depósitos en marzo 2026 con estado Depositado con Diferencia.”
- “Solo los depositados correctos de abril 2026.”

### 5.4 Por sucursal o supervisor

- “Depósitos de marzo 2026 para la sucursal que contenga Cordillera en el nombre.”
- “Movimientos de recaudación del 1 al 15 de marzo 2026 para la sucursal id 123.”
- “Depósitos de junio 2026 donde el supervisor contenga Pérez.”

### 5.5 Incluir oficina (caso excepcional)

- “Mismo resumen de depósitos de mayo 2026 pero incluyendo sucursales tipo oficina (no excluir OFICINA).”

---

## 6. Dominio: abonados y DTEs (Track)

Tabla **`CABECERA_ABONADOS`**. El resumen incluye **kpi_dtes_pendientes** (`status_id = 4`, como el API legacy) y el bloque **imputada por pagar**.

### 6.1 Resumen del mes

- “Resumen de abonados de marzo 2026: totales, por status, KPI pendientes DTE y monto imputada por pagar.”
- “Cuántos DTE con status_id 4 y monto subtotal en abril 2026.”

### 6.2 Listados

- “Lista documentos abonados de marzo 2026 con imputada por pagar.”
- “Abonados de febrero 2026 para la sucursal que contenga Florida en el nombre.”
- “DTEs del 2026-03-01 al 2026-03-15 con RUT que contenga 76123456.”

---

## 7. Checklist rápido antes de una demo

| Objetivo | Ejemplo mínimo |
|----------|-----------------|
| Catálogo / filtros de locales | “Sucursales en comuna Providencia” + “¿cuántas hay?” |
| Informe ejecutivo un mes | “Resumen general de ventas de marzo 2026 vs 2025 con presupuesto” |
| Tabla gerencial | “Informe por sucursal marzo 2026 con tickets y ticket promedio” |
| Por responsable + filtro | “Ventas por responsable marzo 2026; solo los que contengan Gómez” |
| Serie diaria | “Ventas día a día del 1 al 15 de marzo 2026” |
| Depósitos | “Resumen de depósitos de marzo 2026” + “depósitos pendientes de marzo 2026” |
| Abonados | “Resumen de abonados de marzo 2026” + “lista imputada por pagar marzo 2026” |
| RAG / reglamento | “Según el reglamento interno de JIS PARKING, ¿qué dice sobre orden y limpieza?” (sección 8.1) |
| RAG / protocolo atención | “Según el protocolo PROT-SC-001, ¿cuál es la frase obligatoria de saludo en patio?” (sección 8.4) |
| RAG / pérdida ticket o siniestro | “¿Qué pasos indica la documentación para pérdida de ticket?” o “¿quién puede revisar las cámaras en un siniestro?” (8.5 y 8.6) |

---

## 8. Dominio: conocimiento documental (RAG) — reglamento, protocolos y formularios

Preguntas **solo de texto** indexado (PDF/Markdown en `data/jisparking_knowledge/`). El agente debería usar **`jis_buscar_conocimiento_jisparking`**, no MySQL. Si cambian versiones de los PDF/Markdown, conviene ajustar el redactado de las preguntas; lo importante es forzar **contenido del documento**, no datos operativos de BD.

### 8.1 Reglamento interno (orden, higiene, seguridad)

- “Según el reglamento interno de JIS PARKING, ¿cuáles son las obligaciones del personal en materia de orden, higiene y seguridad?”
- “¿Qué dice el reglamento interno sobre el uso de elementos de protección personal (EPP)?”
- “Resume en español qué establece el reglamento sobre limpieza y orden de las instalaciones.”
- “¿El reglamento interno menciona procedimientos en caso de accidente o emergencia? ¿Qué indica?”
- “¿Qué conductas o prohibiciones relacionadas con seguridad aparecen en el reglamento interno?”
- “¿Hay algo en el reglamento sobre el uso de instalaciones comunes o espacios de trabajo compartidos?”

### 8.2 Mezcla intencional (el agente debe elegir RAG, no SQL)

- “No me des números de ventas: según la documentación interna, ¿qué cubre el reglamento de orden, higiene y seguridad?”
- “¿Qué temas trata el reglamento interno de JIS PARKING? Responde solo con lo que diga el documento indexado.”

### 8.3 Contraste (RAG + SQL en la misma sesión)

Primero una pregunta de reglamento (8.1), luego una de datos, para verificar que no mezcla fuentes:

- “Ahora, aparte del reglamento: ¿cuántas sucursales activas hay en total?”

### 8.4 Protocolos de atención a clientes (PROT-SC-001, `servicio_cliente_protocolos_atencion.md`)

Las preguntas con **patio**, **inicio de jornada**, **centro de pago**, **cajero automático**, **pérdida de ticket** o **siniestro** también disparan la búsqueda en el RAG aunque no mencionen la palabra «reglamento».

- “Según el protocolo PROT-SC-001 de JIS Parking, ¿qué debe hacer el personal en patio en el inicio de jornada?”
- “¿Cuál es la frase obligatoria de apertura en atención al cliente según el protocolo de servicio?”
- “Resume los pasos del protocolo en centro de pago: recepción del ticket, cobro y trato al cliente.”
- “¿Qué dice el protocolo sobre asistencia en cajero automático cuando el equipo falla? ¿El reparo es gratuito?”
- “Si hay congestión en el patio, ¿qué indica el protocolo sobre orientación al cliente?”
- “¿Cómo debe ser la despedida según el protocolo (tratamiento y frase tipo)?”
- “¿Qué dice la filosofía de servicio ‘Bienvenido a diferenciarnos’ en el documento de protocolos?”

### 8.5 Pérdida de ticket (FORM-SC-001, `servicio_cliente_formulario_perdida_ticket.md`)

- “Según la documentación indexada sobre pérdida de ticket, ¿qué datos o pasos se piden al cliente antes de completar el registro?”
- “¿Qué indica el procedimiento después de que el cliente agota la búsqueda del ticket y no lo encuentra?”
- “¿En qué consiste el paso de revisión de CCTV en caso de pérdida de ticket, según el protocolo o formulario indexado?”
- “¿Qué documento o código está asociado al formulario de pérdida de ticket en la base de conocimiento?”

### 8.6 Siniestro / evidencia en cámaras (`servicio_cliente_formulario_siniestro.md` + sección siniestro del protocolo)

- “Según la documentación de JIS Parking, ¿quién puede revisar las cámaras de vigilancia y entregar información a PDI o Fiscalía?”
- “¿Qué debe hacer el personal si no hay evidencia del siniestro en las cámaras?”
- “Si sí hay evidencia del siniestro, ¿qué indica el protocolo sobre el supervisor y el registro?”
- “¿Qué campos o datos debe incluir el registro de siniestro según el formulario indexado?”

### 8.7 Cruce entre documentos (varios chunks / coherencia)

- “En una sola respuesta, relaciona las frases obligatorias del protocolo PROT-SC-001 con el cierre ‘Somos JIS Parking’ del mismo documento.”
- “¿Dónde enlaza el protocolo PROT-SC-001 con el formulario de pérdida de ticket y con el de siniestro?”

---

*Documento generado para el canal chat LLM + MySQL + RAG de JIS Reportes 2.0. Actualizar cuando se agreguen herramientas, documentos indexados o dominios nuevos.*
