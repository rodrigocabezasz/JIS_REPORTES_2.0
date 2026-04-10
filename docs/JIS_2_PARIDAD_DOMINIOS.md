# JIS Reportes 2.0 vs jisreportes.com — paridad por dominio

Referencia: `docs/JISREPORTES_COM_FUENTE_OFICIAL.md` (código oficial back/front) y `PLAN_CATALOGO_DB_Y_HERRAMIENTAS.md`.

**Contexto:** jisreportes.com (Streamlit + FastAPI + ETL) y JIS 2.0 (chat sobre la misma MySQL) se complementan; el chat no reemplaza gráficos, PDFs ni flujos con **identidad de usuario** (cartera por rol).

---

## 1. Sucursales / datos maestros

| Capacidad legacy | Dónde en jisreportes.com | JIS 2.0 |
|------------------|--------------------------|---------|
| Listado sucursales con filtros | `GET /sucursales`, `pages/datos_maestros.py` | `jis_listar_sucursales` sobre `QRY_BRANCH_OFFICES` |
| Distribución % por dimensión | UI agrega desde sucursales | `jis_distribucion_sucursales` |
| Sucursales por usuario logueado | `GET /sucursales_rut`, `GET /api/usuarios/.../sucursales` | **No** (chat anónimo): sin RUT/token no se replica “mis sucursales” |
| CRUD sucursales | `pages/datos_maestros.py`, `/sucursales-crud` | **Fuera de alcance** (solo lectura / reporting) |

**Brechas aceptadas:** cartera por rol y CRUD. El resto de preguntas de inventario/filtros sí tienen herramienta.

---

## 2. Ventas / informes

| Capacidad legacy | Dónde | JIS 2.0 |
|------------------|-------|---------|
| KPI mensual / acumulado, detalle filas | `/kpis/ingresos`, `/kpis/presupuesto`, `ventas.py` | `jis_consultar_kpi_ingresos` |
| Totales empresa, ranking | resumen + ranking en dashboard | `jis_obtener_resumen_ejecutivo`, `jis_ranking_sucursales` |
| Serie mes a mes una sucursal | `POST /kpis/evolucion_anual` | `jis_obtener_evolucion_temporal` |
| Informe gerencial YoY + ppto + tickets | `informe.py` (paths dinámicos), KPI comparativo | `jis_informe_ventas_comparativo` |
| Ventas diarias por rango | `/ventas_diarias/*`, `ventas_diario.py` | `jis_consultar_ventas_diarias` |
| Centro de mando / proyecciones ML | `dashboard_ventas_unificado.py`, `/projections/generate` | **No** (proyección ML / UI unificada) |
| Venta vs meta (analytics) | `ventas_vs_meta.py`, `/VentasVsMeta/...` | **No** (dominio aparte; no mismo SQL que informe comparativo) |
| Ventas por hora | `ventas_hora.py`, ETL | **No** |

**Brechas:** proyecciones, ventas vs meta analytics, ventas por hora. Las preguntas de **cifras históricas KPI/diario/informe** están cubiertas.

---

## 3. Depósitos

| Capacidad legacy | Dónde | JIS 2.0 |
|------------------|-------|---------|
| Reporte consolidado (día × sucursal, estados) | `GET /operations/deposit_report`, `depositos.py` | `jis_consultar_depositos` (`QRY_REPORTE_DEPOSITOS`) |
| KPI tarjetas (conteos, diferencia, latencia) | `GET /kpi/depositos/resumen`, mismo dashboard | `jis_resumen_depositos` |
| Filtro por cartera usuario | API con `accessible_branches` | **No** en chat anónimo |
| Solo pendientes vía reporte | `/reportes/depositos_pendientes` | Cubierto con `estado_deposito` + fechas |

**Brechas:** agregación **exactamente igual** a la del servicio Python del legacy (reglas derivadas en `services`); la **vista** y filtros alinean el negocio. Gráficos Plotly no están en el chat.

---

## 4. Abonados / DTEs (nuevo en 2.0)

| Capacidad legacy | Dónde | JIS 2.0 |
|------------------|-------|---------|
| Lista completa + join tipo DTE | `GET /abonados`, `dtes.py` | `jis_consultar_abonados` |
| KPI DTEs pendientes (`status_id = 4`) | `GET /kpi/dtes/resumen` | `jis_resumen_abonados` (`kpi_dtes_pendientes`) |
| Análisis “imputada por pagar / pagada”, gráficos | `dtes.py` (pandas) | Listado/resumen con filtros; sin gráficos |
| Filtro por sucursales del usuario | API según rol | **No** sin sesión |

---

## 5. Próximos dominios (fuera de este documento)

- Abonados: ampliar con más presets de estado si el negocio lo pide.
- Rendiciones, honorarios, asistencia, etc.: evaluar con el mismo patrón (vista/tabla + tool + `after_tools`).

---

*Última revisión: alineada a implementación de herramientas en `jis_tools.py` y prompts en `jis_reports_agent.py`.*
