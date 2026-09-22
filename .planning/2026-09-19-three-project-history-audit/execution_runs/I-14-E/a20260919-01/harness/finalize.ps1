# I-14-E: post-campaign pipeline (ASCII-only on purpose: the earlier non-ASCII literal
# broke path parsing).  Runs the artifact collector, the analyser, the fail-able-case
# builder, the hash closure and the commands transcription, in that order.
$ErrorActionPreference = 'Continue'
$attempt = Split-Path -Parent $PSScriptRoot
$py = Join-Path $attempt 'iso\venv\Scripts\python.exe'
$after = Join-Path $attempt 'after'
$tmp = $env:TEMP

function Step([string]$name, [string[]]$cmdArgs) {
    Write-Output "=== $name ==="
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    & $cmdArgs[0] @($cmdArgs[1..($cmdArgs.Length - 1)])
    Write-Output ("rc=$LASTEXITCODE elapsed={0:N1}s" -f $sw.Elapsed.TotalSeconds)
    Write-Output ""
}

$bands = @(
    @{ name = 'child-quiet'; root = 'i14e-band-child-quiet' },
    @{ name = 'child-cpu8'; root = 'i14e-band-child-cpu8' },
    @{ name = 'child-spawn'; root = 'i14e-band-child-spawn' },
    @{ name = 'logon-quiet'; root = 'i14e-band-logon-quiet' },
    @{ name = 'logon-cpu8'; root = 'i14e-band-logon-cpu8' }
)

foreach ($band in $bands) {
    $bandJson = Join-Path $after ("band-" + $band.name + ".json")
    if (-not (Test-Path $bandJson)) { Write-Output ("skip (missing): " + $bandJson); continue }
    Step ("artifacts " + $band.name) @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'collect_artifacts.py'),
        '--band', $bandJson, '--scratch', (Join-Path $tmp $band.root),
        '--out', (Join-Path $after ("artifacts-" + $band.name + ".json")),
        '--copy-to', (Join-Path $after ("artifacts-" + $band.name)))
}

Step 'analyze' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'analyze.py'))
Step 'fail-able cases' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'fail_able_cases.py'))
Step 'final hashes' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'final_hashes.py'))
Step 'sync commands' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'sync_commands.py'))
Write-Output 'FINALIZE COMPLETE'
