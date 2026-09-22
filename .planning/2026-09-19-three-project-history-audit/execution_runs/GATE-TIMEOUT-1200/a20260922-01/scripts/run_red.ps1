# GATE-TIMEOUT-1200 RED arm: gate at timeout=600 (original bytes) + exactly 8 CPU burners.
# One bounded attempt per oracle.md. Never fakes load.
# ASCII-ONLY ON PURPOSE: Windows PowerShell 5.1 decodes BOM-less .ps1 as ANSI, so this
# script contains no non-ASCII literals and derives every path from $PSScriptRoot.
$ErrorActionPreference = 'Continue'
$a = Split-Path $PSScriptRoot -Parent
$repo = $a
foreach ($i in 1..5) { $repo = Split-Path $repo -Parent }
$before = '0d290326200ebde819d3473589bd1aa0ed36da4806097d8a59dc8dc316fcc594'
$anchorCopy = "$a\before\pre_push_gate.py.orig"
if (-not (Test-Path "$repo\tools\pre_push_gate.py")) { Write-Output "FATAL: repo derivation failed: $repo"; exit 8 }
if (-not (Test-Path $anchorCopy)) { Write-Output "FATAL: anchor copy missing: $anchorCopy"; exit 8 }
if (-not (Test-Path "$a\scripts\cpu_burner.py")) { Write-Output "FATAL: burner script missing"; exit 8 }
Write-Output "REPO=$repo"
Write-Output "ATTEMPT=$a"

# 0. pre-run state snapshot (read-only)
git -C $repo status --porcelain | Out-File -Encoding utf8 "$a\evidence\git_status_before_red.txt"

# 1. set the gate to the RED state: restore original bytes (timeout=600)
Copy-Item $anchorCopy "$repo\tools\pre_push_gate.py" -Force
$h = (Get-FileHash "$repo\tools\pre_push_gate.py" -Algorithm SHA256).Hash.ToLower()
if ($h -ne $before) { Write-Output "FATAL: gate hash at RED start [$h] != anchor [$before]"; exit 9 }
Write-Output "RED_GATE_HASH_VERIFIED=$h"
git -C $repo diff --numstat -- tools/pre_push_gate.py | Out-File -Encoding utf8 "$a\evidence\red_gate_numstat_at_start.txt"

# 2. spawn exactly 8 CPU burners
$pids = @()
$burnStart = (Get-Date).ToUniversalTime().ToString('o')
1..8 | ForEach-Object {
    $p = Start-Process -PassThru -WindowStyle Hidden 'C:\Miniconda\python.exe' -ArgumentList @('-u', "$a\scripts\cpu_burner.py")
    $pids += $p.Id
}
$alive0 = @($pids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count
$rec = @{ arm = 'red'; started_utc = $burnStart; requested = 8; alive_after_start = $alive0; pids = $pids; script = "$a\scripts\cpu_burner.py" } | ConvertTo-Json
[System.IO.File]::WriteAllText("$a\evidence\burners_red.json", $rec, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "BURNERS_STARTED alive=$alive0 pids=$($pids -join ',')"
Start-Sleep -Seconds 5
$alive1 = @($pids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count
Write-Output "BURNERS_ALIVE_AFTER_5S=$alive1"

# 3. run the gate, FULL unfiltered capture
& 'C:\Miniconda\python.exe' -u "$a\scripts\timed_gate_run.py" $repo "$a\after\gate_red_600.txt" "$a\after\step_times_red_600.json"
Write-Output "WRAPPER_RC=$LASTEXITCODE"

# 4. stop the burners (RED attempt is over either way)
$burnStop = (Get-Date).ToUniversalTime().ToString('o')
foreach ($procId in $pids) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
$left = @($pids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count
$rec2 = @{ arm = 'red'; stopped_utc = $burnStop; pids = $pids; survivors = $left } | ConvertTo-Json
[System.IO.File]::WriteAllText("$a\evidence\burners_red_stopped.json", $rec2, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "BURNERS_STOPPED survivors=$left"

# 5. quick verdict lines from the capture (unfiltered file stays untouched)
if (Test-Path "$a\after\gate_red_600.txt") {
    $txt = Get-Content "$a\after\gate_red_600.txt"
    Write-Output "HAS_TIMEOUTEXPIRED_600=$([bool]($txt -match 'timed out after 600 seconds'))"
    Write-Output "HAS_GATE_GREEN=$([bool]($txt -match 'pre-push gate GREEN'))"
    Write-Output "CAPTURE_BYTES=$((Get-Item "$a\after\gate_red_600.txt").Length)"
}
Write-Output "RED_ARM_DONE"
