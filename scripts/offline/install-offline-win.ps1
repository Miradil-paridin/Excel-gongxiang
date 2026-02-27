param(
    [string]$TargetDir = ""
)

$ErrorActionPreference = "Stop"

$bundleDir = (Resolve-Path $PSScriptRoot).Path
if ([string]::IsNullOrWhiteSpace($TargetDir)) {
    $TargetDir = Join-Path $bundleDir "excel-gongxiang"
}

Write-Host "[1/7] Verify bundle files"
$required = @(
    "$bundleDir\artifacts\source\project-src.tar.gz",
    "$bundleDir\artifacts\docker\onlyoffice-documentserver-7.4.0.tar",
    "$bundleDir\artifacts\frontend\frontend-node_modules.tar.gz"
)
foreach ($item in $required) {
    if (-not (Test-Path $item)) {
        throw "Missing required file: $item"
    }
}
if (-not (Test-Path "$bundleDir\artifacts\python-wheels")) {
    throw "Missing folder: $bundleDir\artifacts\python-wheels"
}

Write-Host "[2/7] Extract source -> $TargetDir"
if (-not (Test-Path $TargetDir)) {
    New-Item -ItemType Directory -Path $TargetDir | Out-Null
}
tar -xzf "$bundleDir\artifacts\source\project-src.tar.gz" -C $TargetDir

Write-Host "[3/7] Load Docker image (OnlyOffice)"
docker load -i "$bundleDir\artifacts\docker\onlyoffice-documentserver-7.4.0.tar"

Write-Host "[4/7] Setup Python venv and install backend deps offline"
Push-Location $TargetDir
try {
    python -m venv venv
    & "$TargetDir\venv\Scripts\python.exe" -m pip install --upgrade pip
    & "$TargetDir\venv\Scripts\pip.exe" install --no-index `
      --find-links "$bundleDir\artifacts\python-wheels" `
      -r "$TargetDir\backend\requirements.txt"
}
finally {
    Pop-Location
}

Write-Host "[5/7] Restore frontend dependencies"
tar -xzf "$bundleDir\artifacts\frontend\frontend-node_modules.tar.gz" -C "$TargetDir\frontend"

Write-Host "[6/7] Prepare env file"
if ((-not (Test-Path "$TargetDir\backend\.env")) -and (Test-Path "$TargetDir\backend\.env.example")) {
    Copy-Item "$TargetDir\backend\.env.example" "$TargetDir\backend\.env" -Force
}

Write-Host "[7/7] Done"
Write-Host "Next steps:"
Write-Host "  1) Start OnlyOffice:"
Write-Host "     cd `"$TargetDir\docker`""
Write-Host "     docker compose up -d"
Write-Host "  2) Start backend:"
Write-Host "     cd `"$TargetDir\backend`""
Write-Host "     ..\venv\Scripts\python manage.py migrate"
Write-Host "     ..\venv\Scripts\python manage.py runserver 0.0.0.0:8000"
Write-Host "  3) Start frontend (new terminal):"
Write-Host "     cd `"$TargetDir\frontend`""
Write-Host "     npm run dev -- --host 0.0.0.0 --port 3000"
