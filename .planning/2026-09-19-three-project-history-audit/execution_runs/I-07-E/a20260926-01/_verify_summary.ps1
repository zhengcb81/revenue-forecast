# _verify_summary.ps1 -- I-07-E/a20260926-01 invariant verifier (read-only; shared by green/red arms)
# usage: powershell -NoProfile -ExecutionPolicy Bypass -File _verify_summary.ps1 -Root <attempt-or-mut-dir> -PlanRoot <plan-root>
# exit_code_legend (frozen, START_HERE table): 0=ALL_INVARIANTS_OK 1=harness failure 2=no verdict 3=invariant violation (named)
param(
  [Parameter(Mandatory=$true)][string]$Root,
  [Parameter(Mandatory=$true)][string]$PlanRoot
)
$ErrorActionPreference = 'Stop'
$violations = @()
function Add-Violation([string]$id, [string]$msg) {
  $script:violations += ($id + ': ' + $msg)
  Write-Output ('VIOLATION ' + $id + ': ' + $msg)
}
function Add-Ok([string]$id, [string]$msg) { Write-Output ('CHECK ' + $id + ': OK -- ' + $msg) }

$summaryPath = Join-Path $Root 'calibration_validation_summary.md'
$handoffPath = Join-Path $Root 'handoff.json'
$verifPath   = Join-Path $Root 'verification.json'
foreach ($p in @($summaryPath, $handoffPath, $verifPath)) {
  if (-not (Test-Path $p)) { Write-Output ('HARNESS missing input: ' + $p); exit 1 }
}
$summary = Get-Content $summaryPath -Raw -Encoding UTF8
$handoff = Get-Content $handoffPath -Raw -Encoding UTF8 | ConvertFrom-Json
$verif   = Get-Content $verifPath   -Raw -Encoding UTF8 | ConvertFrom-Json

# ---- J1 release lock (handoff) ----
$j1ok = $true
if ($handoff.params_released -ne $false)    { Add-Violation 'J1' 'handoff.params_released != false'; $j1ok = $false }
if ($handoff.implementer_signed -ne $false) { Add-Violation 'J1' 'handoff.implementer_signed != false'; $j1ok = $false }
if ($handoff.releases_nothing -ne $true)    { Add-Violation 'J1' 'handoff.releases_nothing != true'; $j1ok = $false }
if ($handoff.status -ne 'review_pending')   { Add-Violation 'J1' ('handoff.status != review_pending, got: ' + $handoff.status); $j1ok = $false }
if ($j1ok) { Add-Ok 'J1' 'params_released=false / implementer_signed=false / releases_nothing=true / status=review_pending' }

# ---- J2 OPEN-2 red line (register-only, never consumed) ----
$j2ok = $true
if (-not $summary.Contains('open2_ban_observed=true')) { Add-Violation 'J2' 'summary missing open2_ban_observed=true'; $j2ok = $false }
if (-not $summary.Contains('registered_not_consumed')) { Add-Violation 'J2' 'summary missing registered_not_consumed'; $j2ok = $false }
if ($summary.Contains('consumed_for_forecast'))        { Add-Violation 'J2' 'summary contains consumed_for_forecast (banned value consumed)'; $j2ok = $false }
if ($handoff.open2_ban_observed -ne $true)             { Add-Violation 'J2' 'handoff.open2_ban_observed != true'; $j2ok = $false }
if ($j2ok) { Add-Ok 'J2' 'OPEN-2 ban observed: registered_not_consumed, no consumption marker' }

# ---- J3 upstream sha consistency (recompute vs frozen list in verification.json) ----
$j3ok = $true
$n = 0
foreach ($u in $verif.upstream_inputs) {
  $n++
  $p = Join-Path $PlanRoot ($u.path -replace '/', '\')
  if (-not (Test-Path $p)) { Add-Violation 'J3' ('upstream missing: ' + $u.path); $j3ok = $false; continue }
  $actual = (Get-FileHash $p -Algorithm SHA256).Hash.ToLower()
  if ($actual -ne $u.sha256) { Add-Violation 'J3' ('sha mismatch ' + $u.path + ' recorded=' + $u.sha256 + ' actual=' + $actual); $j3ok = $false }
}
if ($j3ok) { Add-Ok 'J3' ('upstream sha256 recomputed match for ' + $n + ' inputs') }

# ---- J4 EA template (H4 (iv) form) ----
$j4ok = $true
$countFalse = ([regex]::Matches($summary, [regex]::Escape('equivalent_to_disclosure_basis=false'))).Count
$countTrue  = ([regex]::Matches($summary, [regex]::Escape('equivalent_to_disclosure_basis=true'))).Count
if ($countFalse -lt 7) { Add-Violation 'J4' ('EA template broken: equivalent_to_disclosure_basis=false count=' + $countFalse + ' (<7)'); $j4ok = $false }
if ($countTrue -gt 0)  { Add-Violation 'J4' ('EA constant rewritten: equivalent_to_disclosure_basis=true count=' + $countTrue); $j4ok = $false }
foreach ($ea in 1..7) {
  if (-not $summary.Contains('EA-' + $ea)) { Add-Violation 'J4' ('EA-' + $ea + ' missing'); $j4ok = $false }
}
if (-not $summary.Contains('sensitivity_interval')) { Add-Violation 'J4' 'sensitivity_interval missing'; $j4ok = $false }
if ($j4ok) { Add-Ok 'J4' ('EA-1..EA-7 present; equivalent_to_disclosure_basis=false x' + $countFalse + '; =true x0') }

# ---- J5 synthetic-number quarantine ----
$j5ok = $true
if (-not $summary.Contains('synthetic_quarantine_enforced=true')) { Add-Violation 'J5' 'summary missing synthetic_quarantine_enforced=true'; $j5ok = $false }
$quarantine = @('281520','299040','17520','264000')
foreach ($line in ($summary -split "`n")) {
  foreach ($q in $quarantine) {
    if ($line.Contains($q)) {
      if (-not $line.Contains('quarantine')) {
        Add-Violation 'J5' ('quarantined synthetic number ' + $q + ' outside quarantine register line')
        $j5ok = $false
      }
    }
  }
}
if ($j5ok) { Add-Ok 'J5' 'synthetic numbers quarantined (281520/299040/17520/264000 only in quarantine register)' }

if ($violations.Count -eq 0) { Write-Output 'RESULT ALL_INVARIANTS_OK'; exit 0 }
Write-Output ('RESULT INVARIANT_VIOLATION count=' + $violations.Count)
exit 3
