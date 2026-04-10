# Crea .venv e instala requirements.txt (Python 3.11-3.13)

# Uso:  cd C:\JIS_REPORTES_2.0 ; .\scripts\create_venv.ps1

#

# Si solo tienes Python 3.14: instala 3.12 desde https://www.python.org/downloads/



$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")

Set-Location $Root



$venvPath = Join-Path $Root ".venv"

if (Test-Path $venvPath) {

    Write-Host "Ya existe .venv - eliminalo primero si quieres recrearlo: Remove-Item -Recurse -Force .venv"

}



$created = $false

if (Get-Command py -ErrorAction SilentlyContinue) {

    foreach ($ver in @("3.13", "3.12", "3.11")) {

        & py "-$ver" -c "import sys; raise SystemExit(0 if (3,11)<=sys.version_info[:2]<=(3,13) else 1)" 2>$null

        if ($LASTEXITCODE -eq 0) {

            Write-Host "Creando venv con: py -$ver"

            & py "-$ver" -m venv $venvPath

            $created = $true

            break

        }

    }

}



if (-not $created) {

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {

        Write-Error "Instala Python 3.12 (64-bit) y vuelve a ejecutar este script."

    }

    & python -c "import sys; raise SystemExit(0 if (3,11)<=sys.version_info[:2]<=(3,13) else 1)" 2>$null

    if ($LASTEXITCODE -ne 0) {

        Write-Error "Tu python no es 3.11-3.13. Instala 3.12 y usa el launcher: py -3.12"

    }

    Write-Host "Creando venv con: python -m venv"

    & python -m venv $venvPath

    $created = $true

}



$venvPy = Join-Path $venvPath "Scripts\python.exe"

if (-not (Test-Path $venvPy)) {

    Write-Error "No se creo $venvPy"

}



& $venvPy -m pip install -U pip wheel setuptools

& $venvPy -m pip install -r (Join-Path $Root "requirements.txt")



Write-Host ""

Write-Host "Activa el entorno:"

Write-Host "  .\.venv\Scripts\Activate.ps1"

Write-Host "Verificar:  python scripts\verify_connectivity.py"

