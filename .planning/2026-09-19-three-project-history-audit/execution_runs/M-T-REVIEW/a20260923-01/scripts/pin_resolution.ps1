# M-T-REVIEW pin resolution (both handoff key styles + evidence_hashes.json), changes.diff
# scope check, negative results fallback, mtime mass-rewrite probe. Pure ASCII.
$ErrorActionPreference = 'Stop'
$HERE = $PSScriptRoot
$ATTEMPT = Split-Path $HERE
$MTREV = Split-Path $ATTEMPT
$RUNS = Split-Path $MTREV
$PLAN = Split-Path $RUNS
$OUT = Join-Path $ATTEMPT 'evidence'

$sha = [System.Security.Cryptography.SHA256]::Create()
function HashBytes([byte[]]$b) { return (($sha.ComputeHash($b) | ForEach-Object { $_.ToString('x2') }) -join '') }
function RawHash([string]$p) { if (Test-Path -LiteralPath $p) { return HashBytes ([IO.File]::ReadAllBytes($p)) } return $null }
function CrlfHash([string]$p) {
  if (-not (Test-Path -LiteralPath $p)) { return $null }
  $t = [IO.File]::ReadAllText($p)
  return HashBytes ([Text.Encoding]::UTF8.GetBytes(($t -replace "(?<!`r)`n", "`r`n")))
}
function ReadJson([string]$p) { try { Get-Content -LiteralPath $p -Raw -Encoding UTF8 | ConvertFrom-Json } catch { $null } }

$rows = New-Object System.Collections.ArrayList
foreach ($num in 1..31) {
  $cid = 'M{0:d2}' -f $num
  foreach ($att in @(Get-ChildItem -Directory (Join-Path $RUNS $cid) | Select-Object -ExpandProperty Name)) {
    $AD = Join-Path (Join-Path $RUNS $cid) $att
    $evDir = Join-Path (Join-Path $AD 'evidence') $cid
    $handoff = ReadJson (Join-Path $AD 'handoff.json')
    $evHashes = ReadJson (Join-Path $evDir 'evidence_hashes.json')

    $fileRows = @()
    foreach ($f in @('input.json', 'oracle.json', 'cases.json')) {
      $rel = ('evidence/{0}/{1}' -f $cid, $f)
      $pin = $null; $pinSrc = $null
      if ($handoff -and $handoff.PSObject.Properties['input_hashes']) {
        $ih = $handoff.input_hashes
        foreach ($k in @($rel, $f, ('evidence_' + $f.Replace('.json', '_json')))) {
          $prop = $ih.PSObject.Properties[$k]
          if ($prop -and $prop.Value -and ("$($prop.Value)" -match '^[0-9a-f]{64}$')) { $pin = "$($prop.Value)"; $pinSrc = ('handoff.input_hashes[{0}]' -f $k); break }
        }
      }
      if (-not $pin -and $evHashes -and $evHashes.PSObject.Properties['files']) {
        $prop = $evHashes.files.PSObject.Properties[$rel]
        if ($prop -and $prop.Value) { $pin = "$($prop.Value)"; $pinSrc = 'evidence_hashes.json.files' }
      }
      $p = Join-Path $evDir $f
      $raw = RawHash $p; $cr = CrlfHash $p
      $fileRows += [pscustomobject]@{
        file = $rel; pin = $pin; pin_source = $pinSrc
        raw = $raw; crlf_variant = $cr
        match_raw = ($null -ne $pin -and $raw -eq $pin); match_crlf = ($null -ne $pin -and $cr -eq $pin)
      }
    }

    # changes.diff scope: does it touch production paths?
    $diffScope = $null
    $dp = Join-Path $AD 'changes.diff'
    if (Test-Path -LiteralPath $dp) {
      $dt = Get-Content -LiteralPath $dp -Raw -Encoding UTF8
      $prodHits = @([regex]::Matches($dt, 'diff --git a/(\S+)') | ForEach-Object { $_.Groups[1].Value } | Where-Object { $_ -notmatch '^(\.planning|execution_runs|iso/|evidence/|scripts/oracle_|scripts/run_card|scripts/)' })
      $diffScope = [pscustomobject]@{ bytes = (Get-Item -LiteralPath $dp).Length; paths = @([regex]::Matches($dt, 'diff --git a/(\S+)') | ForEach-Object { $_.Groups[1].Value } | Select-Object -First 8); possible_product_paths = $prodHits }
    }

    # negatives fallback from negative_results.json
    $negTotal = $null; $negPassed = $null; $negSrc = 'handoff'
    if ($handoff -and $handoff.PSObject.Properties['negative_case_summary'] -and $handoff.negative_case_summary.total) {
      $negTotal = $handoff.negative_case_summary.total; $negPassed = $handoff.negative_case_summary.passed
    }
    else {
      $nr = ReadJson (Join-Path $evDir 'negative_results.json')
      if ($nr) {
        $negSrc = 'negative_results.json'
        if ($nr.PSObject.Properties['cases']) { $negTotal = @($nr.cases).Count; $negPassed = @($nr.cases | Where-Object { $_.verdict -eq 'PASS_rejected' -or $_.passed -eq $true -or $_.ok -eq $true }).Count }
        elseif ($nr.PSObject.Properties['total']) { $negTotal = $nr.total; $negPassed = $nr.passed }
        else { $negTotal = @($nr.PSObject.Properties).Count; $negSrc = 'negative_results.json(keycount)' }
      }
    }

    # mtime mass-rewrite probe: count files in attempt with mtime on 2026-09-20
    $all = Get-ChildItem $AD -Recurse -File -ErrorAction SilentlyContinue | Where-Object { $_.FullName -notmatch 'venv|site-packages|__pycache__' }
    $sep20 = @($all | Where-Object { $_.LastWriteTimeUtc.ToString('yyyy-MM-dd') -eq '2026-09-20' }).Count

    [void]$rows.Add([pscustomobject]@{
        card = $cid; attempt = $att
        files = $fileRows
        all_pins_resolved = -not ($fileRows | Where-Object { $null -eq $_.pin })
        all_pins_reproduced = -not ($fileRows | Where-Object { -not ($_.match_raw -or $_.match_crlf) })
        crlf_only_count = @($fileRows | Where-Object { $_.match_crlf -and -not $_.match_raw }).Count
        changes_diff = $diffScope
        negative_total = $negTotal; negative_passed = $negPassed; negative_src = $negSrc
        file_count = @($all).Count; files_touched_0920 = $sep20
      })
  }
}

$rows | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $OUT 'pin_resolution.json') -Encoding UTF8
Write-Output 'card,attempt,pins_resolved,pins_reproduced,crlf_only,diff_bytes,diff_prod_paths,neg_total,neg_passed,neg_src,files,touched_0920'
foreach ($r in $rows) {
  $dp = 'NA'; if ($r.changes_diff) { $dp = ($r.changes_diff.possible_product_paths -join '|') }
  $db = 'NA'; if ($r.changes_diff) { $db = $r.changes_diff.bytes }
  Write-Output ('{0},{1},{2},{3},{4},{5},{6},{7},{8},{9},{10},{11}' -f $r.card, $r.attempt, $r.all_pins_resolved, $r.all_pins_reproduced, $r.crlf_only_count, $db, $dp, $r.negative_total, $r.negative_passed, $r.negative_src, $r.file_count, $r.files_touched_0920)
}
