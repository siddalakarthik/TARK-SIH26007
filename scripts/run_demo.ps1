param(
    [ValidateRange(1024, 65535)][int]$Port = 8000,
    [switch]$CheckOnly,
    [string]$DemoPythonPath = ''
)

# Local observation demo only. This script does not discover or open hardware.
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python = Join-Path $projectRoot '.venv\Scripts\python.exe'
$overrides = @{
    TARK_ENV = 'development'
    TARK_AUTH_MODE = 'public_demo'
    TARK_ACCESS_TOKEN = ''
    TARK_CORS_ORIGINS = ''
    TARK_DATABASE_PATH = (Join-Path $projectRoot 'data\database\r2_demo.db')
    TARK_GNSS_DEVICE_PATH = ''
    TARK_RADAR_PORT = ''
    TARK_ESP32_DEVICE_PATH = ''
    TARK_ESP32_BAUD = ''
    TARK_CAMERA_DEVICE_PATH = ''
    TARK_IMU_I2C_ADDRESS = ''
    TARK_THERMAL_I2C_ADDRESS = ''
    TARK_ENABLE_BROWSER_CAMERA = 'false'
    TARK_GNSS_RAW_LOG_ENABLED = 'false'
    TARK_GNSS_RAW_LOG_PATH = ''
    TARK_ROUTE_PROVIDER_URL = ''
    TARK_REVERSE_GEOCODER_URL = ''
}
if ($DemoPythonPath) {
    $dependencyPath = (Resolve-Path -LiteralPath $DemoPythonPath).Path
    if (-not (Test-Path -LiteralPath $dependencyPath -PathType Container)) {
        throw 'DemoPythonPath must point to an existing, operator-reviewed dependency directory.'
    }
    $overrides['PYTHONPATH'] = if ($env:PYTHONPATH) { "$dependencyPath;$env:PYTHONPATH" } else { $dependencyPath }
}
$savedEnvironment = @{}
foreach ($name in $overrides.Keys) {
    $savedEnvironment[$name] = [Environment]::GetEnvironmentVariable($name, 'Process')
}

Push-Location $projectRoot
try {
    if (-not (Test-Path -LiteralPath $python)) {
        throw 'Project .venv is missing. Follow docs/R2_WEBSITE_RUN.md; no packages are installed automatically.'
    }
    if (-not (Test-Path -LiteralPath (Join-Path $projectRoot 'frontend\dist\index.html'))) {
        throw 'Compiled frontend is missing. Build it with .\scripts\build_frontend.ps1 first.'
    }
    $configuration = Get-Content -LiteralPath (Join-Path $projectRoot 'config\phase1.json') -Raw | ConvertFrom-Json
    if ($configuration.mode -ne 'simulation' -or $configuration.hard_cap_mps -ne 0) {
        throw 'Demo requires config/phase1.json mode=simulation and hard_cap_mps=0. Configuration was not changed.'
    }
    foreach ($name in $overrides.Keys) {
        [Environment]::SetEnvironmentVariable($name, $overrides[$name], 'Process')
    }
    & $python -c 'import fastapi, uvicorn, cbor2; assert cbor2.loads(cbor2.dumps({"demo": True})) == {"demo": True}'
    if ($LASTEXITCODE -ne 0) {
        throw 'Dependency preflight failed. Read the error above; this script does not bypass Windows application-control policy.'
    }
    & $python -c 'import socket, sys; s=socket.socket(); s.bind(("127.0.0.1", int(sys.argv[1]))); s.close()' $Port
    if ($LASTEXITCODE -ne 0) {
        throw "Cannot bind 127.0.0.1:$Port. Reuse or stop the known service yourself; no process was terminated."
    }
    if ($CheckOnly) {
        Write-Host "Demo preflight passed for http://localhost:$Port. No server started."
        return
    }
    Write-Host "TARK local demo: http://localhost:$Port" -ForegroundColor Cyan
    Write-Host 'Simulation only. Hardware adapters disabled. Traction DISABLED_PHASE_1.' -ForegroundColor Yellow
    Write-Host 'Press Ctrl+C to stop. This is not a public or LAN deployment.'
    & $python -m uvicorn app.main:app --app-dir (Join-Path $projectRoot 'backend') --host 127.0.0.1 --port $Port
    if ($LASTEXITCODE -ne 0) { throw "Server exited with code $LASTEXITCODE." }
} finally {
    foreach ($name in $savedEnvironment.Keys) {
        if ($null -eq $savedEnvironment[$name]) {
            # PowerShell/.NET versions differ on null-to-string conversion;
            # remove an originally absent variable instead of retaining "".
            Remove-Item -LiteralPath "Env:$name" -ErrorAction SilentlyContinue
        } else {
            [Environment]::SetEnvironmentVariable($name, $savedEnvironment[$name], 'Process')
        }
    }
    Pop-Location
}
