# GATE-TIMEOUT-1200 GREEN arm: authorized gate state (timeout=1200) + a fresh,
# identically configured set of exactly 8 CPU burners.
# ASCII-ONLY ON PURPOSE: Windows PowerShell 5.1 decodes BOM-less .ps1 as ANSI, so this
# script contains no non-ASCII literals and derives every path from $PSScriptRoot.
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

# 1. set the gate to the GREEN state: authorized bytes (anchor + the one line 600 -> 1200)
Copy-Item $anchorCopy "$repo\tools\pre_push_gate.py" -Force
$gatePath = "$repo\tools\pre_push_gate.py"
$content = [System.IO.File]::ReadAllText($gatePath)
$old = 'cmd: list[str], label: str, timeout: int = 600, *, blocking: bool = True'
$new = 'cmd: list[str], label: str, timeout: int = 1200, *, blocking: bool = True'
if (-not $content.Contains($old)) { Write-Output 'FATAL: anchor line not found'; exit 9 }
[System.IO.File]::WriteAllText($gatePath, ($content.Replace($old, $new)), (New-Object System.Text.UTF8Encoding($false)))
$h = (Get-FileHash $gatePath -Algorithm SHA256).Hash.ToLower()
if ($h -ne $afterHash) { Write-Output "FATAL: gate hash at GREEN start [$h] != authorized after hash [$afterHash]"; exit 9 }
Write-Output "GREEN_GATE_HASH_VERIFIED=$h"

# 2. spawn exactly 8 CPU burners (fresh set, same configuration as RED)
$pids = @()
$burnStart = (Get-Date).ToUniversalTime().ToString('o')
1..8 | ForEach-Object {
    $p = Start-Process -PassThru -WindowStyle Hidden 'C:\Miniconda\python.exe' -ArgumentList @('-u', "$a\scripts\cpu_burner.py")
    $pids += $p.Id
}
$alive0 = @($pids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count
$rec = @{ arm = 'green'; started_utc = $burnStart; requested = 8; alive_after_start = $alive0; pids = $pids; script = "$a\scripts\cpu_burner.py"; same_configuration_as_red = $true } | ConvertTo-Json
[System.IO.File]::WriteAllText("$a\evidence\burners_green.json", $rec, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "BURNERS_STARTED alive=$alive0 pids=$($pids -join ',')"
Start-Sleep -Seconds 5
$alive1 = @($pids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count
Write-Output "BURNERS_ALIVE_AFTER_5S=$alive1"

# 3. run the gate, FULL unfiltered capture
& 'C:\Miniconda\python.exe' -u "$a\scripts\timed_gate_run.py" $repo "$a\after\gate_green_1200.txt" "$a\after\step_times_green_1200.json"
Write-Output "WRAPPER_RC=$LASTEXITCODE"

# 4. stop the burners
$burnStop = (Get-Date).ToUniversalTime().ToString('o')
foreach ($procId in $pids) { Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue }
Start-Sleep -Seconds 2
$left = @($pids | Where-Object { Get-Process -Id $_ -ErrorAction SilentlyContinue }).Count
$rec2 = @{ arm = 'green'; stopped_utc = $burnStop; pids = $pids; survivors = $left } | ConvertTo-Json
[System.IO.File]::WriteAllText("$a\evidence\burners_green_stopped.json", $rec2, (New-Object System.Text.UTF8Encoding($false)))
Write-Output "BURNERS_STOPPED survivors=$left"

# 5. verdict lines + final state checks
if (Test-Path "$a\after\gate_green_1200.txt") {
    $txt = Get-Content "$a\after\gate_green_1200.txt"
    Write-Output "HAS_GATE_GREEN=$([bool]($txt -match 'pre-push gate GREEN'))"
    Write-Output "HAS_55_PASSED=$([bool]($txt -match '55 passed'))"
    Write-Output "SKIPPED_LINES=$(((($txt -match '\d+ skipped') | Measure-Object).Count))"
    Write-Output "HAS_TIMEOUTEXPIRED=$([bool]($txt -match 'TimeoutExpired'))"
    Write-Output "CAPTURE_BYTES=$((Get-Item "$a\after\gate_green_1200.txt").Length)"
}
$final = (Get-FileHash $gatePath -Algorithm SHA256).Hash.ToLower()
Write-Output "GATE_FILE_FINAL_SHA256=$final"
git -C $repo diff --numstat -- tools/pre_push_gate.py | Out-File -Encoding utf8 "$a\evidence\green_gate_numstat_at_end.txt"
git -C $repo status --porcelain | Out-File -Encoding utf8 "$a\evidence\git_status_after_green.txt"
Write-Output "GREEN_ARM_DONE"
