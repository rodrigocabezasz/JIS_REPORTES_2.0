# Casos de prueba — `jis_listar_sucursales` / agente JIS

Usar en Streamlit o Navicat para validar paridad. Tras cambios en código, reiniciar el servicio del agente.

## Distribución / porcentajes por dimensión

| # | Pregunta | Herramienta |
|---|----------|-------------|
| 0 | Porcentaje de sucursales por segmento | `jis_distribucion_sucursales` con `dimension="segmento"` |

## Conteo vs listado

| # | Pregunta (español) | Esperado en tool |
|---|-------------------|------------------|
| 1 | ¿Cuántas sucursales activas hay en Providencia? | `comuna_contiene="Providencia"`, `modo_respuesta="contar"` |
| 2 | Dame el número de sucursales en la Región Metropolitana | `region_contiene="Metropolitana"`, `modo_respuesta="contar"` |
| 3 | Lista las sucursales en comuna Santiago | `comuna_contiene="Santiago"`, `modo_respuesta="listar"` o omitir modo |
| 4 | ¿Cuántas sucursales tiene asignadas [nombre completo]? | `responsable_contiene="…"`, `solo_activas=false` si piden “todas las asignadas” |

## Filtros por dimensión (activas por defecto)

| # | Pregunta | Argumentos principales |
|---|----------|-------------------------|
| 5 | Sucursales del responsable David Gómez | `responsable_contiene` (2 o más tokens según cómo escriban) |
| 6 | Locales cuyo nombre contiene Lider Tobalaba | `sucursal_contiene="Lider Tobalaba"` |
| 7 | Todas las de zona Centro | `zona_contiene="Centro"` |
| 8 | Segmento supermercado | `segmento_contiene="SUPERMERCADO"` o `"supermercado"` |
| 9 | Marca Tottus / principal LIDER | `marca_contiene` o `principal_contiene` |
| 10 | En calle Matucana | `direccion_contiene="Matucana"` |
| 11 | Código DTE que contenga 76160 | `codigo_dte_contiene="76160"` |
| 12 | Supervisor con RUT que termina en … | `supervisor_contiene` (substring del `principal_supervisor`) |
| 13 | Sucursal id 42 | `branch_office_id=42` |

## Nombre de ciudad / local ambiguo (OR)

| # | Pregunta | Esperado |
|---|----------|----------|
| 14b | Sucursales Sta Isabel / Santa Isabel | `local_marca_o_comuna_contiene="Sta Isabel"` (no solo `marca_contiene`) |

## Combinaciones

| # | Pregunta | Ejemplo de combinación |
|---|----------|-------------------------|
| 14 | Malls en Metropolitana | `segmento_contiene="MALL"`, `region_contiene="Metropolitana"` |
| 15 | Lider en comuna Lo Prado | `marca_contiene="Lider"`, `comuna_contiene="Lo Prado"` |
| 16 | Zona Centro y segmento EDIFICIOS | `zona_contiene="Centro"`, `segmento_contiene="EDIFICIOS"` |

## Visibilidad y estados (legacy)

| # | Pregunta | Argumentos |
|---|----------|------------|
| 17 | Solo sucursales visibles en reportes por responsable | `solo_visibilidad_reporte=true` |
| 18 | Incluir cerradas / no activas para un responsable | `solo_activas=false` |

## SQL de referencia (Navicat)

Activas + comuna:

```sql
SELECT COUNT(*) FROM QRY_BRANCH_OFFICES
WHERE status_id = 7 AND LOWER(commune) LIKE LOWER('%Providencia%');
```

Paridad con conteo del agente con `modo_respuesta="contar"` y mismos filtros.
