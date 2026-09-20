# M01 command runner. ASCII-only on purpose: Windows PowerShell 5.1 decodes
# .ps1 files using the ANSI code page, so a non-ASCII path literal would be
# mangled. All paths are derived from $env:USERPROFILE instead.
$ErrorActionPreference = "Continue"
$plan = Join-Path $env:USERPROFILE "Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
$d = Join-Path $plan "execution_runs\M01\a20260919-01"
$py = Join-Path $d "iso\venv\Scripts\python.exe"
$code = Join-Path $d "iso\checkout_scripts"
$ev = Join-Path $d "evidence\M01"
$log = Join-Path $d "before\run_log.txt"
Remove-Item $log -ErrorAction SilentlyContinue

function Run-Step {
  param([string]$Id, [string[]]$Argv, [string]$OutFile, [string]$ErrFile)
  Add-Content -Path $log -Value ("### STEP " + $Id)
  Add-Content -Path $log -Value ("argv: " + $py + " " + ($Argv -join " "))
  $so = & $py @Argv 2> $ErrFile
  $rc = $LASTEXITCODE
  $so | Out-File -FilePath $OutFile -Encoding utf8
  Add-Content -Path $log -Value ("raw_rc=" + $rc)
  Add-Content -Path $log -Value ("stdout_file=" + $OutFile)
  Add-Content -Path $log -Value ("stderr_file=" + $ErrFile)
  return $rc
}

$rcA = Run-Step -Id "A-oracle" -Argv @("-X","utf8","-B",(Join-Path $d "scripts\oracle_M01.py")) -OutFile (Join-Path $ev "oracle_stdout.txt") -ErrFile (Join-Path $d "before\oracle_stderr.txt")
$rcB = Run-Step -Id "B-product-run" -Argv @("-X","utf8","-B",(Join-Path $d "scripts\run_M01.py"),"--attempt",$d,"--code-root",$code,"--out",(Join-Path $ev "run_result.json")) -OutFile (Join-Path $ev "stdout.txt") -ErrFile (Join-Path $ev "stderr.txt")
$rcC = Run-Step -Id "C-pytest-sanity" -Argv @("-X","utf8","-B","-m","pytest","--version") -OutFile (Join-Path $d "before\pytest_version.txt") -ErrFile (Join-Path $d "before\pytest_version_err.txt")

Add-Content -Path $log -Value ("SUMMARY oracle_rc=" + $rcA + " product_rc=" + $rcB + " pytest_rc=" + $rcC)
Write-Host ("oracle_rc=" + $rcA + " product_rc=" + $rcB + " pytest_rc=" + $rcC)
Get-Content $log
