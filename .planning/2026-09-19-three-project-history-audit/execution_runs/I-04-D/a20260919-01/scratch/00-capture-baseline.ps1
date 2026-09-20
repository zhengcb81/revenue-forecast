$ErrorActionPreference = "Continue"
$P = "C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
$A = "$P\execution_runs\I-04-D\a20260919-01"

"=== git heads / porcelain (captured BEFORE any edit) ===" | Set-Content -LiteralPath "$A\before\00-git-heads.txt" -Encoding UTF8
foreach ($r in @("filing-fetch","company-wiki","revenue-forecast")) {
  $d = "C:\Users\郑曾波\Projects\$r"
  Add-Content -LiteralPath "$A\before\00-git-heads.txt" -Value "--- $r ---" -Encoding UTF8
  Add-Content -LiteralPath "$A\before\00-git-heads.txt" -Value ("HEAD " + (& git -C $d rev-parse HEAD 2>&1)) -Encoding UTF8
  Add-Content -LiteralPath "$A\before\00-git-heads.txt" -Value "porcelain:" -Encoding UTF8
  (& git -C $d status --porcelain 2>&1) | ForEach-Object { Add-Content -LiteralPath "$A\before\00-git-heads.txt" -Value ("  " + $_) -Encoding UTF8 }
}

"=== read-only anchor hashes (BEFORE any edit) ===" | Set-Content -LiteralPath "$A\before\01-anchor-hashes.txt" -Encoding UTF8
$targets = @(
  @{n="production filing-fetch/scripts/fetch_filing.py"; p="C:\Users\郑曾波\Projects\filing-fetch\scripts\fetch_filing.py"},
  @{n="production company-wiki/src/company_wiki/source_catalog/control.py"; p="C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\control.py"},
  @{n="production company-wiki/src/company_wiki/source_catalog/store.py"; p="C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\store.py"},
  @{n="production company-wiki/src/company_wiki/source_catalog/cli.py"; p="C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\cli.py"},
  @{n="production company-wiki/src/company_wiki/source_catalog/lock.py"; p="C:\Users\郑曾波\Projects\company-wiki\src\company_wiki\source_catalog\lock.py"},
  @{n="iso baseline I-04-B/iso/.../fetch_filing.py"; p="$P\execution_runs\I-04-B\a20260919-01\iso\filing-fetch\scripts\fetch_filing.py"},
  @{n="iso baseline I-04-B/iso/.../test_fetch_filing.py"; p="$P\execution_runs\I-04-B\a20260919-01\iso\filing-fetch\tests\test_fetch_filing.py"},
  @{n="iso copy (this attempt) fetch_filing.py"; p="$A\iso\filing-fetch\scripts\fetch_filing.py"}
)
foreach ($t in $targets) {
  if (Test-Path -LiteralPath $t.p) {
    $h = (Get-FileHash -LiteralPath $t.p -Algorithm SHA256).Hash.ToLower()
    $len = (Get-Item -LiteralPath $t.p).Length
    Add-Content -LiteralPath "$A\before\01-anchor-hashes.txt" -Value ("{0}`n  sha256={1}`n  bytes={2}" -f $t.n, $h, $len) -Encoding UTF8
  } else {
    Add-Content -LiteralPath "$A\before\01-anchor-hashes.txt" -Value ("{0}`n  MISSING" -f $t.n) -Encoding UTF8
  }
}

"=== catalog invariant (BEFORE any edit) ===" | Set-Content -LiteralPath "$A\before\02-catalog-invariant.txt" -Encoding UTF8
$db = "C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3"
$wal = "C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3-wal"
$i = Get-Item -LiteralPath $db
Add-Content -LiteralPath "$A\before\02-catalog-invariant.txt" -Value ("catalog.sqlite3 bytes={0} mtime_utc={1}" -f $i.Length, $i.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")) -Encoding UTF8
$w = Get-Item -LiteralPath $wal
Add-Content -LiteralPath "$A\before\02-catalog-invariant.txt" -Value ("catalog.sqlite3-wal bytes={0} mtime_utc={1}" -f $w.Length, $w.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")) -Encoding UTF8

"=== reviews mtime (BEFORE any edit) ===" | Set-Content -LiteralPath "$A\before\03-reviews-mtime.txt" -Encoding UTF8
$rv = "$P\reviews"
Add-Content -LiteralPath "$A\before\03-reviews-mtime.txt" -Value ("reviews dir mtime_utc=" + (Get-Item -LiteralPath $rv).LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")) -Encoding UTF8
Get-ChildItem -LiteralPath $rv -Force | ForEach-Object { Add-Content -LiteralPath "$A\before\03-reviews-mtime.txt" -Value ("  " + $_.Name + " mtime_utc=" + $_.LastWriteTimeUtc.ToString("yyyy-MM-ddTHH:mm:ssZ")) -Encoding UTF8 }

"=== anchor relocation (current line numbers vs card line numbers) ===" | Set-Content -LiteralPath "$A\evidence\anchor-relocation.txt" -Encoding UTF8
$prod = "C:\Users\郑曾波\Projects\filing-fetch\scripts\fetch_filing.py"
Add-Content -LiteralPath "$A\evidence\anchor-relocation.txt" -Value "PRODUCTION $prod" -Encoding UTF8
Select-String -LiteralPath $prod -Pattern '^class PausedWorkerScope|^    def __enter__|^    def _register|^    def _unregister|^    def __exit__|^def _pid_is_alive|^def _read_pause_entries|^def _write_pause_entries|^def _prune_pause_entries|^    def _remaining' -Encoding UTF8 | ForEach-Object { Add-Content -LiteralPath "$A\evidence\anchor-relocation.txt" -Value ("  L{0}: {1}" -f $_.LineNumber, $_.Line.Trim()) -Encoding UTF8 }
$iso = "$A\iso\filing-fetch\scripts\fetch_filing.py"
Add-Content -LiteralPath "$A\evidence\anchor-relocation.txt" -Value "ISO BASELINE (I-04-B output) $iso" -Encoding UTF8
Select-String -LiteralPath $iso -Pattern '^class PausedWorkerScope|^    def __enter__|^    def _register|^    def _unregister|^    def __exit__|^def _pid_is_alive|^def _read_pause_entries|^def _write_pause_entries|^def _prune_pause_entries|^    def _request_remaining|^    def _cleanup_timeout' -Encoding UTF8 | ForEach-Object { Add-Content -LiteralPath "$A\evidence\anchor-relocation.txt" -Value ("  L{0}: {1}" -f $_.LineNumber, $_.Line.Trim()) -Encoding UTF8 }

"done"
Get-Content -LiteralPath "$A\before\01-anchor-hashes.txt" -Encoding UTF8
Get-Content -LiteralPath "$A\evidence\anchor-relocation.txt" -Encoding UTF8