$ErrorActionPreference = 'Stop'
Push-Location "$PSScriptRoot\..\frontend"
try {
    $vitest = Join-Path (Get-Location) 'node_modules\.bin\vitest.cmd'
    if(-not (Test-Path -LiteralPath $vitest)) {
        throw "Frontend dependencies are missing. Run .\scripts\build_frontend.ps1 on a network-enabled development machine."
    }
    & $vitest run --environment jsdom
    if($LASTEXITCODE -ne 0){exit $LASTEXITCODE}
} finally {
    Pop-Location
}
