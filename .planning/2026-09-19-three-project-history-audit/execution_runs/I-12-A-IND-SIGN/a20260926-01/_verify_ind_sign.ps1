# _verify_ind_sign.ps1 —— I-12-A 行业面会签只读校验器（K1-K5，冻结自 oracle §4）
# 用法: powershell -NoProfile -ExecutionPolicy Bypass -File _verify_ind_sign.ps1 -Root <attempt|_mut/Rx> -PlanRoot <plan root>
# exit legend: 0=ALL_INVARIANTS_OK  1=harness failure  2=no verdict  3=invariant violation (named K1..K5)
param(
  [Parameter(Mandatory = $true)][string]$Root,
  [Parameter(Mandatory = $true)][string]$PlanRoot
)
$ErrorActionPreference = 'Stop'
$fails = @()
function Check([string]$id, [bool]$cond, [string]$msg) {
  if ($cond) { Write-Output ("CHECK {0} OK   {1}" -f $id, $msg) }
  else { $script:fails += ("{0}: {1}" -f $id, $msg); Write-Output ("CHECK {0} FAIL {1}" -f $id, $msg) }
}
function Get-Sha256Hex([string]$s) {
  $sha = [System.Security.Cryptography.SHA256]::Create()
  (($sha.ComputeHash([System.Text.Encoding]::UTF8.GetBytes($s))) | ForEach-Object { $_.ToString('x2') }) -join ''
}
function Read-JsonFile([string]$path) {
  if (-not (Test-Path -LiteralPath $path)) { Write-Output ("HARNESS missing: {0}" -f $path); exit 1 }
  [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8) | ConvertFrom-Json
}
function Prop($o, [string]$n) { $o.PSObject.Properties[$n] }

$handoffPath = Join-Path $Root 'handoff.json'
$indPath     = Join-Path $Root 'ind_signatures.json'
$ho = Read-JsonFile $handoffPath
$ind = Read-JsonFile $indPath
$items = @($ind.items)
if ($items.Count -eq 0) { Write-Output 'NO VERDICT: items empty'; exit 2 }

# ---------- K1 release lock ----------
Check 'K1_release_lock' ((Prop $ho 'role') -and $ho.role -eq 'industry_reviewer_i12a') 'handoff.role=industry_reviewer_i12a'
Check 'K1_release_lock' ((Prop $ho 'releases_nothing') -and $ho.releases_nothing -eq $true) 'releases_nothing=true'
Check 'K1_release_lock' ((Prop $ho 'statistics_sign_still_needed') -and $ho.statistics_sign_still_needed -eq $true) 'statistics_sign_still_needed=true (统计面 6 项仍待签)'
Check 'K1_release_lock' ((Prop $ho 'git_diff_non_planning') -and [int]$ho.git_diff_non_planning -eq 0) 'git_diff_non_planning=0'
Check 'K1_release_lock' ((Prop $ho 'writes_outside_planning') -and [int]$ho.writes_outside_planning -eq 0) 'writes_outside_planning=0'
Check 'K1_release_lock' ((Prop $ho 'params_released') -and $ho.params_released -eq $false -and [int]$ho.params_released_count -eq 0) 'params_released=false / count=0'
$accept = (Prop $ho 'produces_accept')
Check 'K1_release_lock' ((-not $accept) -or $ho.produces_accept -ne $true) 'produces_accept!=true (不产生 ACCEPT)'

# ---------- K2 seal discipline ----------
Check 'K2_seal_discipline' ((Prop $ho 'test_results_unsealed') -and $ho.test_results_unsealed -eq $false) 'handoff.test_results_unsealed=false'
Check 'K2_seal_discipline' ((Prop $ho 'test_results_sealed') -and $ho.test_results_sealed -eq $true) 'handoff.test_results_sealed=true'
Check 'K2_seal_discipline' ((Prop $ho 'accuracy_results_read') -and $ho.accuracy_results_read -eq $false) 'handoff.accuracy_results_read=false'
$seal = $ind.seal_state
Check 'K2_seal_discipline' ($seal.test_results_sealed -eq $true -and $seal.test_results_unsealed -eq $false) 'ind_signatures.seal_state 封存标志'
Check 'K2_seal_discipline' ($seal.accuracy_results_read -eq $false) 'ind_signatures.seal_state.accuracy_results_read=false'
Check 'K2_seal_discipline' (@($seal.reads_forbidden_and_not_performed).Count -gt 0) 'reads_forbidden_and_not_performed 非空（封存令登记）'

# ---------- K3 source integrity (9 件逐件复算) ----------
$sh = $ind.source_hashes
$keys = @($sh.PSObject.Properties | Where-Object { $_.Name -ne 'note' } | ForEach-Object { $_.Name })
Check 'K3_source_integrity' ($keys.Count -eq 9) ("source_hashes 计数=9 (实测 {0})" -f $keys.Count)
foreach ($k in $keys) {
  $full = Join-Path $PlanRoot ($k -replace '/', [System.IO.Path]::DirectorySeparatorChar)
  if (-not (Test-Path -LiteralPath $full)) { Check 'K3_source_integrity' $false "缺失回源件 $k"; continue }
  $got = (Get-FileHash -Algorithm SHA256 -LiteralPath $full).Hash.ToLower()
  Check 'K3_source_integrity' ($got -eq [string]$sh.$k) ("{0} sha256 复算一致" -f $k)
}

# ---------- K4 signature discipline ----------
$validRulings = @('SIGNED', 'NOT_SIGNED', 'deferred_to_statistics')
$signedCount = 0
$industryUnsigned = 0
$cosignOutstanding = 0
foreach ($it in $items) {
  $id = [string]$it.item_id
  if ($validRulings -notcontains [string]$it.ruling) { $fails += ("K4_signature_discipline: {0} ruling 非法 {1}" -f $id, $it.ruling); continue }
  if ($it.ruling -eq 'SIGNED') {
    $signedCount++
    Check 'K4_signature_discipline' ((Prop $it 'signed_by') -and $it.signed_by -eq 'industry_reviewer_i12a') ("{0} signed_by=industry_reviewer_i12a" -f $id)
    Check 'K4_signature_discipline' (-not [bool]$it.belongs_to_statistical_six) ("{0} 非统计面 6 项（行业面不代签统计阈值）" -f $id)
    $ok = -not [string]::IsNullOrWhiteSpace([string]$it.choice) -and
          (@($it.rationale_refs).Count -gt 0) -and
          -not [string]::IsNullOrWhiteSpace([string]$it.counterexample) -and
          -not [string]::IsNullOrWhiteSpace([string]$it.compatibility_impact) -and
          -not [string]::IsNullOrWhiteSpace([string]$it.recovery_rule) -and
          (@($it.rejected_alternatives).Count -gt 0)
    Check 'K4_signature_discipline' $ok ("{0} 六要素齐全（选择/依据file+line/反例/兼容影响/恢复规则/被拒方案）" -f $id)
    $recomputed = Get-Sha256Hex ([string]$it.decision_payload)
    Check 'K4_signature_discipline' ($recomputed -eq [string]$it.decision_sha256) ("{0} decision_sha256=sha256(decision_payload)" -f $id)
    Check 'K4_signature_discipline' ([string]$it.decision_sha256 -ne 'NOT_SIGNED') ("{0} 已签项不得标 NOT_SIGNED" -f $id)
  } else {
    Check 'K4_signature_discipline' ([string]$it.decision_sha256 -eq 'NOT_SIGNED') ("{0} 未签项 decision_sha256 字面 NOT_SIGNED" -f $id)
  }
  if ([bool]$it.belongs_to_statistical_six -and $it.ruling -eq 'SIGNED') { $fails += ("K4_signature_discipline: {0} 行业面代签统计面 6 项" -f $id) }
  if ([bool]$it.industry_face -and $it.ruling -ne 'SIGNED') { $industryUnsigned++ }
  if ((Prop $it 'requires_industry_cosign') -and [bool]$it.requires_industry_cosign -and $it.ruling -ne 'SIGNED') { $cosignOutstanding++ }
}
$computedComplete = ($industryUnsigned -eq 0 -and $cosignOutstanding -eq 0)
Check 'K4_signature_discipline' ([int]$ind.summary.signed_count -eq $signedCount) ("summary.signed_count={0} == 计数 {1}" -f $ind.summary.signed_count, $signedCount)
Check 'K4_signature_discipline' ([int]$ind.summary.total_items -eq $items.Count) ("summary.total_items={0} == items {1}" -f $ind.summary.total_items, $items.Count)
Check 'K4_signature_discipline' ((Prop $ho 'industry_countersign_complete') -and ($ho.industry_countersign_complete -eq $computedComplete)) ("handoff.industry_countersign_complete={0} == 计算值 {1}（未签行业项 {2}、待共同签 {3}）" -f $ho.industry_countersign_complete, $computedComplete, $industryUnsigned, $cosignOutstanding)
Check 'K4_signature_discipline' ($ind.summary.industry_countersign_complete -eq $computedComplete) 'ind_signatures.summary.industry_countersign_complete 与计算值一致'
Check 'K4_signature_discipline' ($computedComplete -eq $false) ('行业面存在未签项 ⇒ 必须 fail-closed false（本轮未签行业项存在）')

# ---------- K5 write boundary ----------
$prefix = 'execution_runs/I-12-A-IND-SIGN/a20260926-01'
$wf = $ho.written_files
$wfKeys = @($wf.PSObject.Properties | Where-Object { $_.Name -ne 'note' } | ForEach-Object { $_.Name })
$wfBad = @($wfKeys | Where-Object { -not $_.StartsWith($prefix) })
Check 'K5_write_boundary' ($wfKeys.Count -gt 0 -and $wfBad.Count -eq 0) ("written_files 全部落在本 attempt 目录（{0} 件，越界 {1}）" -f $wfKeys.Count, $wfBad.Count)
$cp = @($ho.changed_paths)
$cpBad = @($cp | Where-Object { -not $_.StartsWith($prefix) })
Check 'K5_write_boundary' ($cp.Count -gt 0 -and $cpBad.Count -eq 0) ("changed_paths 全部落在本 attempt 目录（{0} 件，越界 {1}）" -f $cp.Count, $cpBad.Count)
Check 'K5_write_boundary' ((Prop $ho 'i12a_files_modified') -and [int]$ho.i12a_files_modified -eq 0) 'I-12-A 目录写入数=0（只读）'

# ---------- verdict ----------
if ($fails.Count -gt 0) {
  foreach ($f in $fails) { Write-Output ("VIOLATION {0}" -f $f) }
  Write-Output ("RESULT INVARIANTS_VIOLATED count={0}" -f $fails.Count)
  exit 3
}
Write-Output 'CHECK K1-K5 ALL OK'
Write-Output 'RESULT ALL_INVARIANTS_OK'
exit 0
