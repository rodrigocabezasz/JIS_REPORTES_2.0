# Arranca la UI Streamlit del toolkit (ruta completa al .py)
$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$app = Join-Path $Root "framework\agent-service-toolkit\src\streamlit_app.py"
Write-Host "Streamlit: $app"
Set-Location $Root
streamlit run $app
