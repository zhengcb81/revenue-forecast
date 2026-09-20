# drive_card.ps1 - one-shot command driver for a single M-card attempt (M09-M12).
#
# Every unit below is a real command with a real argv; the raw exit code of each unit is
# appended to after/rc_ledger.txt as "<unit_id><TAB><rc>". Console output of each unit is
# preserved under after/console_<unit_id>_<CARD>.txt.
#
# Exit-code rule inside this driver:
#   * a unit that runs a native command records that command's $LASTEXITCODE;
#   * a unit made only of cmdlets records its own accumulated failure flag (0 = no cmdlet
#     reported an error and every comparison printed the expected verdict, 1 = otherwise).
#   $LASTEXITCODE is reset to $null before each unit so a stale value can never leak in.
#
# This file is byte-identical in all four attempts; it derives every path from its own
# location, so no non-ASCII path literal appears inside the script.
#
# Usage:
#   powershell -NoProfile -ExecutionPolicy Bypass -File <attempt>\scripts\drive_card.ps1 -Card M09

param(
    [Parameter(Mandatory = $true)][ValidateSet('M09', 'M10', 'M11', 'M12')][string]$Card
)

$ErrorActionPreference = 'Continue'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch { }

$scriptsDir = $PSScriptRoot
$attempt = Split-Path -Parent $scriptsDir
$cardDir = Split-Path -Parent $attempt
$runsDir = Split-Path -Parent $cardDir
$planRoot = Split-Path -Parent $runsDir
$planningDir = Split-Path -Parent $planRoot
$repoRoot = Split-Path -Parent $planningDir
$projectsRoot = Split-Path -Parent $repoRoot
$companyWiki = Join-Path $projectsRoot 'company-wiki'

$venv = Join-Path $attempt 'iso\venv'
$py = Join-Path $venv 'Scripts\python.exe'
$templatePy = Join-Path $planRoot 'execution_runs\I-00-A\a20260919-01\iso\venv\Scripts\python.exe'
$codeRoot = Join-Path $attempt 'iso\checkout_scripts'
$evidence = Join-Path $attempt "evidence\$Card"
$after = Join-Path $attempt 'after'
$ledger = Join-Path $after 'rc_ledger.txt'

if (-not (Test-Path $after)) { New-Item -ItemType Directory -Path $after | Out-Null }

function Add-Ledger([string]$unitId, [int]$rc) {
    Add-Content -Path $ledger -Value ("{0}`t{1}" -f $unitId, $rc) -Encoding ASCII
}

function Invoke-Unit([string]$unitId, [scriptblock]$action) {
    $console = Join-Path $after ("console_{0}_{1}.txt" -f $unitId, $Card)
    $global:LASTEXITCODE = $null
    $script:unitFail = 0
    & $action 2>&1 | Out-File -FilePath $console -Encoding utf8
    $rc = $global:LASTEXITCODE
    if ($null -eq $rc) { $rc = $script:unitFail }
    Add-Ledger $unitId $rc
    Write-Host ("{0} rc={1} console={2}" -f $unitId, $rc, $console)
    return $rc
}

Write-Host "=== drive_card $Card attempt $attempt ==="
Write-Host "repoRoot    $repoRoot"
Write-Host "companyWiki $companyWiki"
Write-Host "python      $py"
Write-Host "codeRoot    $codeRoot"

# ---- A0: venv (idempotent re-run of the creation command) ----
Invoke-Unit "A0-$Card-iso-venv-create" {
    & $templatePy -m venv $venv
    if (-not $?) { $script:unitFail = 1 }
    Write-Output "template interpreter:"; & $templatePy -V
    Write-Output "attempt interpreter:"; & $py -V
    Write-Output "venv dir: $venv"
    Write-Output "template python: $templatePy"
} | Out-Null

# ---- A1: offline pytest install attempt (environment record only) ----
Invoke-Unit "A1-$Card-pytest-offline-install" {
    & $py -m pip install --no-index pytest
    Write-Output "pip exit code: $LASTEXITCODE"
} | Out-Null

# ---- A2: isolated snapshot copy + hash comparison ----
Invoke-Unit "A2-$Card-isolated-snapshot" {
    Copy-Item (Join-Path $repoRoot 'scripts\model_registry.py') (Join-Path $codeRoot 'model_registry.py') -Force
    if (-not $?) { $script:unitFail = 1 }
    Copy-Item (Join-Path $repoRoot 'scripts\model_extensions.py') (Join-Path $codeRoot 'model_extensions.py') -Force
    if (-not $?) { $script:unitFail = 1 }
    $pairs = @(
        @{ prod = (Join-Path $repoRoot 'scripts\model_registry.py'); iso = (Join-Path $codeRoot 'model_registry.py') },
        @{ prod = (Join-Path $repoRoot 'scripts\model_extensions.py'); iso = (Join-Path $codeRoot 'model_extensions.py') }
    )
    foreach ($pair in $pairs) {
        $h1 = (Get-FileHash -Algorithm SHA256 $pair.prod).Hash.ToLower()
        $h2 = (Get-FileHash -Algorithm SHA256 $pair.iso).Hash.ToLower()
        $verdict = if ($h1 -eq $h2) { 'MATCH' } else { 'DIFF' }
        if ($verdict -ne 'MATCH') { $script:unitFail = 1 }
        Write-Output ("{0} production={1} isolated={2}" -f $verdict, $h1, $h2)
    }
} | Out-Null

# ---- A3: frozen oracle generation ----
Invoke-Unit "A3-$Card-oracle-generate" {
    & $py -X utf8 -B (Join-Path $scriptsDir 'oracle_cards_M09_M12.py') --card $Card --out-root $attempt
} | Out-Null

# ---- A4: regenerate into a scratch root (byte-identity proof input) ----
$regenRoot = Join-Path $attempt 'recovery\regenerate'
Invoke-Unit "A4-$Card-oracle-regenerate-compare" {
    & $py -X utf8 -B (Join-Path $scriptsDir 'oracle_cards_M09_M12.py') --card $Card --out-root $regenRoot
    $names = @('input.json', 'oracle.json', 'cases.json', 'observation_expected.json', 'oracle_selfcheck.json')
    foreach ($name in $names) {
        $frozen = Join-Path $evidence $name
        $regen = Join-Path (Join-Path $regenRoot "evidence\$Card") $name
        $h1 = (Get-FileHash -Algorithm SHA256 $frozen).Hash.ToLower()
        $h2 = (Get-FileHash -Algorithm SHA256 $regen).Hash.ToLower()
        $verdict = if ($h1 -eq $h2) { 'BYTE-IDENTICAL' } else { 'DIFFERENT' }
        if ($verdict -ne 'BYTE-IDENTICAL') { $script:unitFail = 1 }
        Write-Output ("{0} {1} frozen={2} regenerated={3}" -f $verdict, $name, $h1, $h2)
    }
} | Out-Null

# ---- B: the product run (verdict-carrying exit code) ----
$bRc = Invoke-Unit "B-$Card-product-run" {
    & $py -X utf8 -B (Join-Path $scriptsDir 'run_card.py') --card $Card --attempt $attempt `
        --code-root $codeRoot `
        --out (Join-Path $evidence 'run_result.json') `
        --formula-out (Join-Path $evidence 'formula_result.json') `
        --negative-out (Join-Path $evidence 'negative_results.json') `
        --stdout-out (Join-Path $evidence 'stdout.txt') `
        --stderr-out (Join-Path $evidence 'stderr.txt')
}
Write-Host "PRODUCT RUN rc=$bRc"

# ---- C: read-only registry enumeration ----
Invoke-Unit "C-$Card-registry-enumeration" {
    & $py -X utf8 -B (Join-Path $scriptsDir 'enumerate_registry_facts.py') --card $Card `
        --code-root $codeRoot --out (Join-Path $evidence 'registry_enumeration.json')
} | Out-Null

# ---- G: exit-code mutation self-check ----
Invoke-Unit "G-$Card-mutation-selfcheck" {
    & $py -X utf8 -B (Join-Path $scriptsDir 'selfcheck_mutations.py') --card $Card `
        --attempt $attempt --python $py
} | Out-Null

Write-Host "=== ledger ==="
Get-Content $ledger | ForEach-Object { Write-Host $_ }
Write-Host "=== drive_card $Card done ==="
exit 0
