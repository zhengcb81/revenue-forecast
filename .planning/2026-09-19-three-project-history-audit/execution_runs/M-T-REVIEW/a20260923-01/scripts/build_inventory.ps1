# M-T-REVIEW inventory + sampled-verification checks (read-only over all reviewed attempts)
# Pure ASCII on purpose: PS 5.1 reads no-BOM scripts as ANSI, which breaks CJK literals.
# CJK matching uses regex \uXXXX escapes. Writes ONLY into this attempt's evidence/ dir.
$ErrorActionPreference = 'Stop'
$HERE = $PSScriptRoot                       # ...\M-T-REVIEW\a20260923-01\scripts
$ATTEMPT = Split-Path $HERE                 # ...\M-T-REVIEW\a20260923-01
$MTREV = Split-Path $ATTEMPT                # ...\M-T-REVIEW
$RUNS = Split-Path $MTREV                   # ...\execution_runs
$PLAN = Split-Path $RUNS                    # plan root
$V2 = Join-Path $PLAN 'execution_v2'
$REPO = Split-Path (Split-Path $PLAN)       # revenue-forecast repo root
$OUT = Join-Path $ATTEMPT 'evidence'

function Sha256([string]$p) { if (Test-Path -LiteralPath $p) { (Get-FileHash -Algorithm SHA256 -LiteralPath $p).Hash.ToLower() } else { $null } }
function Mt([string]$p) { if (Test-Path -LiteralPath $p) { (Get-Item -LiteralPath $p).LastWriteTimeUtc.ToString('yyyy-MM-ddTHH:mm:ssZ') } else { $null } }
function ReadJson([string]$p) { try { Get-Content -LiteralPath $p -Raw -Encoding UTF8 | ConvertFrom-Json } catch { $null } }
# CJK helpers (regex escapes): 期望输出 \u671f\u671b\u8f93\u51fa ;  结论 \u7ed3\u8bba ;  裁决 \u88c1\u51b3 ;  裁定 \u88c1\u5b9a ;
#   资格 \u8d44\u683c ;  独立 \u72ec\u7acb ;  审查 \u5ba1\u67e5 ;  点复审 \u70b9\u590d\u5ba1
$RE_DIGEST = '^(#{1,4} )|\u7ed3\u8bba|verdict|accepted|changes_required|blocked|not_applicable|\u88c1\u51b3|\u88c1\u5b9a|\u8d44\u683c'
$RE_EXPECT = '\u671f\u671b\u8f93\u51fa\uff1a`(\[[^\]]*\])`'
$RE_INDEP  = '\u72ec\u7acb reviewer|\u72ec\u7acb\u5ba1\u67e5|\u70b9\u590d\u5ba1'

function Digest([string]$p, [int]$n) {
  if (-not (Test-Path -LiteralPath $p)) { return @() }
  $lines = Get-Content -LiteralPath $p -Encoding UTF8
  $hits = @()
  for ($i = 0; $i -lt $lines.Count -and $hits.Count -lt $n; $i++) {
    $L = $lines[$i]
    if ($L -match $RE_DIGEST) {
      $hits += ('{0}: {1}' -f ($i + 1), $L.Substring(0, [Math]::Min(200, $L.Length)))
    }
  }
  return , $hits
}

$inventory = New-Object System.Collections.ArrayList
$checks = New-Object System.Collections.ArrayList

# ---------- M cards ----------
foreach ($num in 1..31) {
  $cid = 'M{0:d2}' -f $num
  $specPath = Join-Path $V2 ('card_' + $cid + '.md')
  $specExpected = $null
  $specSha = Sha256 $specPath
  if (Test-Path -LiteralPath $specPath) {
    $specText = Get-Content -LiteralPath $specPath -Raw -Encoding UTF8
    if ($specText -match $RE_EXPECT) { $specExpected = $Matches[1] }
  }
  $cardDir = Join-Path $RUNS $cid
  $attempts = @()
  if (Test-Path -LiteralPath $cardDir) { $attempts = @(Get-ChildItem -Directory $cardDir | Select-Object -ExpandProperty Name) }
  [void]$inventory.Add([pscustomobject]@{ card = $cid; spec_path = ('execution_v2/card_' + $cid + '.md'); spec_sha256 = $specSha; spec_expected_output = $specExpected; attempts = $attempts })

  foreach ($att in $attempts) {
    $AD = Join-Path $cardDir $att
    $evDir = Join-Path (Join-Path $AD 'evidence') $cid
    $handoff = ReadJson (Join-Path $AD 'handoff.json')
    $binding = ReadJson (Join-Path $AD 'binding.json')
    $oracleJson = ReadJson (Join-Path $evDir 'oracle.json')
    $qual = ReadJson (Join-Path $evDir 'qualification.json')

    # (a) mtime ordering
    $mtOracleMd = Mt (Join-Path $AD 'oracle.md')
    $mtOracleJs = Mt (Join-Path $evDir 'oracle.json')
    $mtStdout = Mt (Join-Path $evDir 'stdout.txt')
    $mtReview = Mt (Join-Path $AD 'review.md')
    $oracle_before_stdout = ($null -ne $mtOracleJs -and $null -ne $mtStdout -and $mtOracleJs -lt $mtStdout)

    # (b) hash spot (fixed sample frozen in oracle.md): input/oracle/cases vs handoff pins
    $pinMap = @{ 'input.json' = 'evidence_input_json'; 'oracle.json' = 'evidence_oracle_json'; 'cases.json' = 'evidence_cases_json' }
    $hashSpot = @()
    foreach ($f in @('input.json', 'oracle.json', 'cases.json')) {
      $actual = Sha256 (Join-Path $evDir $f)
      $pinned = $null
      if ($handoff -and $handoff.input_hashes) { $pinned = $handoff.input_hashes.($pinMap[$f]) }
      $hashSpot += [pscustomobject]@{ file = ('evidence/' + $cid + '/' + $f); actual = $actual; pinned = $pinned; pin_present = ($null -ne $pinned); match = ($null -ne $actual -and $null -ne $pinned -and $actual -eq $pinned) }
    }
    $isoSpot = @()
    if ($binding) {
      foreach ($k in @('iso/checkout_scripts/model_registry.py', 'iso/checkout_scripts/model_extensions.py')) {
        $actual = Sha256 (Join-Path $AD $k)
        $bp = $null; if ($binding.isolated_copy_hashes) { $bp = $binding.isolated_copy_hashes.$k }
        $prodKey = $k -replace '^iso/checkout_scripts/', 'scripts/'
        $prodPin = $null; if ($binding.production_source_hashes) { $prodPin = $binding.production_source_hashes.$prodKey }
        $prodNow = Sha256 (Join-Path $REPO $prodKey)
        $isoSpot += [pscustomobject]@{ file = $k; actual = $actual; binding_pin = $bp; binding_prod_pin = $prodPin; production_now = $prodNow; match_binding = ($null -ne $actual -and $null -ne $bp -and $actual -eq $bp); match_prod_now = ($null -ne $prodNow -and $null -ne $actual -and $actual -eq $prodNow) }
      }
    }

    # (c) headline clause spots
    $oracleExpected = $null
    if ($oracleJson -and $oracleJson.PSObject.Properties['expected_float']) { $oracleExpected = ($oracleJson.expected_float | ConvertTo-Json -Compress) }
    $handoffPositive = $null
    if ($handoff -and $handoff.PSObject.Properties['positive_expected']) { $handoffPositive = ($handoff.positive_expected | ConvertTo-Json -Compress) }
    $negTotal = $null; $negPassed = $null
    if ($handoff -and $handoff.PSObject.Properties['negative_case_summary']) { $negTotal = $handoff.negative_case_summary.total; $negPassed = $handoff.negative_case_summary.passed }
    $reqEvidence = @('input.json', 'oracle.json', 'source_manifest.json', 'command_manifest.json', 'stdout.txt', 'stderr.txt', 'formula_result.json', 'negative_results.json', 'qualification.json')
    $missingEvidence = @($reqEvidence | Where-Object { -not (Test-Path -LiteralPath (Join-Path $evDir $_)) })
    $qualFormula = $null; $qualDA = $null; $qualAcc = $null
    if ($qual) {
      if ($qual.PSObject.Properties['formula']) { $qualFormula = ('{0}' -f $qual.formula.status) }
      if ($qual.PSObject.Properties['disclosure_adaptation']) { $qualDA = ('{0}' -f $qual.disclosure_adaptation.status) }
      if ($qual.PSObject.Properties['accuracy']) { $qualAcc = ('{0}' -f $qual.accuracy.status) }
    }

    # (d) golden-hash pin family + verdict extraction
    $pinCount = 0
    foreach ($f in @('binding.json', 'handoff.json')) {
      $p = Join-Path $AD $f
      if (Test-Path -LiteralPath $p) { $pinCount += ([regex]::Matches((Get-Content -LiteralPath $p -Raw), '[0-9a-f]{64}')).Count }
    }
    $rp = Join-Path $AD 'review.md'
    $reviewHasIndep = $false
    if (Test-Path -LiteralPath $rp) { $rt = Get-Content -LiteralPath $rp -Raw -Encoding UTF8; $reviewHasIndep = [bool]($rt -match $RE_INDEP) }
    $hStatus = $null; $rStatus = $null
    if ($handoff) {
      if ($handoff.PSObject.Properties['status']) { $hStatus = ('{0}' -f $handoff.status) }
      if ($handoff.PSObject.Properties['reviewer_status']) { $rStatus = ('{0}' -f $handoff.reviewer_status) }
    }

    [void]$checks.Add([pscustomobject]@{
        card = $cid; attempt = $att; kind = 'M'
        files_present = [pscustomobject]@{
          binding = (Test-Path -LiteralPath (Join-Path $AD 'binding.json')); decision = (Test-Path -LiteralPath (Join-Path $AD 'decision.md'))
          commands = (Test-Path -LiteralPath (Join-Path $AD 'commands.json')); oracle_md = (Test-Path -LiteralPath (Join-Path $AD 'oracle.md'))
          review = (Test-Path -LiteralPath $rp); handoff = (Test-Path -LiteralPath (Join-Path $AD 'handoff.json'))
          changes = (Test-Path -LiteralPath (Join-Path $AD 'changes.diff'))
        }
        mtime = [pscustomobject]@{ oracle_md = $mtOracleMd; oracle_json = $mtOracleJs; stdout = $mtStdout; review_md = $mtReview; oracle_json_before_stdout = $oracle_before_stdout }
        hash_spot = $hashSpot
        iso_spot = $isoSpot
        clause = [pscustomobject]@{
          spec_expected_output = $specExpected; oracle_expected_float = $oracleExpected; handoff_positive_expected = $handoffPositive
          negative_total = $negTotal; negative_passed = $negPassed
          missing_required_evidence = $missingEvidence
          qualification_formula = $qualFormula; qualification_disclosure = $qualDA; qualification_accuracy = $qualAcc
        }
        golden_hash_pins_count = $pinCount
        handoff_status = $hStatus; reviewer_status = $rStatus
        review_has_independent_section = $reviewHasIndep
        review_digest = (Digest $rp 14)
        decision_digest = (Digest (Join-Path $AD 'decision.md') 8)
      })
  }
}

# ---------- auxiliary batch dirs ----------
foreach ($aux in @('M01-M04-PROPAGATE', 'M05-M08', 'M17-M20')) {
  $AD = Join-Path $RUNS $aux
  if (-not (Test-Path -LiteralPath $AD)) { continue }
  foreach ($att in @(Get-ChildItem -Directory $AD | Select-Object -ExpandProperty Name)) {
    $AAD = Join-Path $AD $att
    $hStatus = $null; $rStatus = $null
    $handoff = ReadJson (Join-Path $AAD 'handoff.json')
    if ($handoff) {
      if ($handoff.PSObject.Properties['status']) { $hStatus = ('{0}' -f $handoff.status) }
      if ($handoff.PSObject.Properties['reviewer_status']) { $rStatus = ('{0}' -f $handoff.reviewer_status) }
    }
    [void]$checks.Add([pscustomobject]@{
        card = $aux; attempt = $att; kind = 'AUX'
        files_present = [pscustomobject]@{ decision = (Test-Path -LiteralPath (Join-Path $AAD 'decision.md')); handoff = (Test-Path -LiteralPath (Join-Path $AAD 'handoff.json')); review = (Test-Path -LiteralPath (Join-Path $AAD 'review.md')); binding = (Test-Path -LiteralPath (Join-Path $AAD 'binding.json')) }
        handoff_status = $hStatus; reviewer_status = $rStatus
        review_digest = (Digest (Join-Path $AAD 'review.md') 10)
        decision_digest = (Digest (Join-Path $AAD 'decision.md') 8)
      })
  }
}

# ---------- T1 cards ----------
foreach ($t in @(Get-ChildItem -Directory $RUNS | Where-Object Name -like 'T1*')) {
  foreach ($att in @(Get-ChildItem -Directory $t.FullName | Select-Object -ExpandProperty Name)) {
    $AD = Join-Path $t.FullName $att
    $handoff = ReadJson (Join-Path $AD 'handoff.json')
    $verifFiles = @(Get-ChildItem -File $AD -Filter '*.json' | Where-Object { $_.Name -notin @('handoff.json', 'commands.json', 'binding.json') } | Select-Object -ExpandProperty Name)
    $verifDigests = @{}
    foreach ($vf in $verifFiles) {
      $j = ReadJson (Join-Path $AD $vf)
      $keys = @(); if ($j) { $keys = @($j.PSObject.Properties | Select-Object -ExpandProperty Name) }
      $verifDigests[$vf] = @{ sha256 = (Sha256 (Join-Path $AD $vf)); keys = $keys }
    }
    $hdig = [pscustomobject]@{}
    if ($handoff) {
      $props = @{}
      foreach ($k in @('card_id', 'status', 'reviewer_status', 'next_action', 'verdict', 'blocked_by')) {
        if ($handoff.PSObject.Properties[$k]) { $props[$k] = ('{0}' -f $handoff.$k) }
      }
      $hdig = [pscustomobject]$props
    }
    $pinCount = 0
    foreach ($f in @(Get-ChildItem -File $AD -Filter '*.json')) { $pinCount += ([regex]::Matches((Get-Content -LiteralPath $f.FullName -Raw), '[0-9a-f]{64}')).Count }
    [void]$checks.Add([pscustomobject]@{
        card = $t.Name; attempt = $att; kind = 'T1'
        files_present = [pscustomobject]@{ decision = (Test-Path -LiteralPath (Join-Path $AD 'decision.md')); handoff = (Test-Path -LiteralPath (Join-Path $AD 'handoff.json')) }
        mtime = [pscustomobject]@{ decision_md = (Mt (Join-Path $AD 'decision.md')); handoff_json = (Mt (Join-Path $AD 'handoff.json')) }
        verification_jsons = $verifDigests
        handoff_digest = $hdig
        golden_hash_pins_count = $pinCount
        decision_digest = (Digest (Join-Path $AD 'decision.md') 14)
      })
  }
}

$inventory | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OUT 'inventory.json') -Encoding UTF8
$checks | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OUT 'per_card_checks.json') -Encoding UTF8
Write-Output ('inventory cards: {0}; check rows: {1}' -f $inventory.Count, $checks.Count)
