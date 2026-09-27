# M-T-REVIEW hash re-attribution + oracle-expected re-extraction.
# For each M attempt: raw and CRLF-variant hashes of input/oracle/cases vs handoff pins;
# oracle expected values from candidate JSON paths; numeric compare vs spec.
# Pure ASCII. Writes ONLY into this attempt's evidence/ dir.
$ErrorActionPreference = 'Stop'
$HERE = $PSScriptRoot
$ATTEMPT = Split-Path $HERE
$MTREV = Split-Path $ATTEMPT
$RUNS = Split-Path $MTREV
$PLAN = Split-Path $RUNS
$V2 = Join-Path $PLAN 'execution_v2'
$OUT = Join-Path $ATTEMPT 'evidence'

$sha = [System.Security.Cryptography.SHA256]::Create()
function HashBytes([byte[]]$b) { return (($sha.ComputeHash($b) | ForEach-Object { $_.ToString('x2') }) -join '') }
function RawHash([string]$p) { if (Test-Path -LiteralPath $p) { return HashBytes ([IO.File]::ReadAllBytes($p)) } return $null }
function CrlfHash([string]$p) {
  if (-not (Test-Path -LiteralPath $p)) { return $null }
  $t = [IO.File]::ReadAllText($p)
  $c = $t -replace "(?<!`r)`n", "`r`n"
  return HashBytes ([Text.Encoding]::UTF8.GetBytes($c))
}
function ReadJson([string]$p) { try { Get-Content -LiteralPath $p -Raw -Encoding UTF8 | ConvertFrom-Json } catch { $null } }
function NumArr($x) {
  if ($null -eq $x) { return $null }
  $a = @(); foreach ($v in @($x)) { try { $a += [double]$v } catch { return $null } }
  return , $a
}
function ArrEq($a, $b) {
  if ($null -eq $a -or $null -eq $b) { return $false }
  if ($a.Count -ne $b.Count) { return $false }
  for ($i = 0; $i -lt $a.Count; $i++) { if ([math]::Abs($a[$i] - $b[$i]) -gt 1e-9) { return $false } }
  return $true
}

$rows = New-Object System.Collections.ArrayList
foreach ($num in 1..31) {
  $cid = 'M{0:d2}' -f $num
  $specPath = Join-Path $V2 ('card_' + $cid + '.md')
  $specExpected = $null
  if (Test-Path -LiteralPath $specPath) {
    $specText = Get-Content -LiteralPath $specPath -Raw -Encoding UTF8
    if ($specText -match '\u671f\u671b\u8f93\u51fa\uff1a`(\[[^\]]*\])`') { $specExpected = $Matches[1] }
  }
  $specA = $null
  if ($specExpected) { try { $specA = NumArr @(($specExpected | ConvertFrom-Json)) } catch { $specA = $null } }

  foreach ($att in @(Get-ChildItem -Directory (Join-Path $RUNS $cid) | Select-Object -ExpandProperty Name)) {
    $AD = Join-Path (Join-Path $RUNS $cid) $att
    $evDir = Join-Path (Join-Path $AD 'evidence') $cid
    $handoff = ReadJson (Join-Path $AD 'handoff.json')
    $oracleJson = ReadJson (Join-Path $evDir 'oracle.json')

    # hash re-attribution
    $pinMap = @{ 'input.json' = 'evidence_input_json'; 'oracle.json' = 'evidence_oracle_json'; 'cases.json' = 'evidence_cases_json' }
    $hashRows = @()
    foreach ($f in @('input.json', 'oracle.json', 'cases.json')) {
      $p = Join-Path $evDir $f
      $raw = RawHash $p; $cr = CrlfHash $p
      $pin = $null
      if ($handoff -and $handoff.PSObject.Properties['input_hashes']) { $pin = $handoff.input_hashes.($pinMap[$f]) }
      $hashRows += [pscustomobject]@{ file = $f; pinned = $pin; raw = $raw; crlf_variant = $cr; match_raw = ($null -ne $pin -and $raw -eq $pin); match_crlf = ($null -ne $pin -and $cr -eq $pin) }
    }

    # oracle expected extraction from candidate paths
    $orcA = $null; $orcPath = $null
    $candidates = @(
      @{ p = 'positive.expected_float'; v = $(if ($oracleJson -and $oracleJson.positive) { $oracleJson.positive.PSObject.Properties['expected_float'].Value } else { $null }) },
      @{ p = 'positive.expected'; v = $(if ($oracleJson -and $oracleJson.positive) { $oracleJson.positive.PSObject.Properties['expected'].Value } else { $null }) },
      @{ p = 'expected_float'; v = $(if ($oracleJson) { $oracleJson.PSObject.Properties['expected_float'].Value } else { $null }) },
      @{ p = 'positive.expected_floats'; v = $(if ($oracleJson -and $oracleJson.positive) { $oracleJson.positive.PSObject.Properties['expected_floats'].Value } else { $null }) }
    )
    foreach ($c in $candidates) {
      if ($null -ne $c.v) { $orcA = NumArr $c.v; $orcPath = $c.p; break }
    }
    $hpoA = $null
    if ($handoff -and $handoff.PSObject.Properties['positive_expected']) { $hpoA = NumArr $handoff.positive_expected }
    $exp_ok = ((ArrEq $specA $orcA) -and (ArrEq $specA $hpoA))

    [void]$rows.Add([pscustomobject]@{
        card = $cid; attempt = $att
        spec_expected = $specExpected; oracle_expected_path = $orcPath; oracle_expected = ($orcA -join ','); handoff_positive = ($hpoA -join ','); exp_ok = $exp_ok
        hash = $hashRows
        all_pins_reproduced = -not ($hashRows | Where-Object { -not ($_.match_raw -or $_.match_crlf) })
        crlf_normalized_count = @($hashRows | Where-Object { $_.match_crlf -and -not $_.match_raw }).Count
      })
  }
}

$rows | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OUT 'hash_reattribution.json') -Encoding UTF8
Write-Output 'card,attempt,exp_ok,spec,oracle_path,oracle,handoff,pins_reproduced,crlf_norm_files'
foreach ($r in $rows) {
  Write-Output ('{0},{1},{2},{3},{4},{5},{6},{7},{8}' -f $r.card, $r.attempt, $r.exp_ok, $r.spec_expected, $r.oracle_expected_path, $r.oracle_expected, $r.handoff_positive, $r.all_pins_reproduced, $r.crlf_normalized_count)
}
