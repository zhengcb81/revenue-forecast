# _run_mutations.ps1 — I-12-A-STAT-SIGN red/green mutation runner (mutations act on COPIES in _mut/Mx only)
# exit legend inherited from _verify_signatures.ps1: 0=ALL_CRITERIA_OK · 1=harness · 2=no verdict · 3=criteria violation (K1..K8)
param(
  [string]$Root = '.planning/2026-09-19-three-project-history-audit/execution_runs/I-12-A-STAT-SIGN/a20260926-01',
  [string]$PlanRoot = '.planning/2026-09-19-three-project-history-audit'
)
$ErrorActionPreference = 'Stop'
$verifier = Join-Path $Root '_verify_signatures.ps1'
$src = Join-Path $Root 'stat_signatures.json'
$origSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $src).Hash.ToLower()
$raw = [System.IO.File]::ReadAllText($src, [System.Text.UTF8Encoding]::new($false))
$mutRoot = Join-Path $Root '_mut'
if (-not (Test-Path -LiteralPath $mutRoot)) { New-Item -ItemType Directory -Path $mutRoot | Out-Null }

function Sha([string]$s) {
  $b = [System.Text.UTF8Encoding]::new($false).GetBytes($s)
  ([BitConverter]::ToString([System.Security.Cryptography.SHA256]::Create().ComputeHash($b)) -replace '-', '').ToLower()
}
function Get-Slice([string]$text, [string]$id, [ref]$start, [ref]$len) {
  $key = '"item_id": "' + $id + '"'
  $i = $text.IndexOf($key); if ($i -lt 0) { throw "id $id not found" }
  $next = $text.IndexOf('"item_id": "', $i + $key.Length); if ($next -lt 0) { $next = $text.Length }
  $start.Value = $i; $len.Value = $next - $i
}
function SliceEdit([string]$text, [string]$id, [string]$old, [string]$newt) {
  $s = 0; $l = 0; Get-Slice $text $id ([ref]$s) ([ref]$l)
  $slice = $text.Substring($s, $l)
  $cnt = ([regex]::Matches($slice, [regex]::Escape($old))).Count
  if ($cnt -ne 1) { throw "expected exactly 1 occurrence of '$old' in $id slice, found $cnt" }
  $newSlice = $slice.Replace($old, $newt)
  return $text.Substring(0, $s) + $newSlice + $text.Substring($s + $l)
}
function Refresh-Hash([string]$text, [string]$id) {
  $s = 0; $l = 0; Get-Slice $text $id ([ref]$s) ([ref]$l)
  $slice = $text.Substring($s, $l)
  $m = [regex]::Match($slice, '"decision_payload_canonical":\s*"([^"]+)"')
  if (-not $m.Success) { throw "payload not found in $id" }
  $newHash = Sha $m.Groups[1].Value
  $m2 = [regex]::Match($slice, '"decision_sha256":\s*"([0-9a-f]{64})"')
  if (-not $m2.Success) { throw "decision_sha256 not found in $id" }
  $newSlice = $slice.Remove($m2.Groups[1].Index, $m2.Groups[1].Length).Insert($m2.Groups[1].Index, $newHash)
  return $text.Substring(0, $s) + $newSlice + $text.Substring($s + $l)
}

$mutations = [ordered]@{
  'M1' = { param($t) (SliceEdit $t 'S1' '"selection": "NOT_SIGNED"' '"selection": "SIGNED"') }
  'M2' = { param($t) (SliceEdit $t 'S3' '"selection": "SIGNED"' '"selection": "NOT_SIGNED"') }
  'M3' = { param($t) $t = (SliceEdit $t 'S3' '"alpha": 0.05' '"alpha": 0.5'); $t = (SliceEdit $t 'S3' 'alpha=0.05' 'alpha=0.50'); (Refresh-Hash $t 'S3') }
  'M4' = { param($t) $t.Replace('"industry_countersign_still_needed": true', '"industry_countersign_still_needed": false') }
  'M5' = { param($t) (SliceEdit $t 'S2' '"selection": "NOT_SIGNED"' '"selection": "SIGNED"') }
  'M6' = { param($t) (SliceEdit $t 'S6' '"selection": "NOT_SIGNED"' '"selection": "SIGNED"') }
  'M7' = { param($t) $t = (SliceEdit $t 'S4' '"repetitions": 10000' '"repetitions": 100'); $t = (SliceEdit $t 'S4' 'repetitions=10000' 'repetitions=100'); (Refresh-Hash $t 'S4') }
  'M8' = { param($t) $t = (SliceEdit $t 'S5' '"method": "holm"' '"method": "bh_fdr"'); $t = (SliceEdit $t 'S5' 'method=holm' 'method=bh_fdr'); (Refresh-Hash $t 'S5') }
}

$results = @()
# ---- GREEN arm: original bytes ----
$greenDir = Join-Path $mutRoot 'GREEN'
if (-not (Test-Path -LiteralPath $greenDir)) { New-Item -ItemType Directory -Path $greenDir | Out-Null }
Copy-Item -LiteralPath $src -Destination (Join-Path $greenDir 'stat_signatures.json') -Force
$gout = & $verifier -Root $greenDir -PlanRoot $PlanRoot 2>&1
$grc = $LASTEXITCODE
$gtext = "=== GREEN (original bytes copy) ===`nrc=$grc`n" + (($gout | ForEach-Object { "$_" }) -join "`n")
Set-Content -LiteralPath (Join-Path $greenDir 'verifier_output.txt') -Value $gtext -Encoding utf8
$results += "GREEN rc=$grc"

# ---- red arms ----
foreach ($id in $mutations.Keys) {
  $dir = Join-Path $mutRoot $id
  if (-not (Test-Path -LiteralPath $dir)) { New-Item -ItemType Directory -Path $dir | Out-Null }
  $mutated = & $mutations[$id] $raw
  $mpath = Join-Path $dir 'stat_signatures.json'
  [System.IO.File]::WriteAllText($mpath, $mutated, [System.Text.UTF8Encoding]::new($false))
  $o = & $verifier -Root $dir -PlanRoot $PlanRoot 2>&1
  $rc = $LASTEXITCODE
  $primary = ($o | Where-Object { "$_" -like 'FAIL *' } | Select-Object -First 1)
  $text = "=== MUTATION $id ===`nrc=$rc`nfirst_fail=$primary`n" + (($o | ForEach-Object { "$_" }) -join "`n")
  Set-Content -LiteralPath (Join-Path $dir 'verifier_output.txt') -Value $text -Encoding utf8
  $results += "$id rc=$rc first_fail=$primary"
}

$afterSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $src).Hash.ToLower()
$results += "original_stat_signatures_unchanged=" + ($origSha -eq $afterSha)
$results += "original_sha256=$origSha"
$results -join "`n"
if ($origSha -ne $afterSha) { exit 1 }
exit 0
