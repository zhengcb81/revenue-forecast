# REM-21 / batch M09-M12 -- run every arm as a REAL child process and record the RAW rc.
#
#   E     new runner  frozen cases.json               (green control)
#   F     new runner  NEG-CARD expected=ValueError    (the deliverable mutation arm)
#   B     OLD runner  same bytes as F                 (inertness control)
#   G     new runner  NEG-CARD expected key deleted   (rc=2 declaration gate)
#   F2    new runner  CONT-BREAK expected=ValueError  (cross-check: lexicographically lowest id)
#   Gpre  OLD runner  same bytes as G                 (pre-fix rc classification for a missing key)
#
# Every card of the batch M09..M12 is run for every arm.  The child's rc is read from
# $LASTEXITCODE immediately after the call, seeded beforehand with an impossible sentinel so that
# a stale value can never be mistaken for a measurement.
#
# Windows PowerShell 5.1 (Desktop) compatible: no pwsh-only syntax.

param(
  [Parameter(Mandatory = $true)][string]$Interp,
  [Parameter(Mandatory = $true)][string]$Attempt
)

$ErrorActionPreference = 'Continue'
$SENTINEL = 2147483647
$SCRATCH = Join-Path $Attempt '_scratch\M09-M12'
$NEW = Join-Path $Attempt 'M09-M12\run_card.py'
$OLD = Join-Path $Attempt 'M09-M12\run_card_before.py'
$CODEROOT = Join-Path $SCRATCH 'code_root'
$UTF8NOBOM = New-Object System.Text.UTF8Encoding($false)

function Write-Text([string]$path, [string]$text) {
  [System.IO.File]::WriteAllText($path, $text, $UTF8NOBOM)
}

$arms = @(
  (New-Object PSObject -Property @{ name = 'E';    runner = $NEW; label = 'new runner, frozen cases (green control)' }),
  (New-Object PSObject -Property @{ name = 'F';    runner = $NEW; label = 'new runner, NEG-CARD expected->ValueError' }),
  (New-Object PSObject -Property @{ name = 'B';    runner = $OLD; label = 'OLD runner, same mutated bytes as F' }),
  (New-Object PSObject -Property @{ name = 'G';    runner = $NEW; label = 'new runner, NEG-CARD expected key deleted' }),
  (New-Object PSObject -Property @{ name = 'F2';   runner = $NEW; label = 'new runner, CONT-BREAK expected->ValueError' }),
  (New-Object PSObject -Property @{ name = 'Gpre'; runner = $OLD; label = 'OLD runner, same bytes as G' })
)
$cards = @('M09', 'M10', 'M11', 'M12')
$results = New-Object System.Collections.ArrayList

foreach ($arm in $arms) {
  foreach ($card in $cards) {
    $armRoot = Join-Path $SCRATCH $arm.name
    $outDir = Join-Path $armRoot $card
    New-Item -ItemType Directory -Force -Path $outDir | Out-Null
    $outJson = Join-Path $outDir 'run_result.json'
    $stdoutTxt = Join-Path $outDir 'stdout.txt'
    # Remove every previous output first: a crashed child writes nothing, so a leftover file from
    # an earlier run must never be mistaken for this run's product.
    foreach ($f in @('run_result.json', 'formula_result.json', 'negative_results.json',
                     'stdout.txt', 'stderr.txt', 'console.txt')) {
      $p = Join-Path $outDir $f
      if (Test-Path -LiteralPath $p) { Remove-Item -LiteralPath $p -Force }
    }
    $global:LASTEXITCODE = $SENTINEL
    $startedUtc = (Get-Date).ToUniversalTime()
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $txt = & $Interp -X utf8 -B $arm.runner `
      --card $card `
      --attempt $armRoot `
      --code-root $CODEROOT `
      --out $outJson `
      --formula-out (Join-Path $outDir 'formula_result.json') `
      --negative-out (Join-Path $outDir 'negative_results.json') `
      --stdout-out $stdoutTxt `
      --stderr-out (Join-Path $outDir 'stderr.txt') 2>&1 | Out-String
    $rc = $global:LASTEXITCODE
    $sw.Stop()
    if ($rc -eq $SENTINEL) { throw "rc sentinel survived (child never produced an exit code): $($arm.name)/$card" }
    Write-Text (Join-Path $outDir 'console.txt') $txt
    $outWritten = Test-Path -LiteralPath $outJson
    $null = $results.Add((New-Object PSObject -Property @{
          arm            = $arm.name
          card           = $card
          rc             = [int]$rc
          runner         = $arm.runner
          runner_sha256  = (Get-FileHash -Algorithm SHA256 -LiteralPath $arm.runner).Hash.ToLower()
          arm_root       = $armRoot
          started_utc    = $startedUtc.ToString('o')
          elapsed_ms     = $sw.ElapsedMilliseconds
          out_json_written = $outWritten
          out_json_bytes = if ($outWritten) { (Get-Item -LiteralPath $outJson).Length } else { $null }
          out_json_mtime_utc = if ($outWritten) { (Get-Item -LiteralPath $outJson).LastWriteTimeUtc.ToString('o') } else { $null }
          stdout_txt_written = (Test-Path -LiteralPath $stdoutTxt)
          outputs_fresh  = ($outWritten -and ((Get-Item -LiteralPath $outJson).LastWriteTimeUtc -ge $startedUtc))
          label          = $arm.label
        }))
    Write-Output ("{0,-4} {1} rc={2} ms={3} out={4}" -f $arm.name, $card, $rc, $sw.ElapsedMilliseconds, $(if ($outWritten) { 'written' } else { 'ABSENT' }))
  }
}

$doc = New-Object PSObject -Property @{
  interpreter     = $Interp
  interpreter_sha = (Get-FileHash -Algorithm SHA256 -LiteralPath $Interp).Hash.ToLower()
  code_root       = $CODEROOT
  cwd_policy      = 'each child runs with the inherited cwd; --attempt/--code-root/--out are absolute'
  rc_sentinel     = $SENTINEL
  run_count       = $results.Count
  runs            = $results
  rc_histogram    = ($results | Group-Object rc | ForEach-Object { New-Object PSObject -Property @{ rc = [int]$_.Name; n = $_.Count } })
}
Write-Text (Join-Path $SCRATCH '_tools\raw_rc.json') ($doc | ConvertTo-Json -Depth 6)
Write-Output "wrote raw_rc.json ($($results.Count) runs)"
