# _verify_signatures.ps1 — I-12-A-STAT-SIGN 只读校验器
# 判据冻结于 oracle.md §3（C1-C7）与 §5（逐项可签性判定/数值表）。
# 用法: powershell -NoProfile -ExecutionPolicy Bypass -File _verify_signatures.ps1 -Root <dir含stat_signatures.json>
# exit: 0=ALL_CRITERIA_OK · 1=harness 失败 · 2=无裁决 · 3=判据违例（具名 K1..K8）
param(
  [Parameter(Mandatory = $true)][string]$Root,
  [string]$PlanRoot = '.planning/2026-09-19-three-project-history-audit'
)
$ErrorActionPreference = 'Stop'
$fail = New-Object System.Collections.Generic.List[string]
function Add-Fail([string]$id, [string]$msg) { [void]$fail.Add("$id : $msg") }
function Sha([string]$s) {
  $b = [System.Text.UTF8Encoding]::new($false).GetBytes($s)
  ([BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash($b)) -replace '-', '').ToLower()
}
function FileSha([string]$p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() }

try {
  $sigPath = Join-Path $Root 'stat_signatures.json'
  if (-not (Test-Path -LiteralPath $sigPath)) { throw "stat_signatures.json not found at $sigPath" }
  $raw = [System.IO.File]::ReadAllText($sigPath, [System.Text.Encoding]::UTF8)
  $j = $raw | ConvertFrom-Json
} catch { Write-Output "HARNESS_ERROR: $_"; exit 1 }

$expSel = [ordered]@{ S1 = 'NOT_SIGNED'; S2 = 'NOT_SIGNED'; S3 = 'SIGNED'; S4 = 'SIGNED'; S5 = 'SIGNED'; S6 = 'NOT_SIGNED' }
$expField = [ordered]@{ S1 = 5; S2 = 10; S3 = 11; S4 = 11; S5 = 11; S6 = 12 }
$ids = @($expSel.Keys)

# ---------- K1_items_set ----------
$k1 = $true
if ($j.items.Count -ne 6) { $k1 = $false; Add-Fail 'K1_items_set' "items.Count=$($j.items.Count) != 6" }
for ($i = 0; $i -lt $ids.Count; $i++) {
  $it = $j.items[$i]
  if ($it.item_id -ne $ids[$i]) { $k1 = $false; Add-Fail 'K1_items_set' "order[$i]=$($it.item_id) != $($ids[$i])" }
  if ([int]$it.field_index -ne [int]$expField[$it.item_id]) { $k1 = $false; Add-Fail 'K1_items_set' "$($it.item_id).field_index=$($it.field_index) != $($expField[$it.item_id])" }
}
if ($k1) { Write-Output 'CHECK K1_items_set OK' }

# ---------- K2_verdict_lock（oracle §5 冻结判定） ----------
$k2 = $true
foreach ($it in $j.items) {
  if ([string]$it.selection -ne [string]$expSel[$it.item_id]) {
    $k2 = $false
    Add-Fail 'K2_verdict_lock' "$($it.item_id).selection=$($it.selection) != frozen $($expSel[$it.item_id])"
  }
}
if ($k2) { Write-Output 'CHECK K2_verdict_lock OK' }

# ---------- K3_value_lock（oracle §5 冻结数值表） ----------
$k3 = $true
function Get-ItemById([string]$id) { foreach ($x in $j.items) { if ($x.item_id -eq $id) { return $x } } return $null }
$s3 = Get-ItemById 'S3'; $s4 = Get-ItemById 'S4'; $s5 = Get-ItemById 'S5'
if ([math]::Abs([double]$s3.value.confidence_level - 0.95) -gt 1e-9) { $k3 = $false; Add-Fail 'K3_value_lock' "S3.confidence_level=$($s3.value.confidence_level) != 0.95" }
if ([math]::Abs([double]$s3.value.alpha - 0.05) -gt 1e-9) { $k3 = $false; Add-Fail 'K3_value_lock' "S3.alpha=$($s3.value.alpha) != 0.05" }
if ([string]$s3.value.ci_form -ne 'two_sided') { $k3 = $false; Add-Fail 'K3_value_lock' "S3.ci_form=$($s3.value.ci_form) != two_sided" }
if ([int]$s4.value.repetitions -ne 10000) { $k3 = $false; Add-Fail 'K3_value_lock' "S4.repetitions=$($s4.value.repetitions) != 10000" }
if ([int64]$s4.value.seed -ne 2765402844) { $k3 = $false; Add-Fail 'K3_value_lock' "S4.seed=$($s4.value.seed) != 2765402844" }
if ([string]$s5.value.method -ne 'holm') { $k3 = $false; Add-Fail 'K3_value_lock' "S5.method=$($s5.value.method) != holm" }
if ([string]$s5.value.error_control -ne 'FWER') { $k3 = $false; Add-Fail 'K3_value_lock' "S5.error_control=$($s5.value.error_control) != FWER" }
if ([math]::Abs([double]$s5.value.alpha - 0.05) -gt 1e-9) { $k3 = $false; Add-Fail 'K3_value_lock' "S5.alpha=$($s5.value.alpha) != 0.05" }
foreach ($id in @('S1', 'S2', 'S6')) {
  $it = Get-ItemById $id
  if (($null -ne $it) -and ($null -ne $it.value)) {
    $n = @($it.value.PSObject.Properties).Count
    if ($n -ne 0) { $k3 = $false; Add-Fail 'K3_value_lock' "$id is NOT_SIGNED but carries $n value properties (阈值不得无据落地)" }
  } elseif ($null -eq $it) {
    $k3 = $false; Add-Fail 'K3_value_lock' "$id missing"
  }
}
if ($k3) { Write-Output 'CHECK K3_value_lock OK' }

# ---------- K4_signature_form ----------
$k4 = $true
foreach ($it in $j.items) {
  $sel = [string]$it.selection
  $payload = [string]$it.decision_payload_canonical
  if ([string]::IsNullOrWhiteSpace($payload)) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id).decision_payload_canonical empty"; continue }
  if ($sel -eq 'SIGNED') {
    if ([string]::IsNullOrWhiteSpace([string]$it.decision_sha256)) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) SIGNED but decision_sha256 null" }
    if ([string]$it.signature.role -ne 'statistics_reviewer_i12a') { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id).signature.role wrong" }
    if ([bool]$it.signature.signed -ne $true) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) SIGNED but signature.signed!=true" }
    if (@($it.evidence).Count -lt 1) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) SIGNED without evidence refs" }
    foreach ($e in @($it.evidence)) { if ([string]$e.path -or [string]$e.lines) {} else { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) evidence entry missing path/lines" } }
    if ([string]::IsNullOrWhiteSpace([string]$it.rationale) -or [string]::IsNullOrWhiteSpace([string]$it.recovery_rule)) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) missing rationale/recovery_rule" }
    if (@($it.rejected_alternatives).Count -lt 1) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) missing rejected_alternatives" }
    if ($null -eq $it.counterexample -or [string]::IsNullOrWhiteSpace([string]$it.counterexample.arm)) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) missing counterexample" }
    if (-not [string]::IsNullOrWhiteSpace([string]$it.refusal_sha256)) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) SIGNED must not carry refusal_sha256" }
  } elseif ($sel -eq 'NOT_SIGNED') {
    if ($null -ne $it.decision_sha256) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) NOT_SIGNED must carry decision_sha256=null" }
    if ([string]::IsNullOrWhiteSpace([string]$it.refusal_sha256)) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) NOT_SIGNED missing refusal_sha256" }
    if ([string]$it.refusal_reason_code -ne 'insufficient_evidence') { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) refusal_reason_code != insufficient_evidence" }
    if (@($it.missing_evidence_measured).Count -lt 1) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) NOT_SIGNED without measured missing evidence" }
    foreach ($m in @($it.missing_evidence_measured)) { if ([string]::IsNullOrWhiteSpace([string]$m.source)) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) missing_evidence_measured source 为空" } }
    if ([bool]$it.signature.signed -ne $false) { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) NOT_SIGNED but signature.signed!=false" }
    if (-not [string]::IsNullOrWhiteSpace([string]$it.rationale) -and -not [string]::IsNullOrWhiteSpace([string]$it.recovery_rule)) {} else { $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id) missing rationale/recovery_rule" }
  } else {
    $k4 = $false; Add-Fail 'K4_signature_form' "$($it.item_id).selection invalid: $sel"
  }
}
if ($k4) { Write-Output 'CHECK K4_signature_form OK' }

# ---------- K5_result_seal（封存令） ----------
$k5 = $true
if ([bool]$j.source_seal.test_results_sealed -ne $true) { $k5 = $false; Add-Fail 'K5_result_seal' 'test_results_sealed != true' }
if ([bool]$j.source_seal.accuracy_results_read -ne $false) { $k5 = $false; Add-Fail 'K5_result_seal' 'accuracy_results_read != false' }
if ([bool]$j.source_seal.results_read_before_signing -ne $false) { $k5 = $false; Add-Fail 'K5_result_seal' 'results_read_before_signing != false' }
if ([bool]$j.boundary_declaration.test_results_read -ne $false) { $k5 = $false; Add-Fail 'K5_result_seal' 'boundary.test_results_read != false' }
if ([bool]$j.boundary_declaration.test_results_unsealed -ne $false) { $k5 = $false; Add-Fail 'K5_result_seal' 'boundary.test_results_unsealed != false' }
$forbidden = @('I-10-B', 'I-13', 'accuracy', 'backtest', '回测', 'I10B')
foreach ($it in $j.items) {
  foreach ($e in @($it.evidence)) {
    foreach ($f in $forbidden) { if ([string]$e.path -and ([string]$e.path).Contains($f)) { $k5 = $false; Add-Fail 'K5_result_seal' "$($it.item_id) evidence path 引用封存面: $($e.path)" } }
  }
}
if ($k5) { Write-Output 'CHECK K5_result_seal OK' }

# ---------- K6_boundary_lock（不代签/不放行/STOP① 未解除） ----------
$k6 = $true
if ([bool]$j.summary.industry_countersign_still_needed -ne $true) { $k6 = $false; Add-Fail 'K6_boundary_lock' 'summary.industry_countersign_still_needed != true' }
if ([bool]$j.boundary_declaration.industry_countersign_still_needed -ne $true) { $k6 = $false; Add-Fail 'K6_boundary_lock' 'boundary.industry_countersign_still_needed != true' }
if ([bool]$j.boundary_declaration.industry_signature_performed_by_this_attempt -ne $false) { $k6 = $false; Add-Fail 'K6_boundary_lock' 'industry_signature_performed_by_this_attempt != false' }
if ([bool]$j.summary.releases_nothing -ne $true) { $k6 = $false; Add-Fail 'K6_boundary_lock' 'summary.releases_nothing != true' }
if ([bool]$j.boundary_declaration.releases_nothing -ne $true) { $k6 = $false; Add-Fail 'K6_boundary_lock' 'boundary.releases_nothing != true' }
if ([bool]$j.boundary_declaration.params_released -ne $false) { $k6 = $false; Add-Fail 'K6_boundary_lock' 'params_released != false' }
if ([bool]$j.boundary_declaration.stop1_still_triggered -ne $true) { $k6 = $false; Add-Fail 'K6_boundary_lock' 'stop1_still_triggered != true' }
if ([bool]$j.boundary_declaration.produces_ACCEPT -ne $false) { $k6 = $false; Add-Fail 'K6_boundary_lock' 'produces_ACCEPT != false' }
if ([bool]$j.boundary_declaration.implementer_signed -ne $false) { $k6 = $false; Add-Fail 'K6_boundary_lock' 'implementer_signed != false' }
if ([string]$j.summary.stop1_state -ne 'BLOCKED_PROFESSIONAL_DECISION_still_triggered') { $k6 = $false; Add-Fail 'K6_boundary_lock' "stop1_state=$($j.summary.stop1_state)" }
foreach ($it in $j.items) {
  if (-not ([string]$it.signature.industry_countersign).StartsWith('required')) { $k6 = $false; Add-Fail 'K6_boundary_lock' "$($it.item_id).industry_countersign != required_separately" }
  if ([string]$it.signature.role -ne 'statistics_reviewer_i12a') { $k6 = $false; Add-Fail 'K6_boundary_lock' "$($it.item_id).signature.role != statistics_reviewer_i12a" }
}
if ($k6) { Write-Output 'CHECK K6_boundary_lock OK' }

# ---------- K7_hash_integrity（decision_sha256 写前写后复算 + oracle 冻结） ----------
$k7 = $true
foreach ($it in $j.items) {
  $post = Sha ([string]$it.decision_payload_canonical)
  if ($it.selection -eq 'SIGNED') {
    if ([string]$it.decision_sha256 -ne $post) { $k7 = $false; Add-Fail 'K7_hash_integrity' "$($it.item_id) decision_sha256 mismatch (recorded=$($it.decision_sha256) recomputed=$post)" }
  } else {
    if ([string]$it.refusal_sha256 -ne $post) { $k7 = $false; Add-Fail 'K7_hash_integrity' "$($it.item_id) refusal_sha256 mismatch (recorded=$($it.refusal_sha256) recomputed=$post)" }
  }
}
try {
  $oraclePath = Join-Path $PlanRoot ([string]$j.oracle.path -replace '/', [IO.Path]::DirectorySeparatorChar)
  if (Test-Path -LiteralPath $oraclePath) {
    $oh = FileSha $oraclePath; $ob = (Get-Item -LiteralPath $oraclePath).Length
    if ($oh -ne [string]$j.oracle.sha256) { $k7 = $false; Add-Fail 'K7_hash_integrity' "oracle sha mismatch $oh vs $($j.oracle.sha256)" }
    if ([int64]$ob -ne [int64]$j.oracle.bytes) { $k7 = $false; Add-Fail 'K7_hash_integrity' "oracle bytes mismatch $ob vs $($j.oracle.bytes)" }
  } else { $k7 = $false; Add-Fail 'K7_hash_integrity' "oracle.md not found: $oraclePath" }
} catch { $k7 = $false; Add-Fail 'K7_hash_integrity' "oracle rehash error: $_" }
if ($k7) { Write-Output 'CHECK K7_hash_integrity OK' }

# ---------- K8_open2_redline（禁消费值不得成为阈值） ----------
$k8 = $true
foreach ($tok in @('124248', '124,248', '38175', '38,175', 'consumed_for_forecast')) {
  if ($raw.Contains($tok)) { $k8 = $false; Add-Fail 'K8_open2_redline' "stat_signatures.json 含 OPEN-2 禁消费标记: $tok" }
}
if ($k8) { Write-Output 'CHECK K8_open2_redline OK' }

# ---------- 裁决 ----------
if ($fail.Count -eq 0) {
  Write-Output 'RESULT ALL_CRITERIA_OK'
  exit 0
} else {
  foreach ($f in $fail) { Write-Output "FAIL $f" }
  $first = ($fail[0] -split ' : ')[0]
  Write-Output "RESULT CRITERIA_VIOLATION primary=$first count=$($fail.Count)"
  exit 3
}
