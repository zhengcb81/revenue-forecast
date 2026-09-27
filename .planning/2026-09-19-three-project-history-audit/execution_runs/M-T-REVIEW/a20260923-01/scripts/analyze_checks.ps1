# M-T-REVIEW analysis pass: normalize clause comparisons, emit compact summary + UTF-8 digests file.
# Pure ASCII source. Writes ONLY into this attempt's evidence/ dir.
$ErrorActionPreference = 'Stop'
$HERE = $PSScriptRoot
$ATTEMPT = Split-Path $HERE
$OUT = Join-Path $ATTEMPT 'evidence'
$checks = Get-Content -LiteralPath (Join-Path $OUT 'per_card_checks.json') -Raw -Encoding UTF8 | ConvertFrom-Json

function NumArr($x) {
  if ($null -eq $x) { return $null }
  try { $arr = ($x | ConvertFrom-Json) } catch { return $null }
  $out = @(); foreach ($v in $arr) { $out += [double]$v }
  return , $out
}
function ArrEq($a, $b) {
  if ($null -eq $a -or $null -eq $b) { return $false }
  if ($a.Count -ne $b.Count) { return $false }
  for ($i = 0; $i -lt $a.Count; $i++) { if ([math]::Abs($a[$i] - $b[$i]) -gt 1e-9) { return $false } }
  return $true
}

$lines = New-Object System.Collections.ArrayList
$summary = New-Object System.Collections.ArrayList
[void]$lines.Add('M-T-REVIEW per-card digests (extracted fields; CJK preserved)')
[void]$lines.Add('')

foreach ($row in $checks) {
  $tag = ('{0}/{1} [{2}]' -f $row.card, $row.attempt, $row.kind)
  [void]$lines.Add(('===== ' + $tag + ' ====='))
  if ($row.kind -eq 'M') {
    $specA = NumArr $row.clause.spec_expected_output
    $orcA = NumArr $row.clause.oracle_expected_float
    $hpoA = NumArr $row.clause.handoff_positive_expected
    $exp_ok = (ArrEq $specA $orcA) -and (ArrEq $specA $hpoA)
    $hash_ok = -not ($row.hash_spot | Where-Object { $_.pin_present -and -not $_.match })
    $hash_missing_pin = [bool]($row.hash_spot | Where-Object { -not $_.pin_present })
    $iso_ok = -not ($row.iso_spot | Where-Object { $_.match_binding -eq $false })
    $iso_prod_now_ok = -not ($row.iso_spot | Where-Object { $_.match_prod_now -eq $false })
    $ev_missing = ($row.clause.missing_required_evidence -join ',')
    $neg_ok = ($null -ne $row.clause.negative_total -and $row.clause.negative_total -ge 6 -and $row.clause.negative_total -eq $row.clause.negative_passed)
    [void]$summary.Add([pscustomobject]@{
        card = $row.card; attempt = $row.attempt; kind = $row.kind
        exp_ok = $exp_ok; neg_ok = $neg_ok; ev_missing = $ev_missing
        oracle_before_stdout = $row.mtime.oracle_json_before_stdout
        hash_ok = $hash_ok; hash_missing_pin = $hash_missing_pin
        iso_ok = $iso_ok; iso_prod_now_ok = $iso_prod_now_ok
        qual = ('{0}|{1}|{2}' -f $row.clause.qualification_formula, $row.clause.qualification_disclosure, $row.clause.qualification_accuracy)
        hstatus = $row.handoff_status; rstatus = $row.reviewer_status
        indep = $row.review_has_independent_section; pins = $row.golden_hash_pins_count
      })
    [void]$lines.Add(('mtimes: oracle_md={0} oracle_json={1} stdout={2} oracle_before_stdout={3}' -f $row.mtime.oracle_md, $row.mtime.oracle_json, $row.mtime.stdout, $row.mtime.oracle_json_before_stdout))
    foreach ($h in $row.hash_spot) { [void]$lines.Add(('hash_spot {0}: pin_present={1} match={2} actual={3} pinned={4}' -f $h.file, $h.pin_present, $h.match, $h.actual, $h.pinned)) }
    foreach ($s in $row.iso_spot) { [void]$lines.Add(('iso_spot {0}: match_binding={1} match_prod_now={2} actual={3} prod_now={4}' -f $s.file, $s.match_binding, $s.match_prod_now, $s.actual, $s.production_now)) }
    [void]$lines.Add(('clause: spec_expected={0} oracle_expected={1} handoff_positive={2} exp_ok={3}' -f $row.clause.spec_expected_output, $row.clause.oracle_expected_float, $row.clause.handoff_positive_expected, $exp_ok))
    [void]$lines.Add(('clause: negative={0}/{1} neg_ok={2} missing_evidence=[{3}]' -f $row.clause.negative_passed, $row.clause.negative_total, $neg_ok, $ev_missing))
    [void]$lines.Add(('qual: formula={0} disclosure={1} accuracy={2}; handoff_status={3}; reviewer_status={4}; indep_section={5}; pins={6}' -f $row.clause.qualification_formula, $row.clause.qualification_disclosure, $row.clause.qualification_accuracy, $row.handoff_status, $row.reviewer_status, $row.review_has_independent_section, $row.golden_hash_pins_count))
    foreach ($d in @($row.review_digest)) { [void]$lines.Add(('review: ' + $d)) }
    foreach ($d in @($row.decision_digest)) { [void]$lines.Add(('decision: ' + $d)) }
  }
  elseif ($row.kind -eq 'AUX') {
    [void]$lines.Add(('files: {0}' -f ($row.files_present | ConvertTo-Json -Compress)))
    [void]$lines.Add(('handoff_status={0}; reviewer_status={1}' -f $row.handoff_status, $row.reviewer_status))
    foreach ($d in @($row.review_digest)) { [void]$lines.Add(('review: ' + $d)) }
    foreach ($d in @($row.decision_digest)) { [void]$lines.Add(('decision: ' + $d)) }
    [void]$summary.Add([pscustomobject]@{ card = $row.card; attempt = $row.attempt; kind = 'AUX'; exp_ok = ''; neg_ok = ''; ev_missing = ''; oracle_before_stdout = ''; hash_ok = ''; hash_missing_pin = ''; iso_ok = ''; iso_prod_now_ok = ''; qual = ''; hstatus = $row.handoff_status; rstatus = $row.reviewer_status; indep = ''; pins = '' })
  }
  else {
    [void]$lines.Add(('files: {0}' -f ($row.files_present | ConvertTo-Json -Compress)))
    [void]$lines.Add(('mtime: {0}' -f ($row.mtime | ConvertTo-Json -Compress)))
    [void]$lines.Add(('handoff: {0}' -f ($row.handoff_digest | ConvertTo-Json -Compress)))
    foreach ($p in $row.verification_jsons.PSObject.Properties) {
      [void]$lines.Add(('verif {0}: sha={1} keys={2}' -f $p.Name, $p.Value.sha256, ($p.Value.keys -join ',')))
    }
    [void]$lines.Add(('pins={0}' -f $row.golden_hash_pins_count))
    foreach ($d in @($row.decision_digest)) { [void]$lines.Add(('decision: ' + $d)) }
    [void]$summary.Add([pscustomobject]@{ card = $row.card; attempt = $row.attempt; kind = 'T1'; exp_ok = ''; neg_ok = ''; ev_missing = ''; oracle_before_stdout = ''; hash_ok = ''; hash_missing_pin = ''; iso_ok = ''; iso_prod_now_ok = ''; qual = ''; hstatus = ('{0}' -f $row.handoff_digest.status); rstatus = ('{0}' -f $row.handoff_digest.reviewer_status); indep = ''; pins = $row.golden_hash_pins_count })
  }
  [void]$lines.Add('')
}

$utf8 = New-Object System.Text.UTF8Encoding($false)
[System.IO.File]::WriteAllText((Join-Path $OUT 'digests.txt'), ($lines -join "`r`n") + "`r`n", $utf8)
$summary | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath (Join-Path $OUT 'clause_compare.json') -Encoding UTF8

# compact ASCII table to stdout
Write-Output ('card,attempt,kind,exp_ok,neg_ok,ev_missing,oracle_before_stdout,hash_ok,hash_missing_pin,iso_ok,iso_prod_now_ok,hstatus,rstatus,indep,pins')
foreach ($s in $summary) {
  Write-Output ('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11},{12},{13},{14}' -f $s.card, $s.attempt, $s.kind, $s.exp_ok, $s.neg_ok, $s.ev_missing, $s.oracle_before_stdout, $s.hash_ok, $s.hash_missing_pin, $s.iso_ok, $s.iso_prod_now_ok, $s.hstatus, $s.rstatus, $s.indep, $s.pins)
}
