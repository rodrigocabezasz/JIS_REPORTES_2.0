# Arranca el API FastAPI del agente (desde la carpeta del toolkit para que lea .env)

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")

& (Join-Path $Root "scripts\start_ssh_tunnels.ps1")

Set-Location (Join-Path $Root "framework\agent-service-toolkit")

Write-Host "Directorio: $(Get-Location)"

python src\run_service.py

