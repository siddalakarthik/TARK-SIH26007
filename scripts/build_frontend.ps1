$ErrorActionPreference = 'Stop'
Push-Location "$PSScriptRoot\..\frontend"
try {
    # Prefer the already-installed, lockfile-pinned tools.  This lets the local
    # dashboard build in a restricted/offline development environment instead
    # of waiting for a registry check before every rebuild.
    $tsc = Join-Path $PWD 'node_modules\typescript\bin\tsc'
    $vite = Join-Path $PWD 'node_modules\vite\bin\vite.js'
    if ((Test-Path -LiteralPath $tsc) -and (Test-Path -LiteralPath $vite)) {
        & node $tsc -b
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        & node $vite build
    } else {
        pnpm install --frozen-lockfile
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
        pnpm build
    }
} finally {
    Pop-Location
}
