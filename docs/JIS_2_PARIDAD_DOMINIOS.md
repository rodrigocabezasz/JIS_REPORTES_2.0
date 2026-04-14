# JIS Reportes 2.0 vs jisreportes.com — revisión general de cobertura

**Objetivo del producto:** el chat (LangGraph + MySQL) responde con **los mismos datos** que alimentan jisreportes.com, en texto/tablas, **sin** sustituir ETL, gráficos, PDFs ni pantallas con **sesión de usuario**.

**Referencias:** `PLAN_CATALOGO_DB_Y_HERRAMIENTAS.md`, espejo local `docs/JISREPORTES_COM_FUENTE_OFICIAL.md` (generar con `python scripts/build_jisreportes_source_mirror.py`; no versionado en Git).

---

## Resumen ejecutivo

| Estado | Significado |
|--------|-------------|
| **Listo** | Hay tool(s) + prompt + formato `after_tools` donde aplica; cubre el núcleo de datos del dashboard legacy indicado. |
| **Parcial** | Hay datos relacionados pero no toda la lógica/UI (ej. sin gráficos, sin ML, sin filtro por “mis sucursales”). |
| **Pendiente** | Pantalla o API legacy existe; en 2.0 aún no hay herramienta dedicada. |
| **Fuera de alcance** | CRUD, disparos ETL, ML, notificaciones — no es el rol del chat de solo lectura. |

---

## Inventario actual de herramientas (12)

| # | Herramienta | Dominio |
|---|-------------|---------|
| 1 | `jis_listar_sucursales` | Maestro sucursales |
| 2 | `jis_distribucion_sucursales` | Distribución % |
| 3 | `jis_obtener_resumen_ejecutivo` | Ventas agregadas mes |
| 4 | `jis_ranking_sucursales` | Top sucursales |
| 5 | `jis_obtener_evolucion_temporal` | Serie mensual una sucursal |
| 6 | `jis_consultar_kpi_ingresos` | Detalle KPI fila a fila |
| 7 | `jis_informe_ventas_comparativo` | Informe gerencial YoY + ppto |
| 8 | `jis_consultar_ventas_diarias` | KPI diario por rango |
| 9 | `jis_consultar_depositos` | Listado depósitos |
| 10 | `jis_resumen_depositos` | KPI depósitos agregado |
| 11 | `jis_consultar_abonados` | Listado DTE / abonados |
| 12 | `jis_resumen_abonados` | KPI DTE + resumen por status |

---

## Mapa rápido: menú jisreportes.com → estado en 2.0

Áreas típicas del front Streamlit legacy frente al chat:

| Área legacy (menú / módulo) | Estado 2.0 | Notas |
|----------------------------|------------|--------|
| Datos maestros / sucursales | **Listo** / **Parcial** | Listado + distribución OK. CRUD y “mis sucursales” por RUT: **no**. |
| Dashboard ventas + KPI + informe | **Listo** / **Parcial** | Resumen, ranking, evolución, KPI detalle, informe comparativo, ventas diarias. **No:** ventas por hora, venta vs meta (analytics), centro de mando / proyecciones ML. |
| Depósitos | **Listo** / **Parcial** | Vista `QRY_REPORTE_DEPOSITOS` + resumen KPI. Sin gráficos; sin filtro cartera por usuario en chat anónimo. |
| Track abonados / DTEs | **Listo** / **Parcial** | Listado + resumen (incl. `status_id=4` e imputada por pagar). Sin gráficos ni lógica pandas completa del front. |
| Rendiciones | **Pendiente** | Requiere vistas/API del legacy + nueva tool. |
| Honorarios | **Pendiente** | Router `/honorarios` en back; sin tool en 2.0. |
| Presupuesto de ventas / distribución ppto | **Pendiente** | Budgeting `/budgeting/*`; distinto al informe comparativo ya cubierto. |
| Proyecciones de ventas | **Pendiente** / **Fuera** parcial | ML/generación: probablemente fuera del chat; si hay tablas de salida legibles, valorar tool de lectura. |
| Venta real vs meta (VentasVsMeta) | **Pendiente** | Endpoint dedicado; no es el mismo SQL que `jis_informe_ventas_comparativo`. |
| SSS (same store sales) | **Pendiente** | `/sss/*` en back. |
| Asistencia / turnos / planificación | **Pendiente** / **Fuera** | Mucho es carga y mallas; solo lectura de reportes podría alcanzar si hay vista estable. |
| Indicadores económicos, calendario, recursos | **Pendiente** | Depende si el negocio pide esos datos en el mismo chat operativo. |
| Reportes PDF / WhatsApp / notificaciones | **Fuera de alcance** | Disparadores y envío, no consulta SQL conversacional. |
| ETL status / cargas | **Fuera de alcance** | `POST /etl/update/*` no debe ser tool del agente de reporting. |

---

## Detalle por dominio ya trabajado

### 1. Sucursales / datos maestros

| Capacidad legacy | Dónde | JIS 2.0 |
|------------------|-------|---------|
| Listado sucursales con filtros | `GET /sucursales`, `datos_maestros.py` | `jis_listar_sucursales` (`QRY_BRANCH_OFFICES`) |
| Distribución % por dimensión | UI | `jis_distribucion_sucursales` |
| Sucursales por usuario | `GET /sucursales_rut`, APIs usuario | **No** sin token/RUT en el chat |
| CRUD | `/sucursales-crud` | **Fuera de alcance** |

### 2. Ventas / informes

| Capacidad legacy | Dónde | JIS 2.0 |
|------------------|-------|---------|
| KPI mensual / acumulado detalle | `/kpis/*`, `ventas.py` | `jis_consultar_kpi_ingresos` |
| Totales y ranking | dashboards | `jis_obtener_resumen_ejecutivo`, `jis_ranking_sucursales` |
| Evolución anual lista sucursales | `POST /kpis/evolucion_anual` | `jis_obtener_evolucion_temporal` (una sucursal) |
| Informe gerencial YoY + ppto | `informe.py` | `jis_informe_ventas_comparativo` |
| Ventas diarias | `/ventas_diarias/*`, `ventas_diario.py` | `jis_consultar_ventas_diarias` |
| Ppto diario explícito (`QRY_PPTO_DIA`) | legacy | **Parcial:** `jis_consultar_ventas_vs_meta` (mes + join CABECERA); `jis_consultar_ventas_diarias` `metrica=ppto` (KPI diario) |
| Proyecciones / centro de mando | `dashboard_ventas_unificado`, `/projections` | **Pendiente / fuera ML** |
| Venta vs meta analytics | `ventas_vs_meta.py` | **`jis_consultar_ventas_vs_meta`** |
| Ventas por hora | `ventas_hora.py`, ETL | **Pendiente** |

### 3. Depósitos

| Capacidad legacy | Dónde | JIS 2.0 |
|------------------|-------|---------|
| Reporte consolidado | `GET /operations/deposit_report`, `depositos.py` | `jis_consultar_depositos` |
| KPI tarjetas | `GET /kpi/depositos/resumen` | `jis_resumen_depositos` |
| Filtro por cartera | API con `accessible_branches` | **No** en chat anónimo |

### 4. Abonados / DTEs

| Capacidad legacy | Dónde | JIS 2.0 |
|------------------|-------|---------|
| Lista + tipo documento | `GET /abonados`, `dtes.py` | `jis_consultar_abonados` |
| KPI `status_id = 4` | `GET /kpi/dtes/resumen` | `jis_resumen_abonados` |
| Gráficos y tablas derivadas pandas | `dtes.py` | **Parcial** (datos vía listado/resumen) |

---

## Qué faltaría para “igualar información” (orden sugerido)

1. **Sesión / cartera (opcional producto):** pasar `user_rut` o token al servicio del agente y filtrar sucursales como el legacy (`accessible_branches`). Sin esto, nunca será idéntico al dashboard “como usuario logueado”.
2. ~~**Venta vs meta (`VentasVsMeta`):**~~ cubierto por **`jis_consultar_ventas_vs_meta`**.
3. **Presupuesto / distribución diaria (`/budgeting/*`):** flujos de edición/distribución de meta siguen **fuera** del chat; lectura PPTO en mes vía ventas vs meta o KPI diario.
4. **Rendiciones y honorarios:** siguiente bloque natural tras abonados (revisar vistas/tablas en `JIS_DB_MAP.md` y routers).
5. **Ventas por hora:** si el dato vive en tablas/vistas consultables por `reader`, tool acotada por fecha/sucursal.
6. **SSS:** si hay endpoint/vista estable, resumen o ranking.
7. **QA y paridad numérica:** casos Navicat vs agente por dominio (docs de prueba); validar literales de `status` abonados/depósitos en BD real.
8. **Plataforma:** tests unitarios parsers/formatters, límites LangGraph, toggle documentado stream tokens.

---

## Transversal (no es paridad de datos pero sí producto)

- **UX Streamlit** del cliente 2.0 vs chat genérico del toolkit (informe ventas dedicado ya existe como página aparte).
- **Safeguard / Groq** en dev (ruido en logs).
- **Documentación operativa:** README / `instrucciones.txt` (ya orientados a túneles + API + Streamlit).

---

*Última revisión: inventario de 12 tools en `jis_tools.py`, prompts en `jis_reports_agent.py`. Actualizar este archivo al cerrar cada sprint de dominio.*
