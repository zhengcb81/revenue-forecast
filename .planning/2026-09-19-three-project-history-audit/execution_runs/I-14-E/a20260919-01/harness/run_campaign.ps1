# I-14-E measurement campaign (sequential on purpose: the arms must not compete with
# each other for the machine).  Every command is an evidence collector; the log lands in
# after/campaign.log.  Nothing in this script touches a production repo.
$ErrorActionPreference = 'Continue'
$attempt = Split-Path -Parent $PSScriptRoot
$py = Join-Path $attempt 'iso\venv\Scripts\python.exe'
$T0 = Join-Path $attempt 'iso\T0\src'
$T4 = Join-Path $attempt 'iso\T4\src'
$T0b = Join-Path $attempt 'iso\T0b\src'
$repo = Join-Path $env:USERPROFILE 'Projects\company-wiki'
$after = Join-Path $attempt 'after'
New-Item -ItemType Directory -Force -Path $after | Out-Null

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

$ambient = "import json,subprocess,sys,time;py=sys.executable;r=[]`nfor _ in range(3):`n    t=time.perf_counter()`n    subprocess.run([py,'-c','pass'],stdout=subprocess.DEVNULL)`n    r.append(round((time.perf_counter()-t)*1000,1))`nout=subprocess.run(['tasklist'],capture_output=True,text=True).stdout.splitlines()`nprint(json.dumps({'spawn_python_pass_ms':r,'tasklist_lines':len(out)}))"

Invoke-Step 'ambient-before' @($py, '-X', 'utf8', '-c', $ambient)

# ---- M-A: the two load-sensitive quantities of node 1, measured without pytest ----
Invoke-Step 'M-A popen quiet' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'measure_child_lifetime.py'),
    '--python', $py, '--tree', $T0, '--method', 'popen', '--condition', 'quiet', '--samples', '30',
    '--root', "$env:TEMP\i14e-ma-popen-quiet", '--out', (Join-Path $after 'child-lifetime-popen-quiet.json'))
Invoke-Step 'M-A popen cpu8' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'measure_child_lifetime.py'),
    '--python', $py, '--tree', $T0, '--method', 'popen', '--condition', 'cpu', '--burners', '8', '--samples', '25',
    '--root', "$env:TEMP\i14e-ma-popen-cpu8", '--out', (Join-Path $after 'child-lifetime-popen-cpu8.json'))
Invoke-Step 'M-A popen cpu12' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'measure_child_lifetime.py'),
    '--python', $py, '--tree', $T0, '--method', 'popen', '--condition', 'cpu', '--burners', '12', '--samples', '20',
    '--root', "$env:TEMP\i14e-ma-popen-cpu12", '--out', (Join-Path $after 'child-lifetime-popen-cpu12.json'))
Invoke-Step 'M-A startproc quiet' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'measure_child_lifetime.py'),
    '--python', $py, '--tree', $T0, '--method', 'startproc', '--condition', 'quiet', '--samples', '8',
    '--root', "$env:TEMP\i14e-ma-startproc-quiet", '--out', (Join-Path $after 'child-lifetime-startproc-quiet.json'))
Invoke-Step 'M-A startproc cpu8' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'measure_child_lifetime.py'),
    '--python', $py, '--tree', $T0, '--method', 'startproc', '--condition', 'cpu', '--burners', '8', '--samples', '8',
    '--root', "$env:TEMP\i14e-ma-startproc-cpu8", '--out', (Join-Path $after 'child-lifetime-startproc-cpu8.json'))

# ---- M-B node 1: child_without_runtime, three trees (T0, T4, T0b) ----
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

# ---- M-B node 2: logon_wrapper_quoted, two trees ----
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

# ---- M-C: node 2's three timing budgets, measured directly ----
Invoke-Step 'M-C wrapper quiet' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'measure_wrapper_latency.py'),
    '--python', $py, '--condition', 'quiet', '--samples', '8',
    '--root', "$env:TEMP\i14e-mc-quiet", '--out', (Join-Path $after 'wrapper-latency-quiet.json'))
Invoke-Step 'M-C wrapper cpu8' @($py, '-X', 'utf8', (Join-Path $PSScriptRoot 'measure_wrapper_latency.py'),
    '--python', $py, '--condition', 'cpu', '--burners', '8', '--samples', '8',
    '--root', "$env:TEMP\i14e-mc-cpu8", '--out', (Join-Path $after 'wrapper-latency-cpu8.json'))

Invoke-Step 'ambient-after' @($py, '-X', 'utf8', '-c', $ambient)

Write-Output 'CAMPAIGN COMPLETE'
