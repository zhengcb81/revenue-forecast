# I-14-E: M-B steps only (node-level bands).  Split out because the first campaign run
# passed the repo path as a non-ASCII PowerShell string literal, which the 5.1/7 parser
# mis-decoded (GBK) and every M-B step died instantly on a mangled suite path.  This
# script derives the path from $env:USERPROFILE instead, so it carries no non-ASCII
# literal.  Same argv otherwise; the step log is appended to after/campaign.log.
$ErrorActionPreference = 'Continue'
$attempt = Split-Path -Parent $PSScriptRoot
$py = Join-Path $attempt 'iso\venv\Scripts\python.exe'
$T0 = Join-Path $attempt 'iso\T0\src'
$T4 = Join-Path $attempt 'iso\T4\src'
$T0b = Join-Path $attempt 'iso\T0b\src'
$repo = Join-Path $env:USERPROFILE 'Projects\company-wiki'
$after = Join-Path $attempt 'after'

function Invoke-Step([string]$name, [string[]]$cmdArgs) {
    Write-Output "=== $name ==="
    Write-Output ("argv: " + ($cmdArgs -join ' '))
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & $cmdArgs[0] @($cmdArgs[1..($cmdArgs.Length - 1)])
    $rc = $LASTEXITCODE
    $sw.Stop()
    Write-Output ("rc=$rc elapsed={0:N1}s" -f $sw.Elapsed.TotalSeconds)
    Write-Output ""
}

Write-Output ("repo path resolved to: " + $repo)
Write-Output ("repo exists: " + (Test-Path (Join-Path $repo 'tests\contract\test_source_catalog_worker_bootstrap.py')))

Invoke-Step 'M-B node1 quiet' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'run_band.py'),
    '--python', $py, '--repo', $repo, '--node', 'child_without_runtime', '--condition', 'quiet',
    '--trees', "T0=$T0,T4=$T4,T0b=$T0b", '--runs', '3', '--passes', '2',
    '--root', "$env:TEMP\i14e-band-child-quiet", '--evidence', (Join-Path $after 'band-captures-child-quiet'),
    '--out', (Join-Path $after 'band-child-quiet.json'))
Invoke-Step 'M-B node1 cpu8' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'run_band.py'),
    '--python', $py, '--repo', $repo, '--node', 'child_without_runtime', '--condition', 'cpu', '--burners', '8',
    '--trees', "T0=$T0,T4=$T4,T0b=$T0b", '--runs', '3', '--passes', '2',
    '--root', "$env:TEMP\i14e-band-child-cpu8", '--evidence', (Join-Path $after 'band-captures-child-cpu8'),
    '--out', (Join-Path $after 'band-child-cpu8.json'))
Invoke-Step 'M-B node1 spawn' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'run_band.py'),
    '--python', $py, '--repo', $repo, '--node', 'child_without_runtime', '--condition', 'spawn', '--burners', '8',
    '--trees', "T0=$T0,T4=$T4,T0b=$T0b", '--runs', '3', '--passes', '1',
    '--root', "$env:TEMP\i14e-band-child-spawn", '--evidence', (Join-Path $after 'band-captures-child-spawn'),
    '--out', (Join-Path $after 'band-child-spawn.json'))
Invoke-Step 'M-B node2 quiet' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'run_band.py'),
    '--python', $py, '--repo', $repo, '--node', 'logon_wrapper_quoted', '--condition', 'quiet',
    '--trees', "T0=$T0,T4=$T4", '--runs', '4', '--passes', '1',
    '--root', "$env:TEMP\i14e-band-logon-quiet", '--evidence', (Join-Path $after 'band-captures-logon-quiet'),
    '--out', (Join-Path $after 'band-logon-quiet.json'))
Invoke-Step 'M-B node2 cpu8' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'run_band.py'),
    '--python', $py, '--repo', $repo, '--node', 'logon_wrapper_quoted', '--condition', 'cpu', '--burners', '8',
    '--trees', "T0=$T0,T4=$T4", '--runs', '4', '--passes', '1',
    '--root', "$env:TEMP\i14e-band-logon-cpu8", '--evidence', (Join-Path $after 'band-captures-logon-cpu8'),
    '--out', (Join-Path $after 'band-logon-cpu8.json'))

Write-Output 'M-B STEPS COMPLETE'
