# Catálogo de base de datos JIS (MySQL)

*Generado automáticamente: 2026-04-09 15:48 UTC*

## Conexión usada (sin secretos)

| Parámetro | Valor |
| --- | --- |
| Host | `127.0.0.1` |
| Puerto | `3307` |
| Base (schema) | `jisparking` |
| Usuario | `reader_user` |

> **Nota:** `TABLE_ROWS` en MySQL/InnoDB es una estimación; úsala solo como orden de magnitud.

## Resumen

- **Tablas base:** 117
- **Vistas:** 38
- **Objetos con columnas listadas:** 155

## `jisparking`.`ASISTENCIA_DIARIA`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 15405

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `RUT` | varchar(13) | YES |  |  |  |  |
| 3 | `Trabajador` | varchar(100) | YES |  |  |  |  |
| 4 | `Especialidad` | varchar(100) | YES |  |  |  |  |
| 5 | `Sucursal` | varchar(100) | YES |  |  |  |  |
| 6 | `branch_office_id` | int | YES |  |  |  |  |
| 7 | `Contrato` | varchar(100) | YES |  |  |  |  |
| 8 | `Supervisor` | varchar(100) | YES |  |  |  |  |
| 9 | `Turno` | varchar(20) | YES |  |  |  |  |
| 10 | `EntradaFecha` | datetime | YES |  |  |  |  |
| 11 | `SalidaFecha` | datetime | YES |  |  |  |  |
| 12 | `JornadaTurnoMinutos` | smallint | YES |  |  |  |  |
| 13 | `JornadaEfectivaMinutos` | smallint | YES |  |  |  |  |
| 14 | `HorasNoTrabajadasMinutos` | smallint | YES |  |  |  |  |
| 15 | `HorasExtraordinariasMinutos` | smallint | YES |  |  |  |  |
| 16 | `HorasOrdinariasMinutos` | smallint | YES |  |  |  |  |
| 17 | `Semana` | varchar(20) | YES |  |  |  |  |
| 18 | `FechaCarga` | timestamp | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`ASISTENCIA_MALLA`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 32893

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `rut` | varchar(255) | YES |  |  |  |  |
| 3 | `sucursal` | varchar(255) | YES |  |  |  |  |
| 4 | `fecha` | date | YES |  |  |  |  |
| 5 | `codigo` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`ASISTENCIA_TRABAJADOR`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 155

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `rut` | varchar(255) | YES |  |  |  |  |
| 3 | `trabajador` | varchar(255) | YES |  |  |  |  |
| 4 | `email` | varchar(255) | YES |  |  |  |  |
| 5 | `especialidad` | varchar(255) | YES |  |  |  |  |
| 6 | `horas` | int | YES |  |  |  |  |
| 7 | `branch_office_id` | int | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`ASISTENCIA_TURNOS`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 81

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `codigo` | varchar(255) | YES |  |  |  |  |
| 3 | `base` | varchar(255) | YES |  |  |  |  |
| 4 | `turn` | varchar(255) | YES |  |  |  |  |
| 5 | `working` | time | YES |  |  |  |  |
| 6 | `breaking` | time | YES |  |  |  |  |
| 7 | `start` | time | YES |  |  |  |  |
| 8 | `end` | time | YES |  |  |  |  |
| 9 | `desde - hasta` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`CABECERA_ABONADOS`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 17343

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `date` | date | YES |  |  |  |  |
| 3 | `rut` | varchar(50) | YES |  |  |  |  |
| 4 | `cliente` | varchar(150) | YES |  |  |  |  |
| 5 | `razon_social` | varchar(150) | YES |  |  |  |  |
| 6 | `folio` | int | YES |  |  |  |  |
| 7 | `branch_office_id` | int | YES |  |  |  |  |
| 8 | `dte_type_id` | int | YES |  |  |  |  |
| 9 | `status_id` | int | YES |  |  |  |  |
| 10 | `status` | varchar(100) | YES |  |  |  |  |
| 11 | `total` | bigint | YES |  |  |  |  |
| 12 | `period` | varchar(50) | YES |  |  |  |  |
| 13 | `comment` | varchar(200) | YES |  |  |  |  |
| 14 | `chip_id` | int | YES |  |  |  |  |
| 15 | `subtotal` | bigint | YES |  | `0` |  |  |
| 16 | `tax` | bigint | YES |  | `0` |  |  |
| 17 | `payment_date` | date | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`CABECERA_TRANSACCIONES`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 46887

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `date` | date | NO | MUL |  |  |  |
| 3 | `branch_office_id` | int | NO |  |  |  |  |
| 4 | `cash_amount` | float | NO |  |  |  |  |
| 5 | `card_amount` | float | NO |  |  |  |  |
| 6 | `subscribers` | int | NO |  |  |  |  |
| 7 | `ticket_number` | int | NO |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`
- `idx_cabecera_date` (no único): `date`

## `jisparking`.`CALENDARIO_EVENTOS`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 276

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `fecha` | date | NO | MUL |  |  |  |
| 3 | `descripcion` | varchar(255) | NO |  |  |  |  |
| 4 | `categoria` | varchar(50) | NO | MUL |  |  |  |
| 5 | `tipo` | varchar(50) | YES |  | `NACIONAL` |  |  |
| 6 | `region` | varchar(100) | YES |  |  |  |  |
| 7 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |

**Índices**

- `PRIMARY` (único): `id`
- `idx_categoria` (no único): `categoria`
- `idx_fecha` (no único): `fecha`

## `jisparking`.`DETALLE_ABONADOS`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 15880

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `folio` | varchar(255) | YES |  |  |  |  |
| 3 | `rut` | varchar(255) | YES |  |  |  |  |
| 4 | `branch_office_id` | varchar(255) | YES |  |  |  |  |
| 5 | `dte_type_id` | varchar(255) | YES |  |  |  |  |
| 6 | `amount` | varchar(255) | YES |  |  |  |  |
| 7 | `status_id` | varchar(255) | YES |  |  |  |  |
| 8 | `contador` | varchar(255) | YES |  |  |  |  |
| 9 | `created_at` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`DETALLE_DEPOSITOS_DIA`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 8441

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `date` | varchar(255) | YES |  |  |  |  |
| 3 | `branch_office_id` | varchar(255) | YES |  |  |  |  |
| 4 | `deposito` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`DETALLE_RECAUDACION_DIA`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 22827

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `date` | date | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `recaudacion` | bigint | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`DETALLE_TRANSACCIONES`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 110653

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `date` | date | NO |  |  |  |  |
| 3 | `cashiers_id` | int | NO |  |  |  |  |
| 4 | `branch_office_id` | int | NO |  |  |  |  |
| 5 | `cash_amount` | double | NO |  |  |  |  |
| 6 | `card_amount` | double | NO |  |  |  |  |
| 7 | `ticket_number` | int | NO |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`DETALLE_VENTA_HORA`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `folio` | int | YES |  |  |  |  |
| 4 | `total` | bigint | YES |  |  |  |  |
| 5 | `entrance_hour` | time | YES |  |  |  |  |
| 6 | `exit_hour` | time | YES |  |  |  |  |
| 7 | `date` | date | YES |  |  |  |  |
| 8 | `hora_exit` | int | YES |  |  |  |  |
| 9 | `estadia` | time | YES |  |  |  |  |
| 10 | `minutos` | int | YES |  |  |  |  |
| 11 | `rango` | varchar(50) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`DM_PERIODO`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 5773

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `Fecha` | varchar(255) | YES |  |  |  |  |
| 2 | `Dia` | varchar(255) | YES |  |  |  |  |
| 3 | `Mes` | varchar(255) | YES |  |  |  |  |
| 4 | `Periodo` | varchar(255) | YES |  |  |  |  |
| 5 | `Trimestre` | varchar(255) | YES |  |  |  |  |
| 6 | `period` | varchar(255) | YES |  |  |  |  |
| 7 | `Año` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`DM_PERIODO_DATE`

- **Tipo:** BASE TABLE
- **Motor:** MyISAM
- **Filas estimadas (information_schema):** 5844

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `date` | date | NO | PRI |  |  |  |
| 2 | `dia` | varchar(2) | YES |  |  |  |  |
| 3 | `mes` | varchar(30) | YES |  |  |  |  |
| 4 | `periodo` | varchar(30) | YES |  |  |  |  |
| 5 | `trimestre` | varchar(30) | YES |  |  |  |  |
| 6 | `period` | varchar(30) | YES |  |  |  |  |
| 7 | `año` | int | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `date`

## `jisparking`.`DM_anac`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 92

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `Fecha` | varchar(255) | YES |  |  |  |  |
| 2 | `pasajeros` | varchar(255) | YES |  |  |  |  |
| 3 | `suv` | varchar(255) | YES |  |  |  |  |
| 4 | `camioneta` | varchar(255) | YES |  |  |  |  |
| 5 | `comercial` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`DM_dolar`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 503

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `fecha` | varchar(255) | NO | PRI |  |  |  |
| 2 | `valor` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `fecha`

## `jisparking`.`DM_euro`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 502

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `fecha` | varchar(255) | NO | PRI |  |  |  |
| 2 | `valor` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `fecha`

## `jisparking`.`DM_imacec`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 22

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `fecha` | varchar(255) | NO | PRI |  |  |  |
| 2 | `valor` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `fecha`

## `jisparking`.`DM_ipc`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 23

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `fecha` | varchar(255) | NO | PRI |  |  |  |
| 2 | `valor` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `fecha`

## `jisparking`.`DM_tasa_desempleo`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 23

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `fecha` | varchar(255) | NO | PRI |  |  |  |
| 2 | `valor` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `fecha`

## `jisparking`.`DM_tpm`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 502

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `fecha` | varchar(255) | NO | PRI |  |  |  |
| 2 | `valor` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `fecha`

## `jisparking`.`DM_uf`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 740

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `fecha` | varchar(255) | NO | PRI |  |  |  |
| 2 | `valor` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `fecha`

## `jisparking`.`DM_utm`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 26

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `fecha` | varchar(255) | NO | PRI |  |  |  |
| 2 | `valor` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `fecha`

## `jisparking`.`ETL_STATUS`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 12

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `process_name` | varchar(100) | NO | PRI |  |  |  |
| 2 | `last_run_timestamp` | timestamp | NO |  |  |  |  |
| 3 | `last_run_status` | varchar(20) | NO |  |  |  |  |
| 4 | `details` | text | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `process_name`

## `jisparking`.`HECHOS_DEPOSITOS_DETALLE`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 21707

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `deposit_id` | int | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES | MUL |  |  |  |
| 4 | `collection_date` | date | YES |  |  |  |  |
| 5 | `deposit_date` | date | YES |  |  |  |  |
| 6 | `latency_days` | int | YES |  |  |  |  |
| 7 | `recaudado` | decimal(12,0) | YES |  |  |  |  |
| 8 | `depositado` | decimal(12,0) | YES |  |  |  |  |
| 9 | `diferencia` | decimal(12,0) | YES |  |  |  |  |
| 10 | `support` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`
- `idx_branch_date` (no único): `branch_office_id`, `deposit_date`

## `jisparking`.`INASISTENCIAS`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 1349

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `RUT` | varchar(20) | YES |  |  |  |  |
| 3 | `Trabajador` | varchar(255) | YES | MUL |  |  |  |
| 4 | `Especialidad` | varchar(255) | YES |  |  |  |  |
| 5 | `Sucursal` | varchar(255) | YES | MUL |  |  |  |
| 6 | `Contrato` | varchar(255) | YES |  |  |  |  |
| 7 | `Supervisor` | varchar(255) | YES |  |  |  |  |
| 8 | `Turno` | varchar(50) | YES |  |  |  |  |
| 9 | `FechaInasistencia` | date | YES | MUL |  |  |  |
| 10 | `Motivo` | varchar(255) | YES |  |  |  |  |
| 11 | `ObservacionPermiso` | text | YES |  |  |  |  |
| 12 | `FechaCarga` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |

**Índices**

- `PRIMARY` (único): `id`
- `idx_fecha_inasistencia` (no único): `FechaInasistencia`
- `idx_sucursal_inasistencia` (no único): `Sucursal`
- `idx_trabajador_inasistencia` (no único): `Trabajador`

## `jisparking`.`KPI_INGRESOS_DIARIO`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 79647

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `date` | date | NO |  |  |  |  |
| 3 | `periodo` | varchar(20) | NO |  |  |  |  |
| 4 | `año` | int | NO |  |  |  |  |
| 5 | `branch_office_id` | varchar(20) | NO |  |  |  |  |
| 6 | `clave` | varchar(32) | NO |  |  |  |  |
| 7 | `cash_amount` | float | YES |  | `0` |  |  |
| 8 | `cash_net_amount` | float | YES |  | `0` |  |  |
| 9 | `card_amount` | float | YES |  | `0` |  |  |
| 10 | `card_net_amount` | float | YES |  | `0` |  |  |
| 11 | `subscribers` | float | YES |  | `0` |  |  |
| 12 | `ticket_number` | float | YES |  | `0` |  |  |
| 13 | `ppto` | float | YES |  | `0` |  |  |
| 14 | `metrica` | varchar(32) | NO |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`KPI_INGRESOS_IMG_MES`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 6036

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `date` | date | YES |  |  |  |  |
| 3 | `periodo` | varchar(50) | YES |  |  |  |  |
| 4 | `año` | int | YES |  |  |  |  |
| 5 | `branch_office_id` | int | YES |  |  |  |  |
| 6 | `clave` | int | YES |  |  |  |  |
| 7 | `ind` | int | YES |  |  |  |  |
| 8 | `cash_amount` | bigint | YES |  |  |  |  |
| 9 | `cash_net_amount` | bigint | YES |  |  |  |  |
| 10 | `card_amount` | bigint | YES |  |  |  |  |
| 11 | `card_net_amount` | bigint | YES |  |  |  |  |
| 12 | `subscribers` | bigint | YES |  |  |  |  |
| 13 | `ticket_number` | bigint | YES |  |  |  |  |
| 14 | `ppto` | bigint | YES |  |  |  |  |
| 15 | `metrica` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`PBI_INGRESOS_TOTALES`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `Periodo` | varchar(255) | YES |  |  |  |  |
| 3 | `Año` | varchar(255) | YES |  |  |  |  |
| 4 | `Mes` | varchar(255) | YES |  |  |  |  |
| 5 | `period` | varchar(255) | YES |  |  |  |  |
| 6 | `clave` | varchar(255) | YES |  |  |  |  |
| 7 | `branch_office_id` | varchar(255) | YES |  |  |  |  |
| 8 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 9 | `efectivo` | varchar(255) | YES |  |  |  |  |
| 10 | `tarjeta` | varchar(255) | YES |  |  |  |  |
| 11 | `abonados` | varchar(255) | YES |  |  |  |  |
| 12 | `ticket_number` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`PPTO_DIARIO`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 95040

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `date` | date | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `cash_amount` | float | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`RECURSOS_DIARIOS`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 347

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `fecha` | date | NO | MUL |  |  |  |
| 3 | `titulo` | varchar(255) | YES |  |  |  |  |
| 4 | `titulo_display` | varchar(200) | YES |  |  |  |  |
| 5 | `descripcion` | text | YES |  |  |  |  |
| 6 | `categoria` | varchar(100) | YES |  |  |  |  |
| 7 | `autor` | varchar(200) | YES |  |  |  |  |
| 8 | `licencia` | varchar(100) | YES |  |  |  |  |
| 9 | `fuente` | varchar(50) | YES |  |  |  |  |
| 10 | `tags` | text | YES |  |  |  |  |
| 11 | `url_fuente` | text | YES |  |  |  |  |
| 12 | `path_imagen` | text | YES |  |  |  |  |
| 13 | `nombre_archivo_original` | varchar(255) | YES |  |  |  |  |
| 14 | `width` | int | YES |  |  |  |  |
| 15 | `height` | int | YES |  |  |  |  |
| 16 | `color_dominante` | varchar(7) | YES |  |  |  |  |
| 17 | `fecha_creacion` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |

**Índices**

- `PRIMARY` (único): `id`
- `uq_fecha_fuente` (único): `fecha`, `fuente`

## `jisparking`.`REGISTRO_ETL`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 20742

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `nombre_job` | varchar(255) | NO |  |  |  |  |
| 3 | `timestamp_inicio` | datetime | NO |  |  |  |  |
| 4 | `timestamp_fin` | datetime | YES |  |  |  |  |
| 5 | `estado` | varchar(50) | NO |  |  |  |  |
| 6 | `mensaje` | text | YES |  |  |  |  |
| 7 | `ejecutado_por` | varchar(100) | NO |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`WHATSAPP_SEND_LOG`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 69

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | bigint | NO | PRI |  | auto_increment |  |
| 2 | `report_type` | varchar(80) | NO | MUL |  |  |  |
| 3 | `period_key` | varchar(20) | NO |  |  |  |  |
| 4 | `recipient_name` | varchar(150) | YES |  |  |  |  |
| 5 | `recipient_phone` | varchar(30) | NO |  |  |  |  |
| 6 | `template_name` | varchar(120) | NO |  |  |  |  |
| 7 | `filename` | varchar(255) | YES |  |  |  |  |
| 8 | `media_id` | varchar(120) | YES |  |  |  |  |
| 9 | `status` | varchar(20) | NO | MUL |  |  |  |
| 10 | `response_json` | text | YES |  |  |  |  |
| 11 | `error_message` | text | YES |  |  |  |  |
| 12 | `sent_at` | datetime | NO |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`
- `idx_wslog_lookup` (no único): `report_type`, `period_key`, `recipient_phone`, `sent_at`
- `idx_wslog_status` (no único): `status`, `sent_at`

## `jisparking`.`ai_deposit_matches`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `bank_statement_id` | int | YES | MUL |  |  | ID del registro en bank_statements |
| 3 | `transbank_statement_id` | int | YES | MUL |  |  | ID del registro en transbank_statements |
| 4 | `deposit_id` | int | YES | MUL |  |  | ID del depósito encontrado (FK a deposits) |
| 5 | `excel_deposit_number` | varchar(255) | YES | MUL |  |  | Número de depósito del Excel |
| 6 | `excel_branch_office` | varchar(255) | YES |  |  |  | Sucursal del Excel (texto) |
| 7 | `excel_amount` | int | YES |  |  |  | Monto del Excel |
| 8 | `excel_date` | varchar(255) | YES |  |  |  | Fecha del Excel |
| 9 | `db_deposit_id` | int | YES | MUL |  |  | ID del depósito en BD |
| 10 | `db_branch_office_id` | int | YES |  |  |  | ID de sucursal en BD |
| 11 | `db_branch_office_name` | varchar(255) | YES |  |  |  | Nombre de sucursal en BD |
| 12 | `db_payment_number` | int | YES |  |  |  | Número de pago en BD |
| 13 | `db_collection_amount` | int | YES |  |  |  | Monto de cobro en BD |
| 14 | `db_deposited_amount` | int | YES |  |  |  | Monto depositado en BD |
| 15 | `db_collection_date` | varchar(255) | YES |  |  |  | Fecha de cobro en BD |
| 16 | `match_confidence` | decimal(5,2) | YES | MUL |  |  | Confianza del match (0-100) |
| 17 | `match_reason` | text | YES |  |  |  | Razón del match explicada por IA |
| 18 | `match_type` | enum('exact','ai_suggested','manual') | YES | MUL | `ai_suggested` |  | Tipo de match |
| 19 | `is_confirmed` | tinyint(1) | YES | MUL | `0` |  | Si el match fue confirmado manualmente |
| 20 | `is_rejected` | tinyint(1) | YES | MUL | `0` |  | Si el match fue rechazado |
| 21 | `ai_model_used` | varchar(100) | YES |  |  |  | Modelo de IA usado (ej: gpt-4, gpt-3.5-turbo) |
| 22 | `ai_prompt_tokens` | int | YES |  |  |  | Tokens usados en el prompt |
| 23 | `ai_completion_tokens` | int | YES |  |  |  | Tokens usados en la respuesta |
| 24 | `processing_time_ms` | int | YES |  |  |  | Tiempo de procesamiento en milisegundos |
| 25 | `created_at` | timestamp | YES | MUL | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |
| 26 | `updated_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |
| 27 | `created_by_user_id` | int | YES |  |  |  | ID del usuario que creó el match |
| 28 | `confirmed_by_user_id` | int | YES |  |  |  | ID del usuario que confirmó el match |

**Claves foráneas (salientes)**

| Columna | Referencia | Constraint |
| --- | --- | --- |
| `bank_statement_id` | `bank_statements`.`id` | `fk_ai_match_bank_statement` |
| `deposit_id` | `deposits`.`id` | `fk_ai_match_deposit` |
| `transbank_statement_id` | `transbank_statements`.`id` | `fk_ai_match_transbank_statement` |

**Índices**

- `PRIMARY` (único): `id`
- `idx_bank_statement_id` (no único): `bank_statement_id`
- `idx_created_at` (no único): `created_at`
- `idx_db_deposit_id` (no único): `db_deposit_id`
- `idx_deposit_id` (no único): `deposit_id`
- `idx_excel_db_deposit_number` (no único): `excel_deposit_number`, `db_payment_number`
- `idx_excel_deposit_number` (no único): `excel_deposit_number`
- `idx_is_confirmed` (no único): `is_confirmed`
- `idx_is_rejected` (no único): `is_rejected`
- `idx_match_confidence` (no único): `match_confidence`
- `idx_match_type_confirmed` (no único): `match_type`, `is_confirmed`
- `idx_transbank_statement_id` (no único): `transbank_statement_id`

## `jisparking`.`alert_types`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `alert_type` | varchar(255) | YES |  |  |  |  |
| 3 | `added_date` | varchar(255) | YES |  |  |  |  |
| 4 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`alert_users`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 4

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `alert_type_id` | varchar(255) | YES |  |  |  |  |
| 3 | `user_id` | varchar(255) | YES |  |  |  |  |
| 4 | `added_date` | varchar(255) | YES |  |  |  |  |
| 5 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`alerts`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 132

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `alert_user_id` | varchar(255) | YES |  |  |  |  |
| 3 | `alert_type_id` | varchar(255) | YES |  |  |  |  |
| 4 | `status_id` | varchar(255) | YES |  |  |  |  |
| 5 | `added_date` | varchar(255) | YES |  |  |  |  |
| 6 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`bank_account_users`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `user_id` | int | YES |  |  |  |  |
| 3 | `bank_account_type_id` | int | YES |  |  |  |  |
| 4 | `rut` | varchar(255) | YES |  |  |  |  |
| 5 | `bank_account_name` | varchar(255) | YES |  |  |  |  |
| 6 | `bank_account_number` | int | YES |  |  |  |  |
| 7 | `bank_account_email` | varchar(255) | YES |  |  |  |  |
| 8 | `added_date` | datetime | YES |  |  |  |  |
| 9 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`bank_statement_dte_applications`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 36

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `dte_id` | int | NO | MUL |  |  |  |
| 3 | `folio` | int | YES |  |  |  |  |
| 4 | `deposit_number` | varchar(255) | NO | MUL |  |  |  |
| 5 | `deposit_date` | varchar(255) | NO |  |  |  |  |
| 6 | `amount` | int | NO |  |  |  |  |
| 7 | `rut` | varchar(255) | NO |  |  |  |  |
| 8 | `period` | varchar(255) | NO |  |  |  |  |
| 9 | `applied_at` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`
- `idx_dte_id` (no único): `dte_id`
- `uk_cartola_natural` (único): `deposit_number`, `deposit_date`, `amount`, `rut`, `period`

## `jisparking`.`bank_statement_histories`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 611

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `bank_statement_type_id` | int | YES |  |  |  |  |
| 3 | `rut` | varchar(255) | YES |  |  |  |  |
| 4 | `deposit_number` | varchar(255) | YES |  |  |  |  |
| 5 | `amount` | int | YES |  |  |  |  |
| 6 | `period` | varchar(255) | YES | MUL |  |  |  |
| 7 | `deposit_date` | varchar(255) | YES |  |  |  |  |
| 8 | `added_date` | datetime | YES | MUL |  |  |  |

**Índices**

- `PRIMARY` (único): `id`
- `idx_bank_statement_histories_archived` (no único): `added_date`
- `idx_bank_statement_histories_period` (no único): `period`
- `uk_bank_statement_histories_natural` (único): `period`, `bank_statement_type_id`, `deposit_number`, `deposit_date`, `amount`, `rut`

## `jisparking`.`bank_statements`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 649

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `bank_statement_type_id` | int | YES |  |  |  |  |
| 3 | `rut` | varchar(255) | YES |  |  |  |  |
| 4 | `deposit_number` | varchar(255) | YES |  |  |  |  |
| 5 | `amount` | int | YES |  |  |  |  |
| 6 | `period` | varchar(255) | YES |  |  |  |  |
| 7 | `deposit_date` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`banks`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 24

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `bank` | varchar(255) | YES |  |  |  |  |
| 3 | `added_date` | varchar(255) | YES |  |  |  |  |
| 4 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`bitacora`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 4

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `fecha` | date | NO |  |  |  |  |
| 3 | `categoria` | varchar(100) | NO |  |  |  |  |
| 4 | `descripcion` | text | NO |  |  |  |  |
| 5 | `branch_office_id` | int | YES | MUL |  |  |  |
| 6 | `user_rut` | varchar(12) | NO |  |  |  |  |
| 7 | `fecha_registro` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |

**Claves foráneas (salientes)**

| Columna | Referencia | Constraint |
| --- | --- | --- |
| `branch_office_id` | `branch_offices`.`id` | `fk_branch_office` |

**Índices**

- `PRIMARY` (único): `id`
- `fk_branch_office` (no único): `branch_office_id`

## `jisparking`.`branch_offices`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 104

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `region_id` | int | YES |  |  |  |  |
| 3 | `commune_id` | int | YES |  |  |  |  |
| 4 | `segment_id` | int | YES |  |  |  |  |
| 5 | `zone_id` | int | YES |  |  |  |  |
| 6 | `principal_id` | int | YES |  |  |  |  |
| 7 | `getaway_machine_id` | int | YES |  |  |  |  |
| 8 | `visibility_id` | int | YES |  |  |  |  |
| 9 | `basement_id` | int | YES |  |  |  |  |
| 10 | `spots` | int | YES |  |  |  |  |
| 11 | `status_id` | int | YES |  |  |  |  |
| 12 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 13 | `address` | varchar(255) | YES |  |  |  |  |
| 14 | `principal_supervisor` | varchar(255) | YES |  |  |  |  |
| 15 | `rut_who_receives` | varchar(255) | YES |  |  |  |  |
| 16 | `person_who_receives` | varchar(255) | YES |  |  |  |  |
| 17 | `phone_who_receives` | varchar(255) | YES |  |  |  |  |
| 18 | `opening_date` | varchar(255) | YES |  |  |  |  |
| 19 | `dte_code` | varchar(255) | YES |  |  |  |  |
| 20 | `opening_hour` | varchar(255) | YES |  |  |  |  |
| 21 | `closing_hour` | varchar(255) | YES |  |  |  |  |
| 22 | `added_date` | datetime | YES |  |  |  |  |
| 23 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`branch_offices_transbanks`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 47

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `transbank_code` | varchar(255) | YES |  |  |  |  |
| 4 | `status` | int | YES |  | `0` |  |  |
| 5 | `added_date` | varchar(255) | YES |  |  |  |  |
| 6 | `updated_date` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`capitulations`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 2153

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `document_type_id` | int | YES |  |  |  |  |
| 3 | `capitulation_type_id` | int | YES |  |  |  |  |
| 4 | `branch_office_id` | int | YES |  |  |  |  |
| 5 | `expense_type_id` | int | YES |  |  |  |  |
| 6 | `status_id` | int | YES |  |  |  |  |
| 7 | `document_date` | date | YES |  |  |  |  |
| 8 | `document_number` | varchar(255) | YES |  |  |  |  |
| 9 | `user_rut` | varchar(255) | YES |  |  |  |  |
| 10 | `supplier_rut` | varchar(255) | YES |  |  |  |  |
| 11 | `description` | varchar(255) | YES |  |  |  |  |
| 12 | `amount` | int | YES |  |  |  |  |
| 13 | `support` | varchar(255) | YES |  |  |  |  |
| 14 | `why_was_rejected` | varchar(255) | YES |  |  |  |  |
| 15 | `payment_date` | varchar(255) | YES |  |  |  |  |
| 16 | `payment_number` | varchar(255) | YES |  |  |  |  |
| 17 | `payment_support` | varchar(255) | YES |  |  |  |  |
| 18 | `period` | varchar(255) | YES |  |  |  |  |
| 19 | `added_date` | datetime | YES |  |  |  |  |
| 20 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`carbon_monoxides`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `branch_office_id` | varchar(255) | YES |  |  |  |  |
| 3 | `measure_value` | varchar(255) | YES |  |  |  |  |
| 4 | `support` | varchar(255) | YES |  |  |  |  |
| 5 | `added_date` | varchar(255) | YES |  |  |  |  |
| 6 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`cash_reserves`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 3

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `branch_office_id` | varchar(255) | YES |  |  |  |  |
| 3 | `cashier_id` | varchar(255) | YES |  |  |  |  |
| 4 | `amount` | varchar(255) | YES |  |  |  |  |
| 5 | `added_date` | varchar(255) | YES |  |  |  |  |
| 6 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`cashier_sync_commands`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 37

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | NO |  |  |  |  |
| 3 | `cashier_id` | int | NO | MUL |  |  |  |
| 4 | `batch_id` | varchar(36) | YES | MUL |  |  |  |
| 5 | `status` | varchar(20) | NO |  | `pendiente` |  |  |
| 6 | `requester_wa_id` | varchar(32) | NO |  |  |  |  |
| 7 | `action` | varchar(50) | NO |  | `sync_sales` |  |  |
| 8 | `created_at` | datetime | YES |  |  |  |  |
| 9 | `started_at` | datetime | YES |  |  |  |  |
| 10 | `completed_at` | datetime | YES |  |  |  |  |
| 11 | `result_text` | text | YES |  |  |  |  |
| 12 | `error_text` | text | YES |  |  |  |  |
| 13 | `duration_ms` | int | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`
- `idx_batch` (no único): `batch_id`
- `idx_cashier_status` (no único): `cashier_id`, `status`

## `jisparking`.`cashiers`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 274

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES | MUL |  |  |  |
| 3 | `folio_segment_id` | int | YES | MUL |  |  |  |
| 4 | `getaway_machine_id` | int | YES | MUL |  |  |  |
| 5 | `transbank_status_id` | int | YES | MUL |  |  |  |
| 6 | `folio_request_status_id` | int | YES | MUL |  |  |  |
| 7 | `visibility_status_id` | int | YES | MUL |  |  |  |
| 8 | `transbank_type_id` | int | YES |  |  |  |  |
| 9 | `cashier` | varchar(255) | YES |  |  |  |  |
| 10 | `anydesk` | varchar(255) | YES |  |  |  |  |
| 11 | `rustdesk` | varchar(255) | YES |  |  |  |  |
| 12 | `available_folios` | int | YES |  |  |  |  |
| 13 | `transbank_code` | varchar(255) | YES |  |  |  |  |
| 14 | `added_date` | datetime | YES |  |  |  |  |
| 15 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`
- `all_indexes` (no único): `branch_office_id`, `folio_segment_id`, `getaway_machine_id`, `transbank_status_id`, `folio_request_status_id`, `visibility_status_id`
- `branch_office_id` (no único): `branch_office_id`
- `folio_request_status_id` (no único): `folio_request_status_id`
- `folio_segment_id` (no único): `folio_segment_id`
- `getaway_machine_id` (no único): `getaway_machine_id`
- `transbank_status_id` (no único): `transbank_status_id`
- `visibility_status_id` (no único): `visibility_status_id`

## `jisparking`.`collections`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 83518

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `cashier_id` | int | YES |  |  |  |  |
| 4 | `cash_gross_amount` | int | YES |  |  |  |  |
| 5 | `cash_net_amount` | int | YES |  |  |  |  |
| 6 | `card_gross_amount` | int | YES |  |  |  |  |
| 7 | `card_net_amount` | int | YES |  |  |  |  |
| 8 | `subscribers` | int | YES |  |  |  |  |
| 9 | `total_tickets` | int | YES |  |  |  |  |
| 10 | `added_date` | date | YES |  |  |  |  |
| 11 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`collections_10_09_2025`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 57650

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `cashier_id` | int | YES |  |  |  |  |
| 4 | `cash_gross_amount` | int | YES |  |  |  |  |
| 5 | `cash_net_amount` | int | YES |  |  |  |  |
| 6 | `card_gross_amount` | int | YES |  |  |  |  |
| 7 | `card_net_amount` | int | YES |  |  |  |  |
| 8 | `subscribers` | int | YES |  |  |  |  |
| 9 | `total_tickets` | int | YES |  |  |  |  |
| 10 | `added_date` | date | YES |  |  |  |  |
| 11 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`communes`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 345

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  |  |  |  |
| 2 | `region_id` | int | YES |  |  |  |  |
| 3 | `commune` | varchar(255) | YES |  |  |  |  |
| 4 | `added_date` | datetime | YES |  |  |  |  |
| 5 | `updated_date` | datetime | YES |  |  |  |  |

## `jisparking`.`contract_types`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 3

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `contract_type` | varchar(255) | YES |  |  |  |  |
| 3 | `added_date` | varchar(255) | YES |  |  |  |  |
| 4 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`contracts`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 49

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `contract_type_id` | int | YES |  |  |  |  |
| 4 | `rut` | varchar(255) | YES |  |  |  |  |
| 5 | `client` | varchar(255) | YES |  |  |  |  |
| 6 | `start_date` | date | YES |  |  |  |  |
| 7 | `end_date` | date | YES |  |  |  |  |
| 8 | `renovation_date` | date | YES |  |  |  |  |
| 9 | `address` | varchar(255) | YES |  |  |  |  |
| 10 | `currency` | varchar(255) | YES |  |  |  |  |
| 11 | `amount` | int | YES |  |  |  |  |
| 12 | `support` | varchar(255) | YES |  |  |  |  |
| 13 | `added_date` | datetime | YES |  |  |  |  |
| 14 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`customers`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 5153

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `region_id` | int | YES |  |  |  |  |
| 3 | `commune_id` | int | YES |  |  |  |  |
| 4 | `rut` | varchar(255) | YES |  |  |  |  |
| 5 | `customer` | varchar(255) | YES |  |  |  |  |
| 6 | `email` | varchar(255) | YES |  |  |  |  |
| 7 | `phone` | varchar(255) | YES |  |  |  |  |
| 8 | `activity` | varchar(255) | YES |  |  |  |  |
| 9 | `address` | varchar(255) | YES |  |  |  |  |
| 10 | `added_date` | datetime | YES |  |  |  |  |
| 11 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`delivery_address_tags`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 33

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `region_id` | int | NO | MUL |  |  |  |
| 3 | `commune_id` | int | NO | MUL |  |  |  |
| 4 | `branch_office` | varchar(512) | NO |  |  |  |  |
| 5 | `address` | varchar(1024) | NO |  |  |  |  |
| 6 | `supervisor_rut` | varchar(32) | NO |  |  |  |  |
| 7 | `supervisor` | varchar(512) | NO |  |  |  |  |
| 8 | `phone` | varchar(64) | YES |  |  |  |  |
| 9 | `company_name` | varchar(512) | NO |  |  |  |  |
| 10 | `company_rut` | varchar(64) | NO |  |  |  |  |
| 11 | `company_phone` | varchar(64) | NO |  |  |  |  |
| 12 | `company_address` | varchar(1024) | NO |  |  |  |  |
| 13 | `added_date` | datetime | YES |  |  |  |  |
| 14 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`
- `idx_delivery_address_tags_commune` (no único): `commune_id`
- `idx_delivery_address_tags_region` (no único): `region_id`

## `jisparking`.`demarcations`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `branch_office_id` | varchar(255) | YES |  |  |  |  |
| 3 | `material_costs` | varchar(255) | YES |  |  |  |  |
| 4 | `labor_costs` | varchar(255) | YES |  |  |  |  |
| 5 | `made_arrows` | varchar(255) | YES |  |  |  |  |
| 6 | `made_pedestrian_crossing` | varchar(255) | YES |  |  |  |  |
| 7 | `made_disability` | varchar(255) | YES |  |  |  |  |
| 8 | `made_island` | varchar(255) | YES |  |  |  |  |
| 9 | `made_pregnant` | varchar(255) | YES |  |  |  |  |
| 10 | `made_wall` | varchar(255) | YES |  |  |  |  |
| 11 | `file_made_arrows` | varchar(255) | YES |  |  |  |  |
| 12 | `file_made_pedestrian_crossing` | varchar(255) | YES |  |  |  |  |
| 13 | `file_made_disability` | varchar(255) | YES |  |  |  |  |
| 14 | `file_made_island` | varchar(255) | YES |  |  |  |  |
| 15 | `file_made_pregnant` | varchar(255) | YES |  |  |  |  |
| 16 | `file_made_wall` | varchar(255) | YES |  |  |  |  |
| 17 | `added_date` | varchar(255) | YES |  |  |  |  |
| 18 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`deposits`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 101835

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `payment_type_id` | int | YES |  |  |  |  |
| 4 | `collection_id` | int | YES |  |  |  |  |
| 5 | `reject_reason_id` | int | YES |  |  |  |  |
| 6 | `status_id` | int | YES |  |  |  |  |
| 7 | `deposited_amount` | int | YES |  |  |  |  |
| 8 | `payment_number` | varchar(255) | YES |  |  |  |  |
| 9 | `collection_amount` | int | YES |  |  |  |  |
| 10 | `deposit_date` | date | YES |  |  |  |  |
| 11 | `collection_date` | date | YES |  |  |  |  |
| 12 | `support` | varchar(255) | YES |  |  |  |  |
| 13 | `added_date` | datetime | YES |  |  |  |  |
| 14 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`deposits_duplicates_backup`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 622

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `payment_type_id` | int | YES |  |  |  |  |
| 4 | `collection_id` | int | YES |  |  |  |  |
| 5 | `status_id` | int | YES |  |  |  |  |
| 6 | `deposited_amount` | int | YES |  |  |  |  |
| 7 | `payment_number` | varchar(255) | YES |  |  |  |  |
| 8 | `collection_amount` | int | YES |  |  |  |  |
| 9 | `collection_date` | date | YES |  |  |  |  |
| 10 | `support` | varchar(255) | YES |  |  |  |  |
| 11 | `added_date` | datetime | YES |  |  |  |  |
| 12 | `updated_date` | datetime | YES |  |  |  |  |

## `jisparking`.`dte_references`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `dte_id` | int | NO | MUL |  |  |  |
| 3 | `reference_type_id` | varchar(16) | YES |  |  |  | Código SII ej. 33, 34, 801 |
| 4 | `reference_date_id` | varchar(255) | YES |  |  |  | Folio o N° doc. ref. |
| 5 | `reference_code` | varchar(64) | YES |  |  |  | Fecha referencia (YYYY-MM-DD) |
| 6 | `reference_description` | varchar(512) | YES |  |  |  | Razón referencia |
| 7 | `added_date` | datetime | YES |  |  |  |  |

**Claves foráneas (salientes)**

| Columna | Referencia | Constraint |
| --- | --- | --- |
| `dte_id` | `dtes`.`id` | `fk_dte_references_dte` |

**Índices**

- `PRIMARY` (único): `id`
- `idx_dte_references_dte_id` (no único): `dte_id`

## `jisparking`.`dtes`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 1462062

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `cashier_id` | int | YES |  |  |  |  |
| 4 | `dte_type_id` | int | YES |  |  |  |  |
| 5 | `dte_version_id` | int | YES |  |  |  |  |
| 6 | `expense_type_id` | int | YES |  |  |  |  |
| 7 | `payment_type_id` | int | YES |  |  |  |  |
| 8 | `chip_id` | int | YES |  |  |  |  |
| 9 | `reason_id` | int | YES |  |  |  |  |
| 10 | `status_id` | int | YES |  |  |  |  |
| 11 | `massive_resend_status_id` | int | YES |  |  |  |  |
| 12 | `category_id` | int | YES |  |  |  |  |
| 13 | `rut` | varchar(255) | YES |  |  |  |  |
| 14 | `folio` | int | YES |  |  |  |  |
| 15 | `denied_folio` | varchar(255) | YES |  |  |  |  |
| 16 | `cash_amount` | int | YES |  |  |  |  |
| 17 | `card_amount` | int | YES |  |  |  |  |
| 18 | `subtotal` | int | YES |  |  |  |  |
| 19 | `tax` | int | YES |  |  |  |  |
| 20 | `discount` | int | YES |  |  |  |  |
| 21 | `total` | int | YES |  |  |  |  |
| 22 | `ticket_serial_number` | int | YES |  |  |  |  |
| 23 | `ticket_hour` | varchar(255) | YES |  |  |  |  |
| 24 | `ticket_transaction_number` | int | YES |  |  |  |  |
| 25 | `ticket_dispenser_number` | int | YES |  |  |  |  |
| 26 | `ticket_number` | int | YES |  |  |  |  |
| 27 | `ticket_station_number` | int | YES |  |  |  |  |
| 28 | `ticket_sa` | varchar(255) | YES |  |  |  |  |
| 29 | `ticket_correlative` | int | YES |  |  |  |  |
| 30 | `entrance_hour` | varchar(255) | YES |  |  |  |  |
| 31 | `exit_hour` | varchar(255) | YES |  |  |  |  |
| 32 | `comment` | varchar(255) | YES |  |  |  |  |
| 33 | `payment_number` | varchar(255) | YES |  |  |  |  |
| 34 | `payment_amount` | int | YES |  |  |  |  |
| 35 | `payment_date` | varchar(255) | YES |  |  |  |  |
| 36 | `payment_comment` | varchar(255) | YES |  |  |  |  |
| 37 | `quantity` | int | YES |  |  |  |  |
| 38 | `period` | varchar(255) | YES |  |  |  |  |
| 39 | `support` | varchar(255) | YES |  |  |  |  |
| 40 | `added_date` | datetime | YES |  |  |  |  |
| 41 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`dtes2`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 887

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `cashier_id` | int | YES |  |  |  |  |
| 4 | `dte_type_id` | int | YES |  |  |  |  |
| 5 | `dte_version_id` | int | YES |  |  |  |  |
| 6 | `expense_type_id` | int | YES |  |  |  |  |
| 7 | `payment_type_id` | int | YES |  |  |  |  |
| 8 | `chip_id` | int | YES |  |  |  |  |
| 9 | `reason_id` | int | YES |  |  |  |  |
| 10 | `status_id` | int | YES |  |  |  |  |
| 11 | `shopping_order_status_id` | int | YES |  |  |  |  |
| 12 | `rut` | varchar(255) | YES |  |  |  |  |
| 13 | `folio` | int | YES |  |  |  |  |
| 14 | `denied_folio` | varchar(255) | YES |  |  |  |  |
| 15 | `cash_amount` | int | YES |  |  |  |  |
| 16 | `card_amount` | int | YES |  |  |  |  |
| 17 | `subtotal` | int | YES |  |  |  |  |
| 18 | `tax` | int | YES |  |  |  |  |
| 19 | `discount` | int | YES |  |  |  |  |
| 20 | `total` | int | YES |  |  |  |  |
| 21 | `ticket_serial_number` | int | YES |  |  |  |  |
| 22 | `ticket_hour` | varchar(255) | YES |  |  |  |  |
| 23 | `ticket_transaction_number` | int | YES |  |  |  |  |
| 24 | `ticket_dispenser_number` | int | YES |  |  |  |  |
| 25 | `ticket_number` | int | YES |  |  |  |  |
| 26 | `ticket_station_number` | int | YES |  |  |  |  |
| 27 | `ticket_sa` | varchar(255) | YES |  |  |  |  |
| 28 | `ticket_correlative` | int | YES |  |  |  |  |
| 29 | `entrance_hour` | varchar(255) | YES |  |  |  |  |
| 30 | `exit_hour` | varchar(255) | YES |  |  |  |  |
| 31 | `comment` | varchar(255) | YES |  |  |  |  |
| 32 | `payment_number` | varchar(255) | YES |  |  |  |  |
| 33 | `payment_amount` | int | YES |  |  |  |  |
| 34 | `payment_date` | varchar(255) | YES |  |  |  |  |
| 35 | `payment_comment` | varchar(255) | YES |  |  |  |  |
| 36 | `shopping_order_reference` | varchar(255) | YES |  |  |  |  |
| 37 | `shopping_order_date` | date | YES |  |  |  |  |
| 38 | `shopping_order_description` | varchar(255) | YES |  |  |  |  |
| 39 | `period` | varchar(255) | YES |  |  |  |  |
| 40 | `support` | varchar(255) | YES |  |  |  |  |
| 41 | `added_date` | datetime | YES |  |  |  |  |
| 42 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`dtes_repetidos`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 296

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `folio` | varchar(255) | YES |  |  |  |  |
| 3 | `razon_social` | varchar(255) | YES |  |  |  |  |
| 4 | `dte_type_id` | int | YES |  |  |  |  |
| 5 | `pagado` | int | YES |  |  |  |  |
| 6 | `existencia` | int | YES |  |  |  |  |
| 7 | `nc` | int | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`eerr`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 221119

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `seat_id` | int | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `accounting_account` | text | YES |  |  |  |  |
| 5 | `amount` | int | YES |  |  |  |  |
| 6 | `period` | varchar(255) | YES |  |  |  |  |
| 7 | `added_date` | datetime | YES |  |  |  |  |
| 8 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`eerr2`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 207774

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `seat_id` | int | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `accounting_account` | text | YES |  |  |  |  |
| 5 | `amount` | int | YES |  |  |  |  |
| 6 | `period` | varchar(255) | YES |  |  |  |  |
| 7 | `added_date` | datetime | YES |  |  |  |  |
| 8 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`employees_interships`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 23

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `intern` | varchar(255) | YES |  |  |  |  |
| 4 | `observations` | varchar(255) | YES |  |  |  |  |
| 5 | `support` | varchar(255) | YES |  |  |  |  |
| 6 | `added_date` | datetime | YES |  |  |  |  |
| 7 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`employees_interships_answers`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 161

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `intership_id` | int | YES |  |  |  |  |
| 3 | `question_id` | int | YES |  |  |  |  |
| 4 | `answer_id` | int | YES |  |  |  |  |
| 5 | `added_date` | datetime | YES |  |  |  |  |
| 6 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`eventos_historicos`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 2863

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `dia` | int | NO | MUL |  |  |  |
| 3 | `mes` | int | NO |  |  |  |  |
| 4 | `anio` | int | NO |  |  |  |  |
| 5 | `descripcion` | text | NO |  |  |  |  |
| 6 | `categoria` | varchar(50) | YES |  |  |  |  |
| 7 | `relevancia` | varchar(20) | YES |  |  |  |  |
| 8 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |
| 9 | `tipo` | varchar(50) | YES |  |  |  |  |
| 10 | `is_feriado` | tinyint(1) | YES |  | `0` |  | Indica si el día es feriado (1) o día normal (0) |
| 11 | `is_domingo` | tinyint(1) | YES |  | `0` |  | Indica si el día es domingo (1) o no (0) |

**Índices**

- `PRIMARY` (único): `id`
- `dia` (no único): `dia`, `mes`

## `jisparking`.`expense_types`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 92

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `capitulation_visibility_id` | int | YES |  |  |  |  |
| 3 | `eerr_visibility_id` | int | YES |  |  |  |  |
| 4 | `track_visibility_id` | int | YES |  |  |  |  |
| 5 | `positive_negative_id` | int | YES |  |  |  |  |
| 6 | `expense_type` | varchar(255) | YES |  |  |  |  |
| 7 | `accounting_account` | varchar(255) | YES |  |  |  |  |
| 8 | `type` | int | YES |  |  |  |  |
| 9 | `group_detail` | int | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`folios`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 3763922

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `folio` | varchar(255) | YES | MUL |  |  |  |
| 3 | `branch_office_id` | varchar(255) | YES | MUL |  |  |  |
| 4 | `cashier_id` | varchar(255) | YES | MUL |  |  |  |
| 5 | `folio_segment_id` | varchar(255) | YES |  |  |  |  |
| 6 | `requested_status_id` | varchar(255) | YES | MUL |  |  |  |
| 7 | `used_status_id` | varchar(255) | YES | MUL |  |  |  |
| 8 | `billed_status_id` | varchar(255) | YES | MUL |  |  |  |
| 9 | `added_date` | varchar(255) | YES | MUL |  |  |  |
| 10 | `updated_date` | varchar(255) | YES |  |  |  |  |

**Índices**

- `added_date` (no único): `added_date`
- `all_indexes` (no único): `folio`, `branch_office_id`, `cashier_id`
- `billed_status_id` (no único): `billed_status_id`
- `branch_office_id` (no único): `branch_office_id`
- `cashier_id` (no único): `cashier_id`
- `folio` (no único): `folio`
- `requested_status_id` (no único): `requested_status_id`
- `used_status_id` (no único): `used_status_id`

## `jisparking`.`frases_motivadoras`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 1121

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `frase` | text | NO |  |  |  |  |
| 3 | `autor` | varchar(255) | NO | MUL |  |  |  |
| 4 | `clasificacion` | varchar(100) | YES | MUL |  |  |  |
| 5 | `tipo` | varchar(100) | YES | MUL |  |  |  |
| 6 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |

**Índices**

- `PRIMARY` (único): `id`
- `idx_autor` (no único): `autor`
- `idx_clasificacion` (no único): `clasificacion`
- `idx_tipo` (no único): `tipo`

## `jisparking`.`group_details`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 10

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `group_detail` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`honoraries`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 242

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `honorary_reason_id` | int | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `foreigner_id` | int | YES |  |  |  |  |
| 5 | `bank_id` | int | YES |  |  |  |  |
| 6 | `schedule_id` | int | YES |  |  |  |  |
| 7 | `region_id` | int | YES |  |  |  |  |
| 8 | `commune_id` | int | YES |  |  |  |  |
| 9 | `account_type_id` | int | YES |  |  |  |  |
| 10 | `requested_by` | varchar(255) | YES |  |  |  |  |
| 11 | `status_id` | int | YES |  |  |  |  |
| 12 | `employee_to_replace` | varchar(255) | YES |  |  |  |  |
| 13 | `replacement_employee_rut` | varchar(255) | NO |  |  |  |  |
| 14 | `replacement_employee_full_name` | varchar(255) | YES |  |  |  |  |
| 15 | `address` | varchar(255) | YES |  |  |  |  |
| 16 | `account_number` | varchar(255) | YES |  |  |  |  |
| 17 | `start_date` | date | YES |  |  |  |  |
| 18 | `end_date` | date | YES |  |  |  |  |
| 19 | `email` | varchar(255) | YES |  |  |  |  |
| 20 | `amount` | int | YES |  |  |  |  |
| 21 | `observation` | varchar(255) | YES |  |  |  |  |
| 22 | `period` | varchar(255) | YES |  |  |  |  |
| 23 | `added_date` | datetime | YES |  |  |  |  |
| 24 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`honorary_reasons`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 3

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `honorary_reason` | varchar(255) | YES |  |  |  |  |
| 3 | `added_date` | varchar(255) | YES |  |  |  |  |
| 4 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`hr_settings`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `percentage_honorary_bill` | varchar(255) | YES |  |  |  |  |
| 3 | `apigetaway_token` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`interships`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 16

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `intern` | varchar(255) | YES |  |  |  |  |
| 4 | `added_date` | datetime | YES |  |  |  |  |
| 5 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`interships_answers`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 418

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `intership_id` | int | YES |  |  |  |  |
| 3 | `question_id` | int | YES |  |  |  |  |
| 4 | `answer_id` | int | YES |  |  |  |  |
| 5 | `observation` | varchar(255) | YES |  |  |  |  |
| 6 | `support` | varchar(255) | YES |  |  |  |  |
| 7 | `added_date` | datetime | YES |  |  |  |  |
| 8 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`kardex_values`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 76

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `product_id` | int | YES |  |  |  |  |
| 3 | `qty` | int | YES |  |  |  |  |
| 4 | `cost` | int | YES |  |  |  |  |
| 5 | `added_date` | datetime | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |
| 6 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`maintenance_data`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 3

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `maintenance_id` | varchar(255) | YES |  |  |  |  |
| 3 | `file_number` | varchar(255) | YES |  |  |  |  |
| 4 | `support` | varchar(255) | YES |  |  |  |  |
| 5 | `added_date` | varchar(255) | YES |  |  |  |  |
| 6 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`maintenances`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `maintenance_date` | date | YES |  |  |  |  |
| 4 | `added_date` | datetime | YES |  |  |  |  |
| 5 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`movements`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 11

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `supplier_id` | varchar(150) | YES |  |  |  |  |
| 3 | `branch_office_id` | int | NO |  |  |  |  |
| 4 | `type_id` | int | NO |  |  |  |  |
| 5 | `document_number` | varchar(150) | YES |  | `0` |  |  |
| 6 | `status_id` | int | NO |  |  |  |  |
| 7 | `support` | varchar(150) | YES |  |  |  |  |
| 8 | `added_date` | datetime | NO |  |  |  |  |
| 9 | `updated_date` | datetime | NO |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`movements_products`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 11

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `product_id` | int | NO |  |  |  |  |
| 3 | `movement_id` | int | NO |  |  |  |  |
| 4 | `cost` | int | YES |  | `0` |  |  |
| 5 | `qty` | int | NO |  |  |  |  |
| 6 | `added_date` | datetime | NO |  |  |  |  |
| 7 | `updated_date` | datetime | NO |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`patents`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 227

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `semester` | int | YES |  |  |  |  |
| 4 | `year` | int | YES |  |  |  |  |
| 5 | `support` | varchar(255) | YES |  |  |  |  |
| 6 | `added_date` | datetime | YES |  |  |  |  |
| 7 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`ppto_mes_distribucion`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 529

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  |  |  |
| 2 | `Sucursal` | varchar(255) | YES |  |  |  |  |
| 3 | `Ppto` | float | YES |  |  |  |  |
| 4 | `Periodo` | varchar(255) | NO | PRI |  |  |  |

**Índices**

- `PRIMARY` (único): `id`, `Periodo`

## `jisparking`.`preventive_maintenance_items`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 43

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `section_id` | int | NO | MUL |  |  |  |
| 3 | `item_key` | varchar(100) | NO |  |  |  | Clave única del item (ej: external_cleaning) |
| 4 | `item_name` | varchar(255) | NO |  |  |  | Nombre del item en español |
| 5 | `item_order` | int | YES |  | `0` |  | Orden de visualización |
| 6 | `is_active` | tinyint(1) | YES |  | `1` |  |  |
| 7 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |
| 8 | `updated_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |

**Claves foráneas (salientes)**

| Columna | Referencia | Constraint |
| --- | --- | --- |
| `section_id` | `preventive_maintenance_sections`.`id` | `fk_maintenance_item_section` |

**Índices**

- `PRIMARY` (único): `id`
- `idx_section_id` (no único): `section_id`
- `unique_section_item_key` (único): `section_id`, `item_key`

## `jisparking`.`preventive_maintenance_responses`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 559

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `preventive_maintenance_id` | int | NO | MUL |  |  |  |
| 3 | `item_id` | int | NO | MUL |  |  |  |
| 4 | `response_value` | int | YES | MUL |  |  | 1=Sí, 2=No, 3=N/A |
| 5 | `observation` | text | YES |  |  |  |  |
| 6 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |
| 7 | `updated_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |

**Claves foráneas (salientes)**

| Columna | Referencia | Constraint |
| --- | --- | --- |
| `item_id` | `preventive_maintenance_items`.`id` | `fk_response_item` |
| `preventive_maintenance_id` | `preventive_maintenances`.`id` | `fk_response_maintenance` |

**Índices**

- `PRIMARY` (único): `id`
- `idx_item_id` (no único): `item_id`
- `idx_preventive_maintenance_id` (no único): `preventive_maintenance_id`
- `idx_response_maintenance_item` (no único): `preventive_maintenance_id`, `item_id`
- `idx_response_value` (no único): `response_value`
- `unique_maintenance_item` (único): `preventive_maintenance_id`, `item_id`

## `jisparking`.`preventive_maintenance_sections`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 7

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `section_number` | int | NO | UNI |  |  |  |
| 3 | `section_name` | varchar(255) | NO |  |  |  |  |
| 4 | `section_name_es` | varchar(255) | NO |  |  |  | Nombre en español para referencia |
| 5 | `is_active` | tinyint(1) | YES |  | `1` |  |  |
| 6 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |
| 7 | `updated_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |

**Índices**

- `PRIMARY` (único): `id`
- `unique_section_number` (único): `section_number`

## `jisparking`.`preventive_maintenances`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 9

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | NO | MUL |  |  |  |
| 3 | `address` | varchar(255) | YES |  |  |  |  |
| 4 | `maintenance_date` | date | NO | MUL |  |  |  |
| 5 | `technician_name` | varchar(255) | NO |  |  |  |  |
| 6 | `manager_name` | varchar(255) | NO |  |  |  |  |
| 7 | `detected_failures` | text | YES |  |  |  |  |
| 8 | `corrective_actions` | text | YES |  |  |  |  |
| 9 | `technician_signature` | text | YES |  |  |  | Base64 encoded signature image |
| 10 | `manager_signature` | text | YES |  |  |  | Base64 encoded signature image |
| 11 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |
| 12 | `updated_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |

**Claves foráneas (salientes)**

| Columna | Referencia | Constraint |
| --- | --- | --- |
| `branch_office_id` | `branch_offices`.`id` | `fk_preventive_maintenance_branch_office` |

**Índices**

- `PRIMARY` (único): `id`
- `idx_branch_office_id` (no único): `branch_office_id`
- `idx_maintenance_date` (no único): `maintenance_date`
- `idx_maintenance_date_desc` (no único): `maintenance_date`

## `jisparking`.`principals`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 12

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `principal` | varchar(255) | YES |  |  |  |  |
| 3 | `added_date` | varchar(255) | YES |  |  |  |  |
| 4 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`product_categories`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 5

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | bigint unsigned | NO | PRI |  | auto_increment |  |
| 2 | `product_category` | varchar(255) | NO |  |  |  |  |
| 3 | `accounting_account` | varchar(150) | NO |  |  |  |  |
| 4 | `added_date` | datetime | YES |  |  |  |  |
| 5 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`products`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 114

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | bigint unsigned | NO | PRI |  | auto_increment |  |
| 2 | `product_category_id` | bigint unsigned | NO | MUL |  |  |  |
| 3 | `visibility_id` | int | NO |  | `0` |  |  |
| 4 | `code` | varchar(255) | NO |  |  |  |  |
| 5 | `description` | longtext | NO |  |  |  |  |
| 6 | `min_stock` | int | NO |  |  |  |  |
| 7 | `max_stock` | int | NO |  |  |  |  |
| 8 | `measure` | varchar(150) | NO |  |  |  |  |
| 9 | `balance` | int | NO |  |  |  |  |
| 10 | `added_date` | datetime | YES |  |  |  |  |
| 11 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`
- `products_product_category_id_foreign` (no único): `product_category_id`

## `jisparking`.`reference_types`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 54

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `code` | varchar(32) | NO | UNI |  |  | Código enviado en referenced_type_id |
| 3 | `description` | varchar(512) | NO |  |  |  |  |
| 4 | `sort_order` | int | NO |  | `0` |  |  |

**Índices**

- `PRIMARY` (único): `id`
- `uk_reference_types_code` (único): `code`

## `jisparking`.`regions`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 16

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  |  |  |  |
| 2 | `region` | varchar(255) | YES |  |  |  |  |
| 3 | `simplefactura_region_code` | int | YES |  |  |  |  |
| 4 | `region_remuneration_code` | varchar(255) | YES |  |  |  |  |
| 5 | `added_date` | datetime | YES |  |  |  |  |
| 6 | `updated_date` | datetime | YES |  |  |  |  |

## `jisparking`.`remunerations`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 7649

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `accounting_account` | int | YES |  |  |  |  |
| 4 | `amount` | varchar(255) | YES |  |  |  |  |
| 5 | `period` | varchar(255) | YES |  |  |  |  |
| 6 | `added_date` | datetime | YES |  |  |  |  |
| 7 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`rols`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 8

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `rol` | varchar(255) | YES |  |  |  |  |
| 3 | `added_date` | datetime | YES |  |  |  |  |
| 4 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`samestores`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 6776

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id_samestore` | int | NO | PRI |  | auto_increment |  |
| 2 | `id_branch_office` | int | YES |  |  |  |  |
| 3 | `month` | varchar(255) | YES |  |  |  |  |
| 4 | `year` | varchar(255) | YES |  |  |  |  |
| 5 | `value` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id_samestore`

## `jisparking`.`segments`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 9

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `segment` | varchar(255) | YES |  |  |  |  |
| 3 | `added_date` | varchar(255) | YES |  |  |  |  |
| 4 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`settings`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  |  |  |
| 2 | `honorary_open_period` | varchar(255) | YES |  |  |  |  |
| 3 | `honorary_close_period` | varchar(255) | YES |  |  |  |  |
| 4 | `capitulation_open_period` | varchar(255) | YES |  |  |  |  |
| 5 | `capitulation_close_period` | varchar(255) | YES |  |  |  |  |
| 6 | `dropbox_token` | text | YES |  |  |  |  |
| 7 | `facebook_token` | text | YES |  |  |  |  |
| 8 | `simplefactura_token` | text | YES |  |  |  |  |
| 9 | `caf_limit` | int | YES |  |  |  |  |
| 10 | `percentage_honorary_bill` | varchar(255) | YES |  |  |  |  |
| 11 | `apigetaway_token` | text | YES |  |  |  |  |
| 12 | `added_date` | datetime | YES |  |  |  |  |
| 13 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`sinister_types`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `sinister_type` | varchar(255) | YES |  |  |  |  |
| 3 | `added_date` | datetime | YES |  |  |  |  |
| 4 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`sinisters`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 5

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `sinister_type_id` | int | YES |  |  |  |  |
| 4 | `protected_area_id` | int | YES |  |  |  |  |
| 5 | `registered_event_id` | int | YES |  |  |  |  |
| 6 | `notified_security_id` | int | YES |  |  |  |  |
| 7 | `denounced_authorities_id` | int | YES |  |  |  |  |
| 8 | `status_id` | int | YES |  |  |  |  |
| 9 | `sinister_date` | date | YES |  |  |  |  |
| 10 | `client_rut` | varchar(255) | YES |  |  |  |  |
| 11 | `client_name` | varchar(255) | YES |  |  |  |  |
| 12 | `client_last_name` | varchar(255) | YES |  |  |  |  |
| 13 | `client_email` | varchar(255) | YES |  |  |  |  |
| 14 | `client_phone` | varchar(255) | YES |  |  |  |  |
| 15 | `brand` | varchar(255) | YES |  |  |  |  |
| 16 | `model` | varchar(255) | YES |  |  |  |  |
| 17 | `year` | varchar(255) | YES |  |  |  |  |
| 18 | `patent` | varchar(255) | YES |  |  |  |  |
| 19 | `color` | varchar(255) | YES |  |  |  |  |
| 20 | `description` | text | YES |  |  |  |  |
| 21 | `support` | text | YES |  |  |  |  |
| 22 | `added_date` | datetime | YES |  |  |  |  |
| 23 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`sinisters_reviews`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 4

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `sinister_id` | int | YES |  |  |  |  |
| 3 | `sinister_step_type_id` | int | YES |  |  |  |  |
| 4 | `review_description` | text | YES |  |  |  |  |
| 5 | `support` | text | YES |  |  |  |  |
| 6 | `added_date` | datetime | YES |  |  |  |  |
| 7 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`statuses`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 17

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `status` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`suppliers`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 822

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `rut` | varchar(255) | YES |  |  |  |  |
| 3 | `supplier` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`survey_question_options`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 29
- **Comentario tabla:** Tabla de opciones para preguntas de tipo select, radio y checkbox

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `question_id` | int | NO | MUL |  |  | ID de la pregunta |
| 3 | `option_text` | varchar(255) | NO |  |  |  | Texto de la opción |
| 4 | `order` | int | NO |  | `0` |  | Orden de la opción en la pregunta |
| 5 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |
| 6 | `updated_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |

**Claves foráneas (salientes)**

| Columna | Referencia | Constraint |
| --- | --- | --- |
| `question_id` | `survey_questions`.`id` | `fk_survey_options_question` |

**Índices**

- `PRIMARY` (único): `id`
- `idx_question_id` (no único): `question_id`

## `jisparking`.`survey_questions`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 12
- **Comentario tabla:** Tabla de preguntas de encuestas

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `survey_id` | int | NO | MUL |  |  | ID de la encuesta |
| 3 | `question` | text | NO |  |  |  | Texto de la pregunta |
| 4 | `field_type` | enum('text','select','radio','checkbox') | NO |  | `text` |  | Tipo de campo: text, select, radio, checkbox |
| 5 | `order` | int | NO |  | `0` |  | Orden de la pregunta en la encuesta |
| 6 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |
| 7 | `updated_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |

**Claves foráneas (salientes)**

| Columna | Referencia | Constraint |
| --- | --- | --- |
| `survey_id` | `surveys`.`id` | `fk_survey_questions_survey` |

**Índices**

- `PRIMARY` (único): `id`
- `idx_survey_id` (no único): `survey_id`

## `jisparking`.`survey_response_answers`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 8449
- **Comentario tabla:** Tabla de respuestas anónimas de encuestas

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `survey_id` | int | NO | MUL |  |  | ID de la encuesta |
| 3 | `question_id` | int | NO | MUL |  |  | ID de la pregunta |
| 4 | `answer_text` | text | YES |  |  |  | Respuesta de texto (para input text) |
| 5 | `option_id` | int | YES | MUL |  |  | ID de la opción seleccionada (para select, radio, checkbox) |
| 6 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |

**Claves foráneas (salientes)**

| Columna | Referencia | Constraint |
| --- | --- | --- |
| `option_id` | `survey_question_options`.`id` | `fk_response_answers_option` |
| `question_id` | `survey_questions`.`id` | `fk_response_answers_question` |
| `survey_id` | `surveys`.`id` | `fk_response_answers_survey` |

**Índices**

- `PRIMARY` (único): `id`
- `idx_option_id` (no único): `option_id`
- `idx_question_id` (no único): `question_id`
- `idx_survey_id` (no único): `survey_id`

## `jisparking`.`surveys`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 0
- **Comentario tabla:** Tabla de encuestas

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `title` | varchar(255) | NO |  |  |  | Título de la encuesta |
| 3 | `description` | text | YES |  |  |  | Descripción de la encuesta |
| 4 | `created_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |
| 5 | `updated_at` | timestamp | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED on update CURRENT_TIMESTAMP |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`taxes`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 7

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `period` | varchar(255) | YES |  |  |  |  |
| 3 | `support` | varchar(255) | YES |  |  |  |  |
| 4 | `added_date` | datetime | YES |  |  |  |  |
| 5 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`tp_Ppto_operacional`

- **Tipo:** BASE TABLE
- **Motor:** MyISAM
- **Filas estimadas (information_schema):** 88169

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `Sucursal` | varchar(255) | YES |  |  |  |  |
| 3 | `Cuentas` | varchar(255) | YES |  |  |  |  |
| 4 | `Version` | varchar(255) | YES |  |  |  |  |
| 5 | `Dias` | date | YES |  |  |  |  |
| 6 | `Operacional` | bigint | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`tp_customer_intranet1`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 3821

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `customer_id` | varchar(255) | YES |  |  |  |  |
| 2 | `rut` | varchar(255) | YES |  |  |  |  |
| 3 | `phone` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`transbank_cashier_special`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 4

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `code` | int | YES |  |  |  |  |
| 3 | `cashier_id` | int | YES |  |  |  |  |
| 4 | `branch_office_id` | int | YES |  |  |  |  |
| 5 | `cashier` | varchar(255) | YES |  |  |  |  |
| 6 | `Identificación Local` | varchar(255) | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`transbank_statements`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 10471

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `original_date` | varchar(255) | YES |  |  |  |  |
| 4 | `code` | varchar(255) | YES |  |  |  |  |
| 5 | `branch_office_name` | varchar(255) | YES |  |  |  |  |
| 6 | `sale_type` | varchar(255) | YES |  |  |  |  |
| 7 | `payment_type` | varchar(255) | YES |  |  |  |  |
| 8 | `card_number` | varchar(255) | YES |  |  |  |  |
| 9 | `sale_description` | varchar(255) | YES |  |  |  |  |
| 10 | `amount` | varchar(255) | YES |  |  |  |  |
| 11 | `value_1` | varchar(255) | YES |  |  |  |  |
| 12 | `value_2` | varchar(255) | YES |  |  |  |  |
| 13 | `value_3` | varchar(255) | YES |  |  |  |  |
| 14 | `value_4` | varchar(255) | YES |  |  |  |  |
| 15 | `added_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`users`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 40

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `rol_id` | int | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `rut` | varchar(255) | YES |  |  |  |  |
| 5 | `full_name` | varchar(255) | YES |  |  |  |  |
| 6 | `email` | varchar(255) | YES |  |  |  |  |
| 7 | `phone` | varchar(255) | YES |  |  |  |  |
| 8 | `hashed_password` | varchar(255) | YES |  |  |  |  |
| 9 | `added_date` | datetime | YES |  |  |  |  |
| 10 | `updated_date` | datetime | YES |  |  |  |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`whatsapp_notification_recipients`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 54

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO | PRI |  | auto_increment |  |
| 2 | `nombre` | varchar(100) | NO |  |  |  |  |
| 3 | `telefono` | varchar(20) | NO |  |  |  |  |
| 4 | `activo` | tinyint(1) | YES |  | `1` |  |  |
| 5 | `tipo` | varchar(50) | NO |  |  |  |  |
| 6 | `creado_en` | datetime | YES |  | `CURRENT_TIMESTAMP` | DEFAULT_GENERATED |  |

**Índices**

- `PRIMARY` (único): `id`

## `jisparking`.`whatsapp_templates`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 6

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `title` | varchar(255) | YES |  |  |  |  |
| 3 | `template` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`zones`

- **Tipo:** BASE TABLE
- **Motor:** InnoDB
- **Filas estimadas (information_schema):** 4

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | varchar(255) | YES |  |  |  |  |
| 2 | `zone` | varchar(255) | YES |  |  |  |  |
| 3 | `added_date` | varchar(255) | YES |  |  |  |  |
| 4 | `updated_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`INGRESOS_MES_EERR`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `branch_office_id` | int | YES |  |  |  |  |
| 2 | `ingresos` | decimal(33,0) | NO |  | `0` |  |  |
| 3 | `subscribers_total` | decimal(32,0) | NO |  | `0` |  |  |
| 4 | `year` | int | YES |  |  |  |  |
| 5 | `month` | int | YES |  |  |  |  |

## `jisparking`.`QRY_BRANCH_OFFICES`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 3 | `address` | varchar(255) | YES |  |  |  |  |
| 4 | `region` | varchar(255) | YES |  |  |  |  |
| 5 | `commune` | varchar(255) | YES |  |  |  |  |
| 6 | `zone` | varchar(255) | YES |  |  |  |  |
| 7 | `segment` | varchar(255) | YES |  |  |  |  |
| 8 | `principal` | varchar(255) | YES |  |  |  |  |
| 9 | `dte_code` | varchar(255) | YES |  |  |  |  |
| 10 | `principal_supervisor` | varchar(255) | YES |  |  |  |  |
| 11 | `responsable` | varchar(255) | YES |  |  |  |  |
| 12 | `visibility_id` | int | YES |  |  |  |  |
| 13 | `status_id` | int | YES |  |  |  |  |
| 14 | `full_name` | varchar(255) | YES |  |  |  |  |
| 15 | `person_who_receives` | varchar(255) | YES |  |  |  |  |
| 16 | `rut_who_receives` | varchar(255) | YES |  |  |  |  |
| 17 | `phone_who_receives` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`QRY_CABECERA_TRANSACCIONES`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `date` | date | NO |  |  |  |  |
| 2 | `branch_office_id` | int | NO |  |  |  |  |
| 3 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 4 | `segment` | varchar(255) | YES |  |  |  |  |
| 5 | `principal` | varchar(255) | YES |  |  |  |  |
| 6 | `zone` | varchar(255) | YES |  |  |  |  |
| 7 | `responsable` | varchar(255) | YES |  |  |  |  |
| 8 | `cash_amount` | double | YES |  |  |  |  |
| 9 | `card_amount` | double | YES |  |  |  |  |
| 10 | `subscribers` | decimal(32,0) | YES |  |  |  |  |
| 11 | `ticket_number` | decimal(32,0) | YES |  |  |  |  |

## `jisparking`.`QRY_DATOS_TRANSBANK`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | YES |  | `0` |  |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 4 | `codigo_comercio` | varchar(255) | YES |  |  |  |  |
| 5 | `dte_code` | varchar(255) | YES |  |  |  |  |
| 6 | `address` | varchar(255) | YES |  |  |  |  |
| 7 | `region` | varchar(255) | YES |  |  |  |  |
| 8 | `commune` | varchar(255) | YES |  |  |  |  |
| 9 | `status` | varchar(6) | YES |  |  |  |  |
| 10 | `responsable` | varchar(255) | YES |  |  |  |  |
| 11 | `status_id` | int | YES |  |  |  |  |

## `jisparking`.`QRY_DTES`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `folio` | int | YES |  |  |  |  |
| 3 | `dte_version_id` | int | YES |  |  |  |  |
| 4 | `branch_office_id` | int | YES |  |  |  |  |
| 5 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 6 | `segment` | varchar(255) | YES |  |  |  |  |
| 7 | `principal` | varchar(255) | YES |  |  |  |  |
| 8 | `zone` | varchar(255) | YES |  |  |  |  |
| 9 | `responsable` | varchar(255) | YES |  |  |  |  |
| 10 | `dte_type_id` | int | YES |  |  |  |  |
| 11 | `expense_type_id` | int | YES |  |  |  |  |
| 12 | `expense_type` | varchar(255) | YES |  |  |  |  |
| 13 | `status_id` | int | YES |  |  |  |  |
| 14 | `status` | varchar(255) | YES |  |  |  |  |
| 15 | `rut` | varchar(255) | YES |  |  |  |  |
| 16 | `customer` | varchar(255) | YES |  |  |  |  |
| 17 | `neto` | decimal(32,0) | YES |  |  |  |  |
| 18 | `iva` | decimal(32,0) | YES |  |  |  |  |
| 19 | `bruto` | decimal(32,0) | YES |  |  |  |  |
| 20 | `date` | varchar(10) | YES |  |  |  |  |
| 21 | `period` | varchar(255) | YES |  |  |  |  |
| 22 | `comment` | varchar(255) | YES |  |  |  |  |
| 23 | `payment_date` | varchar(255) | YES |  |  |  |  |
| 24 | `payment_comment` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`QRY_DTES_EMITIDOS`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `folio` | int | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 5 | `segment` | varchar(255) | YES |  |  |  |  |
| 6 | `principal` | varchar(255) | YES |  |  |  |  |
| 7 | `zone` | varchar(255) | YES |  |  |  |  |
| 8 | `responsable` | varchar(255) | YES |  |  |  |  |
| 9 | `dte_type_id` | int | YES |  |  |  |  |
| 10 | `expense_type_id` | int | YES |  |  |  |  |
| 11 | `expense_type` | varchar(255) | YES |  |  |  |  |
| 12 | `status_id` | int | YES |  |  |  |  |
| 13 | `status` | varchar(255) | YES |  |  |  |  |
| 14 | `rut` | varchar(255) | YES |  |  |  |  |
| 15 | `customer` | varchar(255) | YES |  |  |  |  |
| 16 | `neto` | decimal(32,0) | YES |  |  |  |  |
| 17 | `iva` | decimal(32,0) | YES |  |  |  |  |
| 18 | `bruto` | decimal(32,0) | YES |  |  |  |  |
| 19 | `date` | varchar(10) | YES |  |  |  |  |
| 20 | `period` | varchar(255) | YES |  |  |  |  |
| 21 | `comment` | varchar(255) | YES |  |  |  |  |
| 22 | `payment_date` | varchar(255) | YES |  |  |  |  |
| 23 | `payment_comment` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`QRY_DTES_RECIBIDOS`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `folio` | int | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 5 | `responsable` | varchar(255) | YES |  |  |  |  |
| 6 | `dte_type_id` | int | YES |  |  |  |  |
| 7 | `expense_type_id` | int | YES |  |  |  |  |
| 8 | `expense_type` | varchar(255) | YES |  |  |  |  |
| 9 | `status_id` | int | YES |  |  |  |  |
| 10 | `status` | varchar(255) | YES |  |  |  |  |
| 11 | `rut` | varchar(255) | YES |  |  |  |  |
| 12 | `supplier` | varchar(255) | YES |  |  |  |  |
| 13 | `neto` | decimal(32,0) | YES |  |  |  |  |
| 14 | `iva` | decimal(32,0) | YES |  |  |  |  |
| 15 | `bruto` | decimal(32,0) | YES |  |  |  |  |
| 16 | `date` | varchar(10) | YES |  |  |  |  |
| 17 | `period` | varchar(255) | YES |  |  |  |  |
| 18 | `comment` | varchar(255) | YES |  |  |  |  |
| 19 | `payment_date` | varchar(255) | YES |  |  |  |  |
| 20 | `payment_comment` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`QRY_EERR`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `eerr_id` | int | NO |  | `0` |  |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 4 | `responsable` | varchar(255) | YES |  |  |  |  |
| 5 | `principal` | varchar(255) | YES |  |  |  |  |
| 6 | `segment` | varchar(255) | YES |  |  |  |  |
| 7 | `zone` | varchar(255) | YES |  |  |  |  |
| 8 | `accounting_account` | text | YES |  |  |  |  |
| 9 | `expense_type` | varchar(255) | YES |  |  |  |  |
| 10 | `group_detail` | varchar(255) | YES |  |  |  |  |
| 11 | `type` | int | YES |  |  |  |  |
| 12 | `period` | varchar(255) | YES |  |  |  |  |
| 13 | `amount` | decimal(32,0) | YES |  |  |  |  |
| 14 | `positive_negative_id` | int | YES |  |  |  |  |

## `jisparking`.`QRY_EERR_CONSOLIDADO`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `branch_office_id` | int | YES |  |  |  |  |
| 2 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 3 | `responsable` | varchar(255) | YES |  |  |  |  |
| 4 | `expense_type` | varchar(255) | YES |  |  |  |  |
| 5 | `group_detail` | varchar(255) | YES |  |  |  |  |
| 6 | `period` | varchar(255) | YES |  |  |  |  |
| 7 | `año` | varchar(4) | YES |  |  |  |  |
| 8 | `mes_numero` | varchar(2) | YES |  |  |  |  |
| 9 | `mes` | varchar(15) | YES |  |  |  |  |
| 10 | `amount` | decimal(32,0) | YES |  |  |  |  |

## `jisparking`.`QRY_IND_SSS`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id_branch_office` | int | YES |  |  |  |  |
| 2 | `clave` | double | YES |  |  |  |  |
| 3 | `ind` | double | YES |  |  |  |  |

## `jisparking`.`QRY_PPTO_DIA`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `date` | date | YES |  |  |  |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `ppto` | float | YES |  |  |  |  |

## `jisparking`.`QRY_REPORTE_ABONADOS`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `dte_id` | int | NO |  | `0` |  |  |
| 2 | `Fecha_Emision` | date | YES |  |  |  |  |
| 3 | `Fecha_Pago` | date | YES |  |  |  |  |
| 4 | `Dias_Cobro` | int | YES |  |  |  |  |
| 5 | `RUT_Cliente` | varchar(50) | YES |  |  |  |  |
| 6 | `Nombre_Cliente` | varchar(150) | YES |  |  |  |  |
| 7 | `folio` | int | YES |  |  |  |  |
| 8 | `branch_office_id` | int | YES |  |  |  |  |
| 9 | `Sucursal` | varchar(255) | YES |  |  |  |  |
| 10 | `Supervisor` | varchar(255) | YES |  |  |  |  |
| 11 | `Estado` | varchar(100) | YES |  |  |  |  |
| 12 | `Monto_Total` | bigint | YES |  |  |  |  |
| 13 | `Monto_Neto` | bigint | YES |  | `0` |  |  |
| 14 | `Impuesto` | bigint | YES |  | `0` |  |  |
| 15 | `Link_Pago` | varchar(2) | NO |  | `` |  |  |
| 16 | `Periodo_Contable` | varchar(50) | YES |  |  |  |  |

## `jisparking`.`QRY_REPORTE_DEPOSITOS`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `Fecha_Recaudacion` | date | YES |  |  |  |  |
| 2 | `Fecha_Deposito` | date | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `Sucursal` | varchar(255) | YES |  |  |  |  |
| 5 | `Supervisor` | varchar(255) | YES |  |  |  |  |
| 6 | `Monto_Recaudado` | decimal(32,0) | YES |  |  |  |  |
| 7 | `Monto_Depositado` | decimal(32,0) | NO |  | `0` |  |  |
| 8 | `Diferencia` | decimal(33,0) | YES |  |  |  |  |
| 9 | `Dias_Latencia` | int | YES |  |  |  |  |
| 10 | `Estado_Deposito` | varchar(25) | NO |  | `` |  |  |
| 11 | `Estado_Diferencia` | varchar(14) | NO |  | `` |  |  |
| 12 | `Prioridad` | varchar(5) | NO |  | `` |  |  |
| 13 | `Respaldo` | text | YES |  |  |  |  |

## `jisparking`.`QRY_latest_sales_update`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `cashier` | varchar(255) | YES |  |  |  |  |
| 3 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 4 | `responsable` | varchar(255) | YES |  |  |  |  |
| 5 | `rustdesk` | varchar(255) | YES |  |  |  |  |
| 6 | `anydesk` | varchar(255) | YES |  |  |  |  |
| 7 | `last_updated_date` | datetime | YES |  |  |  |  |

## `jisparking`.`VW_DepositosAsociados`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `collection_id` | int | YES |  |  |  |  |
| 2 | `fecha_deposito` | datetime | YES |  |  |  |  |
| 3 | `monto_depositado` | decimal(32,0) | YES |  |  |  |  |
| 4 | `support` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`VW_HONORARIES`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `honorary_reason_id` | int | YES |  |  |  |  |
| 3 | `honorary_reason` | varchar(16) | NO |  | `` |  |  |
| 4 | `branch_office_id` | int | YES |  |  |  |  |
| 5 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 6 | `responsable` | varchar(255) | YES |  |  |  |  |
| 7 | `foreigner_id` | int | YES |  |  |  |  |
| 8 | `foreigner_type` | varchar(15) | NO |  | `` |  |  |
| 9 | `bank_id` | int | YES |  |  |  |  |
| 10 | `bank` | varchar(255) | YES |  |  |  |  |
| 11 | `schedule_id` | int | YES |  |  |  |  |
| 12 | `schedule_type` | varchar(15) | NO |  | `` |  |  |
| 13 | `region` | varchar(255) | YES |  |  |  |  |
| 14 | `commune` | varchar(255) | YES |  |  |  |  |
| 15 | `account_type_id` | int | YES |  |  |  |  |
| 16 | `requested_by` | varchar(255) | YES |  |  |  |  |
| 17 | `status_id` | int | YES |  |  |  |  |
| 18 | `status` | varchar(255) | YES |  |  |  |  |
| 19 | `employee_to_replace` | varchar(255) | YES |  |  |  |  |
| 20 | `replacement_employee_rut` | varchar(255) | NO |  |  |  |  |
| 21 | `replacement_employee_full_name` | varchar(255) | YES |  |  |  |  |
| 22 | `address` | varchar(255) | YES |  |  |  |  |
| 23 | `account_number` | varchar(255) | YES |  |  |  |  |
| 24 | `start_date` | date | YES |  |  |  |  |
| 25 | `end_date` | date | YES |  |  |  |  |
| 26 | `email` | varchar(255) | YES |  |  |  |  |
| 27 | `amount` | int | YES |  |  |  |  |
| 28 | `observation` | varchar(255) | YES |  |  |  |  |
| 29 | `added_date` | datetime | YES |  |  |  |  |
| 30 | `period` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`VW_RecaudacionDiaria`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `collection_id` | int | NO |  | `0` |  |  |
| 2 | `fecha_recaudacion` | date | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `monto_recaudado` | int | YES |  |  |  |  |

## `jisparking`.`VW_rendiciones_detallada`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `rendicion_id` | int | NO |  | `0` |  |  |
| 2 | `tipo_documento_id` | int | YES |  |  |  |  |
| 3 | `tipo_rendicion_id` | int | YES |  |  |  |  |
| 4 | `sucursal` | varchar(255) | YES |  |  |  |  |
| 5 | `zona` | varchar(255) | YES |  |  |  |  |
| 6 | `segmento` | varchar(255) | YES |  |  |  |  |
| 7 | `responsable_sucursal` | varchar(255) | YES |  |  |  |  |
| 8 | `tipo_gasto` | varchar(255) | YES |  |  |  |  |
| 9 | `grupo_detalle_gasto` | varchar(255) | YES |  |  |  |  |
| 10 | `estado_rendicion` | varchar(255) | YES |  |  |  |  |
| 11 | `fecha_documento` | date | YES |  |  |  |  |
| 12 | `numero_documento` | varchar(255) | YES |  |  |  |  |
| 13 | `informante` | varchar(255) | YES |  |  |  |  |
| 14 | `rut_proveedor` | varchar(255) | YES |  |  |  |  |
| 15 | `descripcion` | varchar(255) | YES |  |  |  |  |
| 16 | `monto` | int | YES |  |  |  |  |
| 17 | `soporte` | varchar(255) | YES |  |  |  |  |
| 18 | `fecha_pago` | varchar(255) | YES |  |  |  |  |
| 19 | `numero_pago` | varchar(255) | YES |  |  |  |  |
| 20 | `soporte_pago` | varchar(255) | YES |  |  |  |  |
| 21 | `periodo` | varchar(255) | YES |  |  |  |  |
| 22 | `fecha_registro` | datetime | YES |  |  |  |  |

## `jisparking`.`comparation_pending_deposits_bank_statements`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | YES |  | `0` |  |  |
| 2 | `deposit_id` | int | NO |  | `0` |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 5 | `payment_type_id` | int | YES |  |  |  |  |
| 6 | `collection_id` | int | YES |  | `0` |  |  |
| 7 | `status_id` | int | YES |  |  |  |  |
| 8 | `payment_number` | varchar(255) | YES |  |  |  |  |
| 9 | `collection_amount` | int | YES |  |  |  |  |
| 10 | `deposited_amount` | int | YES |  |  |  |  |
| 11 | `collection_date` | date | YES |  |  |  |  |
| 12 | `bank_statement_type_id` | int | YES |  |  |  |  |
| 13 | `bank_statement_rut` | varchar(255) | YES |  |  |  |  |
| 14 | `bank_statement_amount` | int | YES |  |  |  |  |
| 15 | `deposit_number` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`comparation_pending_deposits_bank_statements2`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | YES |  | `0` |  |  |
| 2 | `deposit_id` | int | NO |  | `0` |  |  |
| 3 | `branch_office_id` | int | YES |  | `0` |  |  |
| 4 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 5 | `payment_type_id` | int | YES |  |  |  |  |
| 6 | `status_id` | int | YES |  |  |  |  |
| 7 | `payment_number` | varchar(255) | YES |  |  |  |  |
| 8 | `collection_amount` | int | YES |  |  |  |  |
| 9 | `deposited_amount` | int | YES |  |  |  |  |
| 10 | `collection_date` | date | YES |  |  |  |  |
| 11 | `bank_statement_type_id` | int | YES |  |  |  |  |
| 12 | `bank_statement_rut` | varchar(255) | YES |  |  |  |  |
| 13 | `bank_statement_amount` | int | YES |  |  |  |  |
| 14 | `deposit_number` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`comparation_pending_dtes_bank_statements`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `rut` | varchar(255) | YES |  |  |  |  |
| 3 | `customer` | varchar(255) | YES |  |  |  |  |
| 4 | `folio` | int | YES |  |  |  |  |
| 5 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 6 | `amount` | int | YES |  |  |  |  |
| 7 | `bank_statement_type_id` | int | YES |  |  |  |  |
| 8 | `bank_statement_period` | varchar(255) | YES |  |  |  |  |
| 9 | `bank_statement_amount` | int | YES |  |  |  |  |
| 10 | `bank_statement_rut` | varchar(255) | YES |  |  |  |  |
| 11 | `deposit_number` | varchar(255) | YES |  |  |  |  |
| 12 | `deposit_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`comparation_pending_dtes_bank_statements2`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `rut` | varchar(255) | YES |  |  |  |  |
| 3 | `customer` | varchar(255) | YES |  |  |  |  |
| 4 | `folio` | int | YES |  |  |  |  |
| 5 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 6 | `amount` | int | YES |  |  |  |  |
| 7 | `bank_statement_type_id` | int | YES |  |  |  |  |
| 8 | `bank_statement_period` | varchar(255) | YES |  |  |  |  |
| 9 | `bank_statement_amount` | int | YES |  |  |  |  |
| 10 | `bank_statement_rut` | varchar(255) | YES |  |  |  |  |
| 11 | `deposit_number` | varchar(255) | YES |  |  |  |  |
| 12 | `deposit_date` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`cpdbs`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | YES |  | `0` |  |  |
| 2 | `deposit_id` | int | NO |  | `0` |  |  |
| 3 | `branch_office_id` | int | YES |  | `0` |  |  |
| 4 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 5 | `payment_type_id` | int | YES |  |  |  |  |
| 6 | `status_id` | int | YES |  |  |  |  |
| 7 | `payment_number` | varchar(255) | YES |  |  |  |  |
| 8 | `collection_amount` | int | YES |  |  |  |  |
| 9 | `deposited_amount` | int | YES |  |  |  |  |
| 10 | `collection_date` | date | YES |  |  |  |  |
| 11 | `bank_statement_type_id` | int | YES |  |  |  |  |
| 12 | `bank_statement_rut` | varchar(255) | YES |  |  |  |  |
| 13 | `bank_statement_amount` | int | YES |  |  |  |  |
| 14 | `deposit_number` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`folio_report`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `available_folios` | int | YES |  |  |  |  |
| 2 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 3 | `cashier` | varchar(255) | YES |  |  |  |  |
| 4 | `rustdesk` | varchar(255) | YES |  |  |  |  |
| 5 | `anydesk` | varchar(255) | YES |  |  |  |  |
| 6 | `id` | int | NO |  | `0` |  |  |

## `jisparking`.`folio_requests`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `cashier` | varchar(255) | YES |  |  |  |  |
| 2 | `id` | int | NO |  | `0` |  |  |

## `jisparking`.`latest_update_cashiers`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `cashier` | varchar(255) | YES |  |  |  |  |
| 3 | `rustdesk` | varchar(255) | YES |  |  |  |  |
| 4 | `anydesk` | varchar(255) | YES |  |  |  |  |
| 5 | `last_updated_date` | datetime | YES |  |  |  |  |

## `jisparking`.`total_accepted_capitulations`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | YES |  |  |  |  |
| 2 | `full_name` | varchar(255) | YES |  |  |  |  |
| 3 | `rut` | varchar(255) | YES |  |  |  |  |
| 4 | `amount` | decimal(32,0) | YES |  |  |  |  |

## `jisparking`.`total_all_collection_per_supervisor`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | bigint unsigned | NO |  | `0` |  |  |
| 2 | `principal_supervisor` | varchar(255) | YES |  |  |  |  |
| 3 | `total` | decimal(34,0) | NO |  | `0` |  |  |

## `jisparking`.`total_all_collections`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `total` | decimal(34,0) | NO |  | `0` |  |  |

## `jisparking`.`total_collections`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `added_date` | date | YES |  |  |  |  |
| 3 | `branch_office_id` | int | YES |  |  |  |  |
| 4 | `cashier_id` | int | YES |  |  |  |  |
| 5 | `cash_total` | decimal(32,0) | YES |  |  |  |  |
| 6 | `card_total` | decimal(32,0) | YES |  |  |  |  |
| 7 | `total_tickets` | int | YES |  |  |  |  |
| 8 | `updated_date` | datetime | YES |  |  |  |  |

## `jisparking`.`total_credit_notes`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `added_date` | varchar(10) | YES |  |  |  |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `cashier_id` | int | YES |  |  |  |  |
| 4 | `total` | decimal(32,0) | YES |  |  |  |  |
| 5 | `total_tickets` | bigint | NO |  | `0` |  |  |

## `jisparking`.`total_deposits_collections`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `faltante` | decimal(33,0) | YES |  |  |  |  |
| 2 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 3 | `total_cash` | decimal(32,0) | YES |  |  |  |  |
| 4 | `added_day` | date | YES |  |  |  |  |
| 5 | `branch_office_id` | int | YES |  |  |  |  |

## `jisparking`.`total_detail_collections`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `added_date` | datetime | YES |  |  |  |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `cashier_id` | int | YES |  |  |  |  |
| 4 | `cash_total` | decimal(32,0) | YES |  |  |  |  |
| 5 | `card_total` | decimal(32,0) | YES |  |  |  |  |
| 6 | `total_tickets` | bigint | NO |  | `0` |  |  |

## `jisparking`.`total_dtes`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `added_date` | datetime | YES |  |  |  |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `cashier_id` | int | YES |  |  |  |  |
| 4 | `cash_total` | decimal(32,0) | YES |  |  |  |  |
| 5 | `card_total` | decimal(32,0) | YES |  |  |  |  |
| 6 | `total_tickets` | bigint | NO |  | `0` |  |  |

## `jisparking`.`total_dtes_to_be_sent`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `quantity` | bigint | NO |  | `0` |  |  |
| 3 | `period` | varchar(7) | YES |  |  |  |  |

## `jisparking`.`total_folios_per_cashier`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | NO |  | `0` |  |  |
| 2 | `branch_office` | varchar(255) | YES |  |  |  |  |
| 3 | `available_folios` | int | YES |  |  |  |  |
| 4 | `cashier` | varchar(255) | YES |  |  |  |  |
| 5 | `anydesk` | varchar(255) | YES |  |  |  |  |
| 6 | `rustdesk` | varchar(255) | YES |  |  |  |  |

## `jisparking`.`total_general_collections`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | YES |  |  |  |  |
| 2 | `added_date` | date | YES |  |  |  |  |
| 3 | `updated_date` | datetime | YES |  |  |  |  |
| 4 | `branch_office_id` | int | YES |  |  |  |  |
| 5 | `cashier_id` | int | YES |  |  |  |  |
| 6 | `cash_total_collections` | decimal(54,0) | YES |  |  |  |  |
| 7 | `card_total_collections` | decimal(54,0) | YES |  |  |  |  |
| 8 | `total_credit_notes` | decimal(65,0) | YES |  |  |  |  |
| 9 | `total` | decimal(65,0) | YES |  |  |  |  |
| 10 | `total_tickets_collections` | int | YES |  |  |  |  |
| 11 | `total_tickets_credit_notes` | decimal(42,0) | YES |  |  |  |  |
| 12 | `total_tickets` | decimal(43,0) | YES |  |  |  |  |

## `jisparking`.`transbank_total`

- **Tipo:** VIEW
- **Comentario tabla:** VIEW

| # | Columna | Tipo | Nulo | Key | Default | Extra | Comentario |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | `id` | int | YES |  |  |  |  |
| 2 | `branch_office_id` | int | YES |  |  |  |  |
| 3 | `total` | double | YES |  |  |  |  |
| 4 | `total_tickets` | bigint | NO |  | `0` |  |  |
| 5 | `added_date` | varchar(255) | YES |  |  |  |  |

---

## Uso para el agente

1. Priorizar **vistas** ya usadas por reportes (ej. `QRY_*`) para lecturas estables.
2. Tablas base: solo lectura con SQL acotado y columnas explícitas.
3. Cruzar con este mapa las **preguntas de negocio** → nuevas tools (inventario / resumen / ranking / tendencia).
