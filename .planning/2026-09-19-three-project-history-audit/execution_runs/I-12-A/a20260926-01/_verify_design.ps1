param(
  [Parameter(Mandatory = $true)][string]$Root,
  [Parameter(Mandatory = $true)][string]$PlanRoot
)
# I-12-A design verifier. exit legend: 0=ALL_INVARIANTS_OK 1=harness 2=no verdict 3=violation(named)
$ErrorActionPreference = 'Stop'
$script:viol = @()

function Write-Check([string]$m) { Write-Output ("CHECK " + $m + " ... OK") }
function Add-Viol([string]$m) { $script:viol += $m; Write-Output ("VIOLATION " + $m) }
function Get-Sha([string]$p) { (Get-FileHash -LiteralPath $p -Algorithm SHA256).Hash.ToLower() }
function Read-Utf8([string]$p) { [System.IO.File]::ReadAllText($p) }
function Join-Rel([string]$base, [string]$rel) { Join-Path $base ($rel.Replace('/', [string][char]92)) }
function Get-Reviewer($pa, [string]$id) { @($pa.reviewers) | Where-Object { $_.id -eq $id } | Select-Object -First 1 }

try {
  if (-not (Test-Path -LiteralPath $Root)) { Write-Output ("HARNESS root missing: " + $Root); exit 1 }
  $oraclePath = Join-Path $Root 'oracle.md'
  $handPath = Join-Path $Root 'handoff.json'
  $edPath = Join-Path $Root 'evidence\I-12-A\evaluation_design.json'
  $paPath = Join-Path $Root 'evidence\I-12-A\professional_approval.json'
  $mfPath = Join-Path $Root 'evidence\I-12-A\design_manifest.json'
  foreach ($p in @($oraclePath, $handPath, $edPath, $paPath, $mfPath)) {
    if (-not (Test-Path -LiteralPath $p)) { Write-Output ("HARNESS input missing: " + $p); exit 1 }
  }

  $oracle = Read-Utf8 $oraclePath
  $handRaw = Read-Utf8 $handPath
  $edRaw = Read-Utf8 $edPath
  $h = $handRaw | ConvertFrom-Json
  $ed = $edRaw | ConvertFrom-Json
  $pa = (Read-Utf8 $paPath) | ConvertFrom-Json
  $mf = (Read-Utf8 $mfPath) | ConvertFrom-Json

  # ---- J1 release lock ----
  if ($h.params_released -ne $false) { Add-Viol 'J1: handoff.params_released != false' }
  if ($h.implementer_signed -ne $false) { Add-Viol 'J1: handoff.implementer_signed != false' }
  if ($h.releases_nothing -ne $true) { Add-Viol 'J1: handoff.releases_nothing != true' }
  if ($h.status -ne 'review_pending') { Add-Viol 'J1: handoff.status != review_pending' }
  if ($h.params_released_count -ne 0) { Add-Viol 'J1: handoff.params_released_count != 0' }
  if ($h.releases_nothing -eq $true -and $h.params_released -eq $false -and $h.implementer_signed -eq $false -and $h.status -eq 'review_pending' -and $h.params_released_count -eq 0) { Write-Check 'J1_release_lock' }

  # ---- J2 open2 ban (register only, never consume) ----
  $j2 = $true
  if ($h.open2_ban_observed -ne $true) { Add-Viol 'J2: handoff.open2_ban_observed != true'; $j2 = $false }
  if ($oracle -notmatch 'registered_not_consumed') { Add-Viol 'J2: oracle missing registered_not_consumed'; $j2 = $false }
  if ($edRaw -notmatch 'registered_not_consumed') { Add-Viol 'J2: evaluation_design missing registered_not_consumed'; $j2 = $false }
  if ($edRaw -match 'consumed_for_forecast') { Add-Viol 'J2: evaluation_design contains consumed_for_forecast'; $j2 = $false }
  $ln = 0
  foreach ($line in ($oracle -split "`r?`n")) {
    $ln++
    # token may appear ONLY as (a) the J2 invariant definition row, (b) the frozen M2 mutation-registry row,
    # (c) the section-4 consumption-rule definition row naming the M2 kill. Any other line = consumed value.
    if ($line -match 'consumed_for_forecast' -and $line -notmatch 'M2' -and $line -notmatch 'J2_open2_ban') {
      Add-Viol ('J2: oracle line ' + $ln + ' carries consumed_for_forecast outside the frozen M2/J2 definition rows')
      $j2 = $false
    }
  }
  try {
    if ($ed.open2_redline_registration.registration_state -ne 'registered_not_consumed') { Add-Viol 'J2: registration_state != registered_not_consumed'; $j2 = $false }
    if ($ed.open2_redline_registration.consumed_in_design -ne $false) { Add-Viol 'J2: consumed_in_design != false'; $j2 = $false }
    if ($ed.open2_ban_observed -ne $true) { Add-Viol 'J2: evaluation_design.open2_ban_observed != true'; $j2 = $false }
  } catch { Add-Viol 'J2: evaluation_design open2 block unreadable'; $j2 = $false }
  if ($j2) { Write-Check 'J2_open2_ban' }

  # ---- J3 upstream sha (plan-root relative) ----
  $j3 = $true
  $n3 = 0
  foreach ($u in @($mf.upstream_inputs)) {
    $n3++
    $p = Join-Rel $PlanRoot ([string]$u.path)
    if (-not (Test-Path -LiteralPath $p)) { Add-Viol ('J3: upstream missing ' + $u.path); $j3 = $false; continue }
    $a = Get-Sha $p
    if ($a -ne [string]$u.sha256) { Add-Viol ('J3: sha mismatch ' + $u.path + ' recorded=' + [string]$u.sha256 + ' actual=' + $a); $j3 = $false }
    $b = (Get-Item -LiteralPath $p).Length
    if ($b -ne [int]$u.bytes) { Add-Viol ('J3: bytes mismatch ' + $u.path + ' recorded=' + [string]$u.bytes + ' actual=' + $b); $j3 = $false }
  }
  if ($n3 -ne 11) { Add-Viol ('J3: upstream_inputs count ' + $n3 + ' != 11'); $j3 = $false }
  if ($j3) { Write-Check ('J3_upstream_sha (' + $n3 + ' files)') }

  # ---- J4 professional signoff integrity (never self-signed, STOP must be registered) ----
  $j4 = $true
  $sr = Get-Reviewer $pa 'statistical_reviewer'
  $ir = Get-Reviewer $pa 'industry_reviewer'
  $im = Get-Reviewer $pa 'implementer_i12a'
  if ($null -eq $sr -or $null -eq $ir -or $null -eq $im) { Add-Viol 'J4: reviewer block missing'; $j4 = $false }
  else {
    if ($sr.signed -ne $false) { Add-Viol 'J4: statistical_reviewer.signed != false (self/proxy sign)'; $j4 = $false }
    if ($ir.signed -ne $false) { Add-Viol 'J4: industry_reviewer.signed != false (self/proxy sign)'; $j4 = $false }
    if ($sr.signature_status -ne 'unsigned') { Add-Viol 'J4: statistical_reviewer.signature_status != unsigned'; $j4 = $false }
    if ($ir.signature_status -ne 'unsigned') { Add-Viol 'J4: industry_reviewer.signature_status != unsigned'; $j4 = $false }
    if ($im.signed -ne $false) { Add-Viol 'J4: implementer.signed != false'; $j4 = $false }
    if ($im.may_sign -ne $false) { Add-Viol 'J4: implementer.may_sign != false'; $j4 = $false }
  }
  if ($pa.stop_condition.triggered -ne $true) { Add-Viol 'J4: stop_condition.triggered != true (unsigned options must register BLOCKED_PROFESSIONAL_DECISION)'; $j4 = $false }
  if ($pa.stop_condition.code -ne 'BLOCKED_PROFESSIONAL_DECISION') { Add-Viol 'J4: stop_condition.code != BLOCKED_PROFESSIONAL_DECISION'; $j4 = $false }
  if ($j4) { Write-Check 'J4_professional_signoff' }

  # ---- J5 result seal ----
  $j5 = $true
  if ($mf.test_results_unsealed -ne $false) { Add-Viol 'J5: design_manifest.test_results_unsealed != false'; $j5 = $false }
  if ($mf.accuracy_results_read -ne $false) { Add-Viol 'J5: design_manifest.accuracy_results_read != false'; $j5 = $false }
  if ($ed.test_results_sealed -ne $true) { Add-Viol 'J5: evaluation_design.test_results_sealed != true'; $j5 = $false }
  if ($ed.accuracy_results_read -ne $false) { Add-Viol 'J5: evaluation_design.accuracy_results_read != false'; $j5 = $false }
  if ($ed.results_unsealed -ne $false) { Add-Viol 'J5: evaluation_design.results_unsealed != false'; $j5 = $false }
  if ($j5) { Write-Check 'J5_result_seal' }

  # ---- J6 manifest freeze (artifact shas) ----
  $j6 = $true
  $n6 = 0
  foreach ($a in @($mf.artifacts_frozen)) {
    $n6++
    $p = Join-Rel $Root ([string]$a.path)
    if (-not (Test-Path -LiteralPath $p)) { Add-Viol ('J6: artifact missing ' + $a.path); $j6 = $false; continue }
    $s = Get-Sha $p
    if ($s -ne [string]$a.sha256) { Add-Viol ('J6: artifact sha mismatch ' + $a.path + ' recorded=' + [string]$a.sha256 + ' actual=' + $s); $j6 = $false }
    $b = (Get-Item -LiteralPath $p).Length
    if ($b -ne [int]$a.bytes) { Add-Viol ('J6: artifact bytes mismatch ' + $a.path + ' recorded=' + [string]$a.bytes + ' actual=' + $b); $j6 = $false }
  }
  if ($n6 -ne 3) { Add-Viol ('J6: artifacts_frozen count ' + $n6 + ' != 3'); $j6 = $false }
  if ($j6) { Write-Check ('J6_manifest_freeze (' + $n6 + ' artifacts)') }
}
catch {
  Write-Output ("HARNESS: " + $_.Exception.Message)
  exit 1
}

if ($script:viol.Count -eq 0) {
  Write-Output 'RESULT ALL_INVARIANTS_OK'
  exit 0
} else {
  Write-Output ('RESULT ' + $script:viol.Count + ' NAMED VIOLATION(S)')
  exit 3
}
