<#
setup_isolation.ps1 - attempt-local isolation bootstrap for one M-card attempt.

This file is ASCII-only by construction (no non-ASCII literal appears in it), so the
PowerShell 5.1 ANSI/GBK script decoding cannot corrupt any path. Every root is derived
from -AttemptRoot / $env:USERPROFILE instead of being spelled out.

Steps
  A0  create the attempt-local isolated interpreter with
      `& <I-00-A template python> -m venv <attempt>\iso\venv`
  A1  (pytest NOT installed here - see the receipt: no offline wheel is available in the
      local pip cache and the A-C scope does not need pytest; no pytest command is run)
  A2  materialise iso\checkout_scripts as a byte-identical read-only snapshot of the two
      production modules and prove equality by sha256
  A3  capture the pre-existing dirty state of the three production repos into before\

Exit codes: 0 ok, 11 venv creation failed, 12 hash mismatch, 13 missing product source.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$AttemptRoot,
    [Parameter(Mandatory = $true)][string]$Card
)

$ErrorActionPreference = "Stop"

$attempt        = (Resolve-Path -LiteralPath $AttemptRoot).Path
$cardDir        = Split-Path -Parent $attempt
$executionRuns  = Split-Path -Parent $cardDir
$plan           = Split-Path -Parent $executionRuns
$prod           = Join-Path $env:USERPROFILE "Projects\revenue-forecast"
$templatePy     = Join-Path $plan "execution_runs\I-00-A\a20260919-01\iso\venv\Scripts\python.exe"

Write-Output ("attempt_root        = " + $attempt)
Write-Output ("card                = " + $Card)
Write-Output ("plan_root           = " + $plan)
Write-Output ("production_root     = " + $prod)
Write-Output ("template_python     = " + $templatePy)

if (-not (Test-Path -LiteralPath $templatePy)) { Write-Output "MISSING template python"; exit 11 }

foreach ($d in @("scripts", "evidence\$Card", "before", "after", "recovery", "iso\checkout_scripts")) {
    New-Item -ItemType Directory -Force -Path (Join-Path $attempt $d) | Out-Null
}

# ---------------- A0: attempt-local venv ----------------
$venvPy = Join-Path $attempt "iso\venv\Scripts\python.exe"
$venvCreated = $false
if (-not (Test-Path -LiteralPath $venvPy)) {
    & $templatePy -m venv (Join-Path $attempt "iso\venv")
    if ($LASTEXITCODE -ne 0) { Write-Output ("venv creation failed rc=" + $LASTEXITCODE); exit 11 }
    $venvCreated = $true
}
Write-Output ("venv_python         = " + $venvPy)
Write-Output ("venv_created_now    = " + $venvCreated)

$pyVersion = (& $venvPy -c "import sys; print(sys.version.split()[0])")
$pyExeHash = (Get-FileHash -LiteralPath $venvPy -Algorithm SHA256).Hash.ToLower()
Write-Output ("python_version      = " + $pyVersion)
Write-Output ("python_exe_sha256   = " + $pyExeHash)

# ---------------- A2: read-only product snapshot ----------------
$srcReg  = Join-Path $prod "scripts\model_registry.py"
$srcExt  = Join-Path $prod "scripts\model_extensions.py"
foreach ($s in @($srcReg, $srcExt)) {
    if (-not (Test-Path -LiteralPath $s)) { Write-Output ("MISSING product source: " + $s); exit 13 }
}
$dstReg = Join-Path $attempt "iso\checkout_scripts\model_registry.py"
$dstExt = Join-Path $attempt "iso\checkout_scripts\model_extensions.py"
Copy-Item -LiteralPath $srcReg -Destination $dstReg -Force
Copy-Item -LiteralPath $srcExt -Destination $dstExt -Force

$h = @{}
foreach ($pair in @(@("scripts/model_registry.py", $srcReg), @("scripts/model_extensions.py", $srcExt),
                    @("iso/checkout_scripts/model_registry.py", $dstReg), @("iso/checkout_scripts/model_extensions.py", $dstExt))) {
    $h[$pair[0]] = (Get-FileHash -LiteralPath $pair[1] -Algorithm SHA256).Hash.ToLower()
}
$equal = ($h["scripts/model_registry.py"] -eq $h["iso/checkout_scripts/model_registry.py"]) -and
         ($h["scripts/model_extensions.py"] -eq $h["iso/checkout_scripts/model_extensions.py"])
foreach ($k in ($h.Keys | Sort-Object)) { Write-Output ("sha256 " + $k + " = " + $h[$k]) }
Write-Output ("isolated_copy_equals_production = " + $equal)
if (-not $equal) { exit 12 }

# ---------------- A3: pre-existing dirty state of the three repos ----------------
$repos = @{}
foreach ($name in @("revenue-forecast", "company-wiki", "filing-fetch")) {
    $repo = Join-Path (Join-Path $env:USERPROFILE "Projects") $name
    $target = Join-Path $attempt ("before\git_status_" + $name + ".txt")
    $errtarget = Join-Path $attempt ("before\git_status_" + $name + ".stderr.txt")
    if (Test-Path -LiteralPath $repo) {
        # raw cmd redirection: git writes a harmless "Permission denied" warning for a
        # read-only directory under .planning\...\reviews, and PowerShell would turn that
        # stderr text into a terminating NativeCommandError under $ErrorActionPreference=Stop.
        cmd /c "git -C `"$repo`" status --porcelain > `"$target`" 2> `"$errtarget`""
        $lines = @(Get-Content -LiteralPath $target -ErrorAction SilentlyContinue)
        $errcount = @(Get-Content -LiteralPath $errtarget -ErrorAction SilentlyContinue | Where-Object { $_ -ne "" }).Count
        $repos[$name] = @{ path = $repo; porcelain_lines = $lines.Count; file = ("before/git_status_" + $name + ".txt"); stderr_lines = $errcount; stderr_file = ("before/git_status_" + $name + ".stderr.txt") }
        Write-Output ("git_status " + $name + " -> " + $repos[$name].file + " (" + $lines.Count + " lines, stderr " + $errcount + " lines)")
    } else {
        $repos[$name] = @{ path = $repo; state = "ABSENT" }
        Write-Output ("git_status " + $name + " -> ABSENT")
    }
}

# ---------------- receipt ----------------
$receipt = [ordered]@{
    card = $Card
    attempt_root = $attempt
    plan_root = $plan
    production_root_readonly = $prod
    template_python = $templatePy
    venv_python = $venvPy
    venv_created_now = $venvCreated
    python_version = $pyVersion
    python_exe_sha256 = $pyExeHash
    pytest_installed = $false
    pytest_note = "pytest was deliberately NOT installed: no pytest wheel is present in the local pip cache and installing it would require network, which is forbidden for this card. The A-C scope runs a self-contained stdlib+product script; no pytest command was executed."
    hashes = $h
    isolated_copy_equals_production = $equal
    repos = $repos
    timestamp_utc = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
}
$receiptPath = Join-Path $attempt "before\setup_receipt.json"
$json = ($receipt | ConvertTo-Json -Depth 6)
[IO.File]::WriteAllText($receiptPath, $json, (New-Object System.Text.UTF8Encoding($false)))
Write-Output ("receipt -> before/setup_receipt.json")
Write-Output "SETUP_OK"
exit 0
