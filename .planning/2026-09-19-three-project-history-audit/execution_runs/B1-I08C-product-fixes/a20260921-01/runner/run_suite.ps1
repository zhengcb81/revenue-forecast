param(
  [Parameter(Mandatory=$true)][string]$RepoRoot,
  [Parameter(Mandatory=$true)][string]$OutBase,
  [Parameter(Mandatory=$true)][string]$Label,
  [string[]]$Targets = @(),
  [string]$TargetsFile = ""
)
$ErrorActionPreference = 'Stop'
$Py = "C:\Miniconda\python.exe"
if (-not [string]::IsNullOrWhiteSpace($TargetsFile)) {
  $Targets = Get-Content $TargetsFile | Where-Object { $_.Trim() -ne "" } | ForEach-Object { $_.Trim() }
}
$Tests = Join-Path $RepoRoot "tests"
$env:PYTHONDONTWRITEBYTECODE = "1"
$env:B1_REPO_ROOT = $RepoRoot
$env:REVENUE_PUBLICATION_REGISTRY = "$OutBase\registry\$Label.jsonl"
$env:PYTHONPATH = "$RepoRoot\scripts;$Tests"
New-Item -ItemType Directory -Force -Path "$OutBase\registry" | Out-Null

$stdout = "$OutBase\$Label.stdout.txt"
$stderr = "$OutBase\$Label.stderr.txt"
$argv = @("-X","utf8","-B","-m","pytest","-p","no:cacheprovider","-q","--no-header","-rN") + $Targets
Push-Location $Tests
try {
  & $Py @argv 1> $stdout 2> $stderr
  $rc = $LASTEXITCODE
} finally { Pop-Location }
Set-Content -Path "$OutBase\$Label.rc.txt" -Value $rc -Encoding ascii
Write-Host "rc=$rc"
Get-Content $stdout | Select-Object -Last 12
if ((Get-Item $stderr).Length -gt 0) { Write-Host "--- stderr ---"; Get-Content $stderr | Select-Object -Last 20 }
exit 0
