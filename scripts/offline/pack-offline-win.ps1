param(
    [string]$BundleDir = ""
)

$ErrorActionPreference = "Stop"

$root = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
if ([string]::IsNullOrWhiteSpace($BundleDir)) {
    $BundleDir = Join-Path $root "dist\offline-bundle-win-$timestamp"
}

Write-Host "[1/7] Prepare bundle directory: $BundleDir"
if (Test-Path $BundleDir) {
    Remove-Item -Recurse -Force $BundleDir
}
New-Item -ItemType Directory -Force -Path "$BundleDir\artifacts\source" | Out-Null
New-Item -ItemType Directory -Force -Path "$BundleDir\artifacts\python-wheels" | Out-Null
New-Item -ItemType Directory -Force -Path "$BundleDir\artifacts\frontend" | Out-Null
New-Item -ItemType Directory -Force -Path "$BundleDir\artifacts\docker" | Out-Null

Write-Host "[2/7] Archive project source"
Push-Location $root
try {
    tar -czf "$BundleDir\artifacts\source\project-src.tar.gz" `
      --exclude=".git" `
      --exclude="dist" `
      --exclude="venv" `
      --exclude="frontend/node_modules" `
      --exclude="backend/media" `
      --exclude="docker/onlyoffice/data" `
      --exclude="docker/onlyoffice/logs" `
      .
}
finally {
    Pop-Location
}

Write-Host "[3/7] Download backend wheels"
$venvPython = Join-Path $root "venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "Python venv not found, creating venv at $root\venv ..."
    $pyCmd = Get-Command py -ErrorAction SilentlyContinue
    $pythonCmd = Get-Command python -ErrorAction SilentlyContinue

    if ($pyCmd) {
        # Prefer Python 3.11 (best wheel compatibility for current requirements)
        & py -3.11 -m venv "$root\venv" 2>$null
        if (-not (Test-Path $venvPython)) {
            & py -3.10 -m venv "$root\venv" 2>$null
        }
        if (-not (Test-Path $venvPython)) {
            & py -3.9 -m venv "$root\venv" 2>$null
        }
        if (-not (Test-Path $venvPython)) {
            & py -3 -m venv "$root\venv"
        }
    }
    elseif ($pythonCmd) {
        & python -m venv "$root\venv"
    }
    else {
        throw "Python not found in PATH. Please install Python 3.9+ and retry."
    }

    if (-not (Test-Path $venvPython)) {
        throw "Failed to create venv at $root\venv. Please create it manually and retry."
    }
}
& $venvPython -m pip install --upgrade pip
# Strictly use prebuilt wheels to avoid source-build failures (e.g. Pillow on unsupported Python versions)
& $venvPython -m pip download --only-binary=:all: `
  -r "$root\backend\requirements.txt" `
  -d "$BundleDir\artifacts\python-wheels"

Write-Host "[4/7] Pack frontend dependencies (node_modules)"
$frontendDir = Join-Path $root "frontend"
if (-not (Test-Path "$frontendDir\node_modules")) {
    Push-Location $frontendDir
    try {
        npm install
    }
    finally {
        Pop-Location
    }
}
Push-Location $frontendDir
try {
    tar -czf "$BundleDir\artifacts\frontend\frontend-node_modules.tar.gz" `
      node_modules package.json package-lock.json
}
finally {
    Pop-Location
}

Write-Host "[5/7] Export Docker image (OnlyOffice)"
docker image inspect onlyoffice/documentserver:7.4.0 | Out-Null
docker save -o "$BundleDir\artifacts\docker\onlyoffice-documentserver-7.4.0.tar" `
  onlyoffice/documentserver:7.4.0

Write-Host "[6/7] Copy installer and docs"
Copy-Item "$PSScriptRoot\install-offline-win.ps1" "$BundleDir\install-offline-win.ps1" -Force
@"
Offline Bundle (Windows) Usage
==============================

1) Copy this bundle directory to the target Windows machine.
2) On target machine (PowerShell as normal user):
   .\install-offline-win.ps1
3) Then start services manually:
   - Backend:
     cd .\excel-gongxiang\backend
     ..\venv\Scripts\python manage.py migrate
     ..\venv\Scripts\python manage.py runserver 0.0.0.0:8000
   - Frontend (new terminal):
     cd .\excel-gongxiang\frontend
     npm run dev -- --host 0.0.0.0 --port 3000
   - OnlyOffice:
     cd .\excel-gongxiang\docker
     docker compose up -d
"@ | Set-Content -Path "$BundleDir\README-OFFLINE-WINDOWS.txt" -Encoding UTF8

Write-Host "[7/7] Generate checksums"
$checksumFile = "$BundleDir\SHA256SUMS.txt"
if (Test-Path $checksumFile) {
    Remove-Item $checksumFile -Force
}
Get-ChildItem -Path $BundleDir -Recurse -File | ForEach-Object {
    if ($_.FullName -ne $checksumFile) {
        $hash = Get-FileHash -Algorithm SHA256 -Path $_.FullName
        "{0}  {1}" -f $hash.Hash.ToLower(), ($_.FullName.Substring($BundleDir.Length + 1).Replace('\','/')) `
          | Add-Content -Path $checksumFile -Encoding UTF8
    }
}

Write-Host "DONE: $BundleDir"
