param(
  [Parameter(Mandatory=$true)][string]$RepoRoot,
  [Parameter(Mandatory=$true)][string]$TestFile,
  [Parameter(Mandatory=$true)][string]$Label
)
# B1-PREREQ arm runner. Evidence protocol (oracle §3.4): every label is
# WRITE-ONCE; raw stdout/stderr/rc land under evidence/<label>.* byte-for-byte.
$ErrorActionPreference = 'Stop'
# Encoding-independent root derivation: the attempt path contains non-ASCII
# characters and this shell may read .ps1 files with the ANSI codepage, so the
# path is NEVER hardcoded in this script.
$Attempt = Split-Path -Parent $PSScriptRoot
$Py = "C:\Miniconda\python.exe"
$Evidence = Join-Path $Attempt "evidence"
New-Item -ItemType Directory -Force -Path $Evidence | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Attempt "runner\registry") | Out-Null

$stdout = "$Evidence\$Label.stdout.txt"
$stderr = "$Evidence\$Label.stderr.txt"
$rcfile = "$Evidence\$Label.rc.txt"
foreach ($f in @($stdout, $stderr, $rcfile)) {
  if (Test-Path $f) {
    Write-Host "LABEL COLLISION: $f already exists; refusing to overwrite (evidence protocol). Use a new label."
    exit 99
  }
}

$env:B1_REPO_ROOT = $RepoRoot
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:REVENUE_PUBLICATION_REGISTRY = Join-Path $Attempt "runner\registry\publications.jsonl"
$env:PYTHONPATH = "$RepoRoot\scripts;$RepoRoot\tests"

$argvStr = '-X utf8 -B -m pytest -p no:cacheprovider -q --no-header -rA "' + $TestFile + '"'
# Raw OS-level byte redirection via cmd (no PowerShell re-encoding) — the F4
# evidence protocol promises byte-for-byte stdout/stderr.
cmd /c "`"$Py`" $argvStr > `"$stdout`" 2> `"$stderr`""
$rc = $LASTEXITCODE
Set-Content -Path $rcfile -Value $rc -Encoding ascii
Write-Host "rc=$rc"
Get-Content $stdout | Select-Object -Last 40
if ((Get-Item $stderr).Length -gt 0) { Write-Host "--- stderr ---"; Get-Content $stderr | Select-Object -Last 30 }
exit 0
