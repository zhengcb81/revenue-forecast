# CFI14FR1-SAMPLE — run03: failure-attribution controls (label 03_<stem>_rerun) + redirect probe (label 04_redirect_probe)
# Control rule (oracle A4 / commands.json CF-c2): for EACH failing file of 02_rerun, re-run that file
# ALONE with the hook redirect DISABLED (CW_SHORT_BASETEMP_DISABLE=1, the conftest disable env read at
# freeze) and the SAME --basetemp; verdict pre-existing vs hook-induced from the delta.
# Probe (oracle A2 / commands.json CF-c3): the 84-char over-budget basetemp must trigger
# relocated=true + cleanup removed=true and the requested dir must never be created.
# Launched DETACHED (Start-Process) so it does not depend on the harness job registry.
$ErrorActionPreference = 'Continue'
$att = 'C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit\execution_runs\CFI14FR1-SAMPLE\a20260922-01'
$ev = "$att\evidence"
$cw = 'C:\Users\郑曾波\Projects\company-wiki'
Set-Location -LiteralPath $cw
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONPYCACHEPREFIX = "$env:TEMP\cf14fr1-pycache"
$bt = 'C:\Users\郑曾波\AppData\Local\Temp\cf14fr1-with-hook'
$index = @()
$index += "controls_started_utc=$((Get-Date).ToUniversalTime().ToString('o'))"
$files = @(
  'tests/contract/test_fc1204_complexity_ratchet.py',
  'tests/contract/test_source_catalog_archive_retired.py',
  'tests/contract/test_source_catalog_parser_liveness.py',
  'tests/contract/test_source_catalog_prune_retired.py',
  'tests/contract/test_zr409_fourth_root_real_journeys.py'
)
foreach ($f in $files) {
  $stem = [IO.Path]::GetFileNameWithoutExtension($f)
  $label = "03_${stem}_rerun"
  Remove-Item -Recurse -Force $bt -ErrorAction SilentlyContinue
  $env:CW_SHORT_BASETEMP_DISABLE = '1'
  $env:CW_BASETEMP_DECISION_FILE = "$ev\$label.decision.jsonl"
  $sw = [Diagnostics.Stopwatch]::StartNew()
  cmd /c "python -m pytest -q $f --basetemp $bt > $ev\$label.txt 2>&1"
  $rc = $LASTEXITCODE
  $sw.Stop()
  "$rc" | Set-Content "$ev\$label.rc.txt"
  $index += "control|$label|$f|rc=$rc|elapsed_s=$([math]::Round($sw.Elapsed.TotalSeconds,1))"
}
Remove-Item Env:CW_SHORT_BASETEMP_DISABLE -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force $bt -ErrorAction SilentlyContinue
# ---- 04 redirect probe ----
$bt4 = "$env:TEMP\cf14fr1-deep\over-budget-basetemp-for-redirect-probe"
Remove-Item -Recurse -Force $bt4 -ErrorAction SilentlyContinue
$env:CW_BASETEMP_DECISION_FILE = "$ev\04_redirect_probe.decision.jsonl"
$sw = [Diagnostics.Stopwatch]::StartNew()
cmd /c "python -m pytest -q tests/contract/test_short_basetemp_convention.py --basetemp $bt4 > $ev\04_redirect_probe.txt 2>&1"
$rc = $LASTEXITCODE
$sw.Stop()
"$rc" | Set-Content "$ev\04_redirect_probe.rc.txt"
$index += "probe|04_redirect_probe|basetemp_len=$($bt4.Length)|rc=$rc|elapsed_s=$([math]::Round($sw.Elapsed.TotalSeconds,1))"
# ---- post-checks: requested over-budget dir must NOT exist; fallback root listing ----
$post = @()
$post += "basetemp04=$bt4"
$post += "basetemp04_len=$($bt4.Length)"
$post += "basetemp04_exists_after_run=$(Test-Path $bt4)"
$fr = "$env:TEMP\cw-pytest-basetemp"
$post += "fallback_root=$fr"
if (Test-Path $fr) {
  Get-ChildItem $fr | ForEach-Object { $post += "fallback_entry|$($_.Name)|$($_.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss.fff'))" }
}
$post += "basetemp_main_exists_after_all=$(Test-Path $bt)"
$post += "finished_utc=$((Get-Date).ToUniversalTime().ToString('o'))"
[IO.File]::WriteAllLines("$ev\04_redirect_probe.postcheck.txt", $post, (New-Object System.Text.UTF8Encoding($false)))
$index += "finished_utc=$((Get-Date).ToUniversalTime().ToString('o'))"
[IO.File]::WriteAllLines("$ev\03_controls_index.txt", $index, (New-Object System.Text.UTF8Encoding($false)))
"done" | Set-Content "$ev\03_controls.done.txt"
