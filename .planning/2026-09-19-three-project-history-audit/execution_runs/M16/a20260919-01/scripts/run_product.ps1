<#
run_product.ps1 - run the verdict-carrying runner against the attempt-local isolated snapshot.

  * interpreter : <attempt>\iso\venv\Scripts\python.exe  (never the global Miniconda python)
  * code root   : <attempt>\iso\checkout_scripts         (byte-identical read-only snapshot)
  * stdout/stderr are captured with Start-Process redirection, which writes the child's raw
    bytes to the file (no PowerShell re-encoding), so stdout.txt is the genuine process stdout
    and scripts/verify_card.py can assert it line-by-line against run_result.json.

Prints `raw_rc=<n>` and exits with the same code so the caller records the real verdict.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$AttemptRoot,
    [Parameter(Mandatory = $true)][string]$Card
)

$ErrorActionPreference = "Stop"
$attempt = (Resolve-Path -LiteralPath $AttemptRoot).Path
$python = Join-Path $attempt "iso\venv\Scripts\python.exe"
$runner = Join-Path $attempt "scripts\run_card.py"
$codeRoot = Join-Path $attempt "iso\checkout_scripts"
$evidenceDir = Join-Path $attempt ("evidence\" + $Card)

if (-not (Test-Path -LiteralPath $python)) { Write-Output "MISSING venv python"; exit 21 }
if (-not (Test-Path -LiteralPath $runner)) { Write-Output "MISSING runner"; exit 22 }
if (-not (Test-Path -LiteralPath $codeRoot)) { Write-Output "MISSING code root"; exit 23 }

$argv = @(
    "-X", "utf8", "-B", $runner,
    "--card", $Card,
    "--attempt", $attempt,
    "--code-root", $codeRoot,
    "--out", (Join-Path $evidenceDir "run_result.json"),
    "--run-result-out", (Join-Path $evidenceDir "formula_result.json")
)
Write-Output ("argv " + ($argv -join " "))
$p = Start-Process -FilePath $python -ArgumentList $argv -WorkingDirectory $attempt -NoNewWindow -Wait -PassThru `
    -RedirectStandardOutput (Join-Path $evidenceDir "stdout.txt") `
    -RedirectStandardError (Join-Path $evidenceDir "stderr.txt")
Write-Output ("raw_rc=" + $p.ExitCode)
exit $p.ExitCode
