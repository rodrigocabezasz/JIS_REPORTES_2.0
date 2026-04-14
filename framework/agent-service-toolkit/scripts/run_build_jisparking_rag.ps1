# Construye el indice RAG (Chroma + embeddings Ollama).
# Uso (PowerShell): cd framework\agent-service-toolkit; .\scripts\run_build_jisparking_rag.ps1
$ErrorActionPreference = "Stop"
$ToolkitRoot = Split-Path $PSScriptRoot
Set-Location $ToolkitRoot

$venvPy = Join-Path $ToolkitRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
    Write-Host "Creando .venv en $ToolkitRoot ..."
    python -m venv .venv
    if (-not (Test-Path $venvPy)) {
        throw "No se pudo crear .venv. Probá: py -3.12 -m venv .venv"
    }
}

Write-Host "Instalando dependencias del toolkit (primera vez puede tardar)..."
& $venvPy -m pip install -q --upgrade pip
& $venvPy -m pip install -q -e .

Write-Host @"
Generando Chroma. Requisitos:
  - Ollama en ejecucion (app Windows en bandeja, o 'ollama serve').
  - Modelo: ollama pull nomic-embed-text   (o el definido en OLLAMA_EMBED_MODEL)
  - Si Ollama esta en otra PC: OLLAMA_BASE_URL en .env del toolkit (misma URL que el agente).
"@
& $venvPy (Join-Path $ToolkitRoot "scripts\build_jisparking_rag.py")
