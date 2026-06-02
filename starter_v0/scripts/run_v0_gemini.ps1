$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path $Python)) {
    $Python = "python"
}

Push-Location $Root
try {
    & $Python run_eval.py `
        --provider gemini `
        --version v0 `
        --suite base `
        --eval-cases data\eval_base.json
}
finally {
    Pop-Location
}
