param(
  [Parameter(Mandatory=$true)][string]$RepoRoot,
  [Parameter(Mandatory=$true)][string]$OutBase,
  [string]$TestFile = "",
  [string]$Label = "run"
)
$ErrorActionPreference = 'Stop'
$Attempt = "C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\B1-I08C-product-fixes\a20260921-01"
$Py = "C:\Miniconda\python.exe"
if ([string]::IsNullOrEmpty($TestFile)) { $TestFile = Join-Path $Attempt "test_b1_rem.py" }

$env:B1_REPO_ROOT = $RepoRoot
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:REVENUE_PUBLICATION_REGISTRY = "$OutBase\registry\publications.jsonl"
$env:PYTHONPATH = "$RepoRoot\scripts;$RepoRoot\tests"
New-Item -ItemType Directory -Force -Path "$OutBase\registry" | Out-Null

$stdout = "$OutBase\$Label.stdout.txt"
$stderr = "$OutBase\$Label.stderr.txt"
$rcfile = "$OutBase\$Label.rc.txt"

$argv = @("-X","utf8","-B","-m","pytest","-p","no:cacheprovider","-q","--no-header","-rA",$TestFile)
& $Py @argv 1> $stdout 2> $stderr
$rc = $LASTEXITCODE
Set-Content -Path $rcfile -Value $rc -Encoding ascii
Write-Host "rc=$rc"
Get-Content $stdout | Select-Object -Last 60
if ((Get-Item $stderr).Length -gt 0) { Write-Host "--- stderr ---"; Get-Content $stderr | Select-Object -Last 30 }
exit 0
