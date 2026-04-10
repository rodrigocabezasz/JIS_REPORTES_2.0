#Requires -Version 5.1

<#

.SYNOPSIS

  Desarrollo local: túneles SSH (si .env) + API en nueva ventana + Streamlit en esta.



.DESCRIPTION

  WinError 10061 en Streamlit = nada escuchando en :8080. Hay que tener el FastAPI del agente

  en marcha; los túneles solo sirven para Ollama (:11434) y MySQL (:3307), no abren el 8080.

#>



function Test-LocalPortOpen {

    param([int]$Port)

    $c = New-Object System.Net.Sockets.TcpClient

    try {

        $iar = $c.BeginConnect("127.0.0.1", $Port, $null, $null)

        $ok = $iar.AsyncWaitHandle.WaitOne(400, $false)

        if (-not $ok) { return $false }

        $c.EndConnect($iar)

        return $true

    }

    catch { return $false }

    finally { if ($c) { $c.Close() } }

}



$Root = Resolve-Path (Join-Path $PSScriptRoot "..")

& (Join-Path $Root "scripts\start_ssh_tunnels.ps1")



$toolkit = Join-Path $Root "framework\agent-service-toolkit"

if (-not (Test-Path -LiteralPath $toolkit)) {

    Write-Error "No existe: $toolkit"

    exit 1

}



if (Test-LocalPortOpen -Port 8080) {

    Write-Host "[run_dev] Ya hay algo en :8080; no abro otra ventana del API."

}

else {

    $inner = @"

Set-Location '$toolkit'

Write-Host '=== JIS Agent API (FastAPI) http://127.0.0.1:8080 ===' -ForegroundColor Green

Write-Host 'Cierra esta ventana para detener el API.' -ForegroundColor Yellow

python src\run_service.py

"@

    $exe = if (Get-Command pwsh.exe -ErrorAction SilentlyContinue) { "pwsh.exe" } else { "powershell.exe" }

    Start-Process -FilePath $exe -ArgumentList @("-NoExit", "-Command", $inner) | Out-Null

    Write-Host "[run_dev] API iniciado en nueva ventana. Esperando puerto 8080..."

    $ready = $false

    for ($i = 0; $i -lt 60; $i++) {

        if (Test-LocalPortOpen -Port 8080) {

            $ready = $true

            break

        }

        Start-Sleep -Seconds 1

    }

    if (-not $ready) {

        Write-Warning "El API no respondió en 8080 tras 60 s. Revisa la otra ventana (errores Python / .env)."

    }

}



& (Join-Path $Root "scripts\run_streamlit.ps1") -SkipTunnel

