# GATE-TIMEOUT-1200 GREEN arm attempt #2 (same-domain control, per parent instruction).
# Attempt #1 evidence (gate_green_1200.txt) is NEVER overwritten: this attempt writes
# *_attempt2_samedomain.* files. ASCII-ONLY (Windows PowerShell 5.1 BOM-less .ps1 = ANSI).
$ErrorActionPreference = 'Continue'
$a = Split-Path $PSScriptRoot -Parent
$repo = $a
foreach ($i in 1..5) { $repo = Split-Path $repo -Parent }
$afterHash = 'cf09ade8164e89d79237ff5a8409496ab1ae2a9c5f3ee2c253ccad20ef06df0b'
$anchorCopy = "$a\before\pre_push_gate.py.orig"
if (-not (Test-Path "$repo\tools\pre_push_gate.py")) { Write-Output "FATAL: repo derivation failed: $repo"; exit 8 }
if (-not (Test-Path $anchorCopy)) { Write-Output "FATAL: anchor copy missing"; exit 8 }
Write-Output "REPO=$repo"
Write-Output "ATTEMPT=$a"

# 0. verify GREEN state + ambient load snapshot BEFORE burners
$content = [System.IO.File]::ReadAllText("$repo\tools\pre_push_gate.py")
$expected = 'cmd: list[str], label: str, timeout: int = 1200, *, blocking: bool = True'
if (-not $content.Contains($expected)) { Write-Output 'FATAL: gate not in authorized 1200 state'; exit 9 }
$h = (Get-FileHash "$repo\tools\pre_push_gate.py" -Algorithm SHA256).Hash.ToLower()
if ($h -ne $afterHash) { Write-Output "FATAL: gate hash [$h] != authorized [$afterHash]"; exit 9 }
Write-Output "GREEN_GATE_HASH_VERIFIED=$h"
$ambientBefore = @(Get-Process python, pythonw -ErrorAction SilentlyContinue).Count
$snap0 = @{ stage = 'green2_before_burners'; taken_utc = (Get-Date).ToUniversalTime().ToString('o'); ambient_python_procs = $ambientBefore } | ConvertTo-Json
[System.IO.File]::WriteAllText("$a\evidence\load_snapshot_green2_start.json", $snap0, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "AMBIENT_BEFORE_BURNERS=$ambientBefore"

# 1. spawn exactly 8 CPU burners (same configuration as RED)
$pids = @()
$burnStart = (Get-Date).ToUniversalTime().ToString('o')
1..8 | ForEach-Object {
    $p = Start-Process -PassThru -WindowStyle Hidden 'C:\Miniconda\python.exe' -ArgumentList @('-u', "$a\scripts\cpu_burner.py")
    $pids += $p.Id
}
$alive0 = @($pids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count
$rec = @{ arm = 'green2'; started_utc = $burnStart; requested = 8; alive_after_start = $alive0; pids = $pids; script = "$a\scripts\cpu_burner.py"; same_configuration_as_red = $true; ambient_before_burners = $ambientBefore } | ConvertTo-Json
[System.IO.File]::WriteAllText("$a\evidence\burners_green2.json", $rec, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "BURNERS_STARTED alive=$alive0 pids=$($pids -join ',')"

# 2. mid-run load snapshot (a few seconds in, gate now running)
Start-Sleep -Seconds 8
$mid = @{ stage = 'green2_mid_run'; taken_utc = (Get-Date).ToUniversalTime().ToString('o'); python_procs = @(Get-Process python, pythonw -ErrorAction SilentlyContinue).Count; this_cards_burners_alive = @($pids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count } | ConvertTo-Json
[System.IO.File]::WriteAllText("$a\evidence\load_snapshot_green2_mid.json", $mid, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "MID_SNAPSHOT_DONE"

# 3. run the gate, FULL unfiltered capture (attempt-2 filenames)
& 'C:\Miniconda\python.exe' -u "$a\scripts\timed_gate_run.py" $repo "$a\after\gate_green_1200_attempt2_samedomain.txt" "$a\after\step_times_green_1200_attempt2.json"
Write-Output "WRAPPER_RC=$LASTEXITCODE"

# 4. stop the burners + end load snapshot
$burnStop = (Get-Date).ToUniversalTime().ToString('o')
foreach ($procId in $pids) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
$left = @($pids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count
$rec2 = @{ arm = 'green2'; stopped_utc = $burnStop; pids = $pids; survivors = $left } | ConvertTo-Json
[System.IO.File]::WriteAllText("$a\evidence\burners_green2_stopped.json", $rec2, (New-Object System.Text.UTF8Encoding($false)))
$snapE = @{ stage = 'green2_after_burners'; taken_utc = (Get-Date).ToUniversalTime().ToString('o'); python_procs = @(Get-Process python, pythonw -ErrorAction SilentlyContinue).Count } | ConvertTo-Json
[System.IO.File]::WriteAllText("$a\evidence\load_snapshot_green2_end.json", $snapE, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "BURNERS_STOPPED survivors=$left"

# 5. verdict markers
$cap = "$a\after\gate_green_1200_attempt2_samedomain.txt"
if (Test-Path $cap) {
    $txt = Get-Content $cap
    Write-Output "HAS_GATE_GREEN=$([bool]($txt -match 'pre-push gate GREEN'))"
    Write-Output "HAS_55_PASSED=$([bool]($txt -match '55 passed'))"
    Write-Output "SKIPPED_LINES=$(((($txt -match '\d+ skipped') | Measure-Object).Count))"
    Write-Output "HAS_TIMEOUTEXPIRED=$([bool]($txt -match 'TimeoutExpired'))"
    Write-Output "HAS_FAILED=$([bool]($txt -match 'FAILED'))"
    Write-Output "CAPTURE_BYTES=$((Get-Item $cap).Length)"
}
$final = (Get-FileHash "$repo\tools\pre_push_gate.py" -Algorithm SHA256).Hash.ToLower()
Write-Output "GATE_FILE_FINAL_SHA256=$final"
Write-Output "GREEN2_ARM_DONE"
