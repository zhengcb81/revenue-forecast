# CFI14FR1-SAMPLE — run02 wrapper (label 02_rerun)
# Reason for this re-run (disclosed): label 01b_with_hook was INTERRUPTED at 2026-09-22
# 23:06:02 local when the harness background-job tree was killed (job record vanished,
# completion notification lost; raw output ends mid-line at 8% of the progress buffer,
# no final summary line, no rc/meta). Per the parent's dispatch: re-run the SAME sample
# once under label 02_rerun, keep the interrupted bytes untouched, authoritative result =
# the complete output of this run.
# This wrapper is launched DETACHED (Start-Process) so it does not depend on the
# harness job registry.
$ErrorActionPreference = 'Continue'
$att = 'C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\CFI14FR1-SAMPLE\a20260922-01'
Set-Location -LiteralPath 'C:\Users\郑曾波\Projects\company-wiki'
$env:CW_BASETEMP_DECISION_FILE = "$att\evidence\02_rerun.decision.jsonl"
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPYCACHEPREFIX = "$env:TEMP\cf14fr1-pycache"
Remove-Item Env:CW_SHORT_BASETEMP_DISABLE -ErrorAction SilentlyContinue
"launched_utc=$((Get-Date).ToUniversalTime().ToString('o'))`nworkdir=C:\Users\郑曾波\Projects\company-wiki`nhook=ACTIVE (CW_SHORT_BASETEMP_DISABLE absent)`nbasetemp=C:\Users\郑曾波\AppData\Local\Temp\cf14fr1-with-hook" | Set-Content "$att\evidence\02_rerun.started.txt"
$sw = [Diagnostics.Stopwatch]::StartNew()
cmd /c 'python -m pytest -q tests/contract tests/unit --basetemp C:\Users\郑曾波\AppData\Local\Temp\cf14fr1-with-hook > C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\CFI14FR1-SAMPLE\a20260922-01\evidence\02_rerun.txt 2>&1'
$rc = $LASTEXITCODE
$sw.Stop()
"$rc" | Set-Content "$att\evidence\02_rerun.rc.txt"
"elapsed_seconds=$([math]::Round($sw.Elapsed.TotalSeconds,1))`nfinished_utc=$((Get-Date).ToUniversalTime().ToString('o'))`nexit_code=$rc" | Set-Content "$att\evidence\02_rerun.meta.txt"
