# Preguntas revisadas para el chatbot JIS (Streamlit)

Frases en español **listas para copiar y pegar** en el chat, alineadas a las herramientas MySQL del agente. Úsalas para demos, regresión manual o entrenamiento de usuarios.

**Notas rápidas**

- **Informe de ventas comparativo** (`jis_informe_ventas_comparativo`): mismos criterios que el informe gerencial en jisreportes.com — **ingresos = efectivo neto + tarjeta neta + abonados**; incluye presupuesto, variación YoY y desviación vs meta. En Streamlit, el detalle por sucursal/responsable muestra montos con **formato de moneda**.
- **Ranking / top sucursales** (`jis_ranking_sucursales`): ordena por volumen con criterio **bruto** (no es el mismo número que el informe comparativo).
- **Depósitos** (`jis_consultar_depositos`, `jis_resumen_depositos`): vista **`QRY_REPORTE_DEPOSITOS`**; el filtro de fechas usa **fecha de recaudación**. Por defecto se excluyen filas cuyo nombre de sucursal contiene **OFICINA** (como el KPI legacy). Listado: columnas recaudado / depositado / diferencia / días latencia. Resumen: mismas sumas agregadas, promedio de latencia total y promedio excluyendo “Depositado Correcto” y “Depositado a Favor” (seguimiento). Filtros opcionales en el resumen: sucursal, supervisor o **responsable_contiene**, estado.
- Para matrices de prueba técnicas de sucursales (argumentos esperados por herramienta), ver también [`CASOS_PRUEBA_SUCURSALES.md`](./CASOS_PRUEBA_SUCURSALES.md).

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

---

## 3. Ventas diarias (otra herramienta)

Serie **día a día** desde `KPI_INGRESOS_DIARIO`. El rango máximo por consulta es **93 días**; si pedís más, acortá o dividí la pregunta.

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
- “Mismo resumen pero solo para la sucursal id [número].”

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

## 6. Checklist rápido antes de una demo

| Objetivo | Ejemplo mínimo |
|----------|-----------------|
| Catálogo / filtros de locales | “Sucursales en comuna Providencia” + “¿cuántas hay?” |
| Informe ejecutivo un mes | “Resumen general de ventas de marzo 2026 vs 2025 con presupuesto” |
| Tabla gerencial | “Informe por sucursal marzo 2026 con tickets y ticket promedio” |
| Por responsable + filtro | “Ventas por responsable marzo 2026; solo los que contengan Gómez” |
| Serie diaria | “Ventas día a día del 1 al 15 de marzo 2026” |
| Depósitos | “Resumen de depósitos de marzo 2026” + “depósitos pendientes de marzo 2026” |

---

*Documento generado para el canal chat LLM + MySQL de JIS Reportes 2.0. Actualizar cuando se agreguen herramientas o dominios nuevos.*
