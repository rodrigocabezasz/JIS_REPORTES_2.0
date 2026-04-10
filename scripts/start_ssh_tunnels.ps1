#Requires -Version 5.1

<#

.SYNOPSIS

  Abre túneles SSH (Ollama + MySQL) en segundo plano si SSH_TUNNEL_AUTO=1 en .env de la raíz del repo.



.DESCRIPTION

  Equivale a:

    ssh -N -L 11434:localhost:11434 -L 3307:localhost:3306 -p 22 usuario@servidor

  Requiere OpenSSH Client (ssh.exe) y acceso por clave o ssh-agent si no usas contraseña interactiva.



  Variables en .env (raíz):

    SSH_TUNNEL_AUTO=1

    SSH_TUNNEL_TARGET=jislab@jisparking.from-vt.com   (o JISLAB_SSH_USER + JISLAB_SSH_HOST)

    JISLAB_SSH_PORT=22

    JISLAB_SSH_KEY_PATH=...   (opcional)

    SSH_LOCAL_OLLAMA_PORT=11434

    SSH_LOCAL_MYSQL_PORT=3307

    SSH_REMOTE_OLLAMA_HOST=localhost

    SSH_REMOTE_OLLAMA_PORT=11434

    SSH_REMOTE_MYSQL_HOST=localhost

    SSH_REMOTE_MYSQL_PORT=3306

#>



param(

    [switch]$Force

)



function Test-LocalPortOpen {

    param([int]$Port)

    $c = New-Object System.Net.Sockets.TcpClient

    try {

        $iar = $c.BeginConnect("127.0.0.1", $Port, $null, $null)

        $ok = $iar.AsyncWaitHandle.WaitOne(600, $false)

        if (-not $ok) { return $false }

        $c.EndConnect($iar)

        return $true

    }

    catch {

        return $false

    }

    finally {

        if ($c) { $c.Close() }

    }

}



function Import-DotEnvFile {

    param([string]$Path)

    if (-not (Test-Path -LiteralPath $Path)) { return }

    Get-Content -LiteralPath $Path -Encoding UTF8 | ForEach-Object {

        $line = $_.Trim()

        if ($line -match '^\s*#' -or $line -eq "") { return }

        if ($line -match '^([A-Za-z_][A-Za-z0-9_]*)=(.*)$') {

            $name = $matches[1]

            $val = $matches[2].Trim()

            if (($val.StartsWith('"') -and $val.EndsWith('"')) -or ($val.StartsWith("'") -and $val.EndsWith("'"))) {

                $val = $val.Substring(1, $val.Length - 2)

            }

            Set-Item -Path "Env:$name" -Value $val

        }

    }

}



$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")

$envFile = Join-Path $RepoRoot ".env"

Import-DotEnvFile -Path $envFile



$autoRaw = $env:SSH_TUNNEL_AUTO

if (-not $autoRaw) { $autoRaw = "" }

$auto = $autoRaw.ToLowerInvariant()

if ($auto -notin @("1", "true", "yes", "on")) {

    Write-Host "[túneles] SSH_TUNNEL_AUTO no está activado en .env; omite inicio automático."

    return

}



$target = $env:SSH_TUNNEL_TARGET

if (-not $target) {

    $u = $env:JISLAB_SSH_USER

    $h = $env:JISLAB_SSH_HOST

    if ($u -and $h) { $target = "${u}@${h}" }

}

if (-not $target) {

    Write-Warning "[túneles] Activa SSH_TUNNEL_AUTO pero falta SSH_TUNNEL_TARGET o JISLAB_SSH_USER + JISLAB_SSH_HOST."

    return

}



$sshPort = if ($env:JISLAB_SSH_PORT) { $env:JISLAB_SSH_PORT } else { "22" }

$lo = if ($env:SSH_LOCAL_OLLAMA_PORT) { [int]$env:SSH_LOCAL_OLLAMA_PORT } else { 11434 }

$lm = if ($env:SSH_LOCAL_MYSQL_PORT) { [int]$env:SSH_LOCAL_MYSQL_PORT } else { 3307 }

$rhO = if ($env:SSH_REMOTE_OLLAMA_HOST) { $env:SSH_REMOTE_OLLAMA_HOST } else { "localhost" }

$rpO = if ($env:SSH_REMOTE_OLLAMA_PORT) { $env:SSH_REMOTE_OLLAMA_PORT } else { "11434" }

$rhM = if ($env:SSH_REMOTE_MYSQL_HOST) { $env:SSH_REMOTE_MYSQL_HOST } else { "localhost" }

$rpM = if ($env:SSH_REMOTE_MYSQL_PORT) { $env:SSH_REMOTE_MYSQL_PORT } else { "3306" }



$forwardOllama = "${lo}:${rhO}:${rpO}"

$forwardMysql = "${lm}:${rhM}:${rpM}"



if (-not $Force -and (Test-LocalPortOpen -Port $lo) -and (Test-LocalPortOpen -Port $lm)) {

    Write-Host "[túneles] Puertos $lo y $lm ya responden en 127.0.0.1; no inicio otro ssh (usa -Force para forzar)."

    return

}



$sshCmd = Get-Command ssh.exe -ErrorAction SilentlyContinue

$sshExe = if ($sshCmd) { $sshCmd.Source } else { $null }

if (-not $sshExe) {

    Write-Error "[túneles] No se encontró ssh.exe. Instala OpenSSH Client: Configuración > Aplicaciones > Características opcionales."

    exit 1

}



$argList = [System.Collections.ArrayList]@(

    "-N",

    "-o", "ServerAliveInterval=30",

    "-o", "ServerAliveCountMax=4",

    "-o", "ExitOnForwardFailure=yes",

    "-p", $sshPort,

    "-L", $forwardOllama,

    "-L", $forwardMysql

)



$keyPath = $env:JISLAB_SSH_KEY_PATH

if ($keyPath) {

    if (-not (Test-Path -LiteralPath $keyPath)) {

        Write-Warning "[túneles] JISLAB_SSH_KEY_PATH no existe: $keyPath"

    }

    else {

        [void]$argList.Insert(0, $keyPath)

        [void]$argList.Insert(0, "-i")

    }

}



[void]$argList.Add($target)



Write-Host "[túneles] Iniciando ssh hacia $target ..."

Write-Host "[túneles]   -L $forwardOllama"

Write-Host "[túneles]   -L $forwardMysql"



Start-Process -FilePath $sshExe -ArgumentList ($argList.ToArray()) -WindowStyle Minimized



Start-Sleep -Seconds 2

$okO = Test-LocalPortOpen -Port $lo

$okM = Test-LocalPortOpen -Port $lm

if ($okO) { Write-Host "[túneles] OK Ollama en 127.0.0.1:$lo (OLLAMA_BASE_URL debe apuntar aquí)." }

else { Write-Warning "[túneles] Puerto $lo aún cerrado: revisa clave SSH, host o que el servicio Ollama exista en el remoto." }

if ($okM) { Write-Host "[túneles] OK MySQL en 127.0.0.1:$lm (DB_HOST=127.0.0.1 DB_PORT=$lm)." }

else { Write-Warning "[túneles] Puerto $lm aún cerrado: revisa MySQL en $rhM`:$rpM en el servidor." }

