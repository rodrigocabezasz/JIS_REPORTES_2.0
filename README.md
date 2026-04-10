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

## Arrancar en desarrollo (orden recomendado)

1. **Túneles SSH** (si MySQL/Ollama están en el VPS): `.\scripts\start_ssh_tunnels.ps1`, o usa **`.\scripts\run_dev.ps1`** (túneles + API en ventana nueva + Streamlit).
2. **API FastAPI** del agente en `http://127.0.0.1:8080` (por defecto): `.\scripts\run_agent_service.ps1`.
3. **Streamlit** (otra terminal): `.\scripts\run_streamlit.ps1`. Si `run_dev` ya abrió túneles: `.\scripts\run_streamlit.ps1 -SkipTunnel`.

Si Streamlit muestra **10061**, el paso 2 no está corriendo o el puerto no coincide.

**`AGENT_URL`:** debe ser la URL base del servicio (ej. `http://127.0.0.1:8080`), igual que `HOST`/`PORT` del `run_service.py`. Definilo en el `.env` del toolkit.

**Agente `jis-reports`:** en Streamlit el streaming va por **mensajes**, no por **tokens** (`stream_tokens=False`), para que Ollama no vuelque JSON de herramientas en la conversación. Otros agentes pueden seguir con tokens.

Instrucciones resumidas en español: [instrucciones.txt](instrucciones.txt). Frases listas para probar el chat: [docs/PREGUNTAS_CHATBOT_REVISADAS.md](docs/PREGUNTAS_CHATBOT_REVISADAS.md).

## Arrancar el agente (manual alternativo)

Desde la **raíz** del workspace (con `.venv` activo) los scripts anteriores son la vía preferida. Equivalente manual:

```powershell
cd framework\agent-service-toolkit
python src\run_service.py
```

En otra terminal:

```powershell
streamlit run framework\agent-service-toolkit\src\streamlit_app.py
```

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
