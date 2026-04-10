# Arranca la UI Streamlit del toolkit (ruta completa al .py)

param(

    # Usar cuando run_dev.ps1 ya abrió túneles y el API en otra ventana

    [switch]$SkipTunnel

)



$Root = Resolve-Path (Join-Path $PSScriptRoot "..")

if (-not $SkipTunnel) {

    & (Join-Path $Root "scripts\start_ssh_tunnels.ps1")

}

$app = Join-Path $Root "framework\agent-service-toolkit\src\streamlit_app.py"

Write-Host "Streamlit: $app  (AGENT_URL debe ser http://127.0.0.1:8080 - el API debe estar en marcha)"

Set-Location $Root



$venvPy = Join-Path $Root ".venv\Scripts\python.exe"

if (Test-Path -LiteralPath $venvPy) {

    & $venvPy -m streamlit run $app

}

else {

    Write-Warning "No se encontro $venvPy - usa: py -3.12 -m venv .venv y pip install -r requirements.txt"

    python -m streamlit run $app

}

