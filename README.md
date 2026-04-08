# JIS Reportes 2.0

Repositorio del producto **agentico** en paralelo a [jisreportes.com](https://jisreportes.com): LangGraph, FastAPI, Ollama (JISLAB) y MySQL del mismo VPS. No sustituye los repos actuales de producción.

**Repositorio:** [github.com/rodrigocabezasz/JIS_REPORTES_2.0](https://github.com/rodrigocabezasz/JIS_REPORTES_2.0)

## Repos de producción (referencia, no incluidos aquí)

- Backend: [jisreportes_back](https://github.com/rodrigocabezasz/jisreportes_back)
- Frontend: [jisreportes_front](https://github.com/rodrigocabezasz/jisreportes_front)

Para revisar SQL o endpoints del sistema actual, clona esos repos aparte o ábrelos en otro workspace de Cursor.

## Requisitos

- **Python 3.11, 3.12 o 3.13** (el framework upstream no soporta 3.14).
- Acceso a **Ollama** (LAN o túnel SSH) y **MySQL** (VPS o túnel).

## Entorno virtual

```powershell
cd C:\JIS_REPORTES_2.0
.\scripts\create_venv.ps1
.\.venv\Scripts\Activate.ps1
python scripts\verify_connectivity.py
```

## Variables de entorno

Plantilla: [.env.example](.env.example). Copia a `.env` (raíz) y a `framework/agent-service-toolkit/.env`. **No subas `.env` a Git.**

## Arrancar el agente (después del venv)

```powershell
cd framework\agent-service-toolkit
python src\run_service.py
```

Streamlit de demo: `streamlit run src\streamlit_app.py` (misma carpeta, otra terminal).

## Estructura

| Ruta | Contenido |
|------|-----------|
| `framework/agent-service-toolkit/` | Toolkit + extensiones JIS (`jis_tools`, `jis-reports`) |
| `backend_v2/` | Destino del servicio propio JIS 2.0 (en evolución) |
| `scripts/` | Utilidades (`verify_connectivity.py`, `create_venv.ps1`) |
| `artifacts/` | Salidas generadas (carpeta reservada) |
| `PLAN_DESARROLLO_JIS_2.0.md` | Plan maestro |

## Primer push a GitHub

```powershell
git init
git add .
git status
```

Comprueba que **no** entren `.env`, `.venv`, `checkpoints.db` ni secretos. Luego:

```powershell
git commit -m "Initial commit: JIS Reportes 2.0 workspace"
git branch -M main
git remote add origin https://github.com/rodrigocabezasz/JIS_REPORTES_2.0.git
git push -u origin main
```

## Licencia del framework

El código bajo `framework/agent-service-toolkit/` proviene del proyecto upstream (licencia MIT en ese paquete). Ver [framework/README.md](framework/README.md).
