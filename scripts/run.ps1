$ErrorActionPreference='Stop'
$root=(Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$python=Join-Path $root '.venv\Scripts\python.exe'
$dist=Join-Path $root 'frontend\dist\index.html'

try {
    if(-not (Test-Path -LiteralPath $python)) {
        throw "Project Python environment missing: $python`nCreate it with: py -3 -m venv .venv`nThen install: .\.venv\Scripts\python.exe -m pip install -e '.[dev]'"
    }
    & $python -c "import fastapi, uvicorn" 
    if($LASTEXITCODE -ne 0) { throw "Backend dependencies are missing. Run .\.venv\Scripts\python.exe -m pip install -e '.[dev]'." }
    if(-not (Test-Path -LiteralPath $dist)) {
        throw "Compiled frontend is missing: $dist`nRun: .\scripts\build_frontend.ps1"
    }
    $listenerLine=netstat -ano -p tcp | Where-Object { $_ -match '^\s*TCP\s+\S+:8000\s+\S+\s+LISTENING\s+(\d+)\s*$' } | Select-Object -First 1
    if($listenerLine -match '^\s*TCP\s+\S+:8000\s+\S+\s+LISTENING\s+(\d+)\s*$') {
        $ownerPid=[int]$Matches[1]
        $process=Get-Process -Id $ownerPid -ErrorAction SilentlyContinue
        $processName=if($process){$process.ProcessName}else{'unknown'}
        throw "Port 8000 is already in use.`nPID: $ownerPid`nPROCESS: $processName`nStop or reuse that process; this script will not terminate it."
    }
    Write-Host 'TARK SERVER RUNNING' -ForegroundColor Green
    Write-Host 'http://localhost:8000' -ForegroundColor Cyan
    Write-Host 'Simulation mode; traction remains DISABLED_PHASE_1.' -ForegroundColor Yellow
    & $python -m uvicorn app.main:app --app-dir (Join-Path $root 'backend') --host 0.0.0.0 --port 8000
    if($LASTEXITCODE -ne 0) { throw "Uvicorn exited with code $LASTEXITCODE." }
} catch {
    Write-Error "TARK STARTUP FAILED`n$($_.Exception.Message)"
    exit 1
}
