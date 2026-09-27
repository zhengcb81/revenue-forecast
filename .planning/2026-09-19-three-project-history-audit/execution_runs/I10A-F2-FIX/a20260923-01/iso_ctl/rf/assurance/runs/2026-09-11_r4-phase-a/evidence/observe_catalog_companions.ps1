# R4 A01 boundary evidence: passive observation of the production catalog's SQLite
# companion files (catalog.sqlite3, -shm, -wal) plus a best-effort process probe.
#
# Purpose (A-DR-08): the v0.1 side-effect snapshot covered ONLY the main database
# file, so a write to catalog.sqlite3-shm was invisible to it. This observer records
# all three files at a fixed cadence WITHOUT opening the database (metadata only), so
# that a catalog open can be time-stamped independently of the author's commands.
# Every observed -shm advance has since been attributed (boundary-audit.md sections
# 1-3): this repo's mandatory pre-push gate reads the production catalog read-only,
# and the 22:00 daily task opens it read-only. This script only observes; it never
# opens the DB itself.
#
# It executes no wiki CLI command and opens no database handle.
param(
    [int]$Seconds = 720,
    [int]$IntervalSeconds = 20,
    [string]$OutDir = $PSScriptRoot,
    [string]$CatalogDir = ''
)

$ErrorActionPreference = 'Stop'

# The catalog directory is derived from $env:USERPROFILE instead of being written
# as a literal: this file is UTF-8 without BOM and Windows PowerShell 5.1 decodes
# a -File script in the ANSI code page, which would mangle a non-ASCII user name
# in a literal or in a command-line argument (observed 2026-09-11: every stat came
# back as -1 because the path silently did not resolve).
if ([string]::IsNullOrWhiteSpace($CatalogDir)) {
    $CatalogDir = Join-Path $env:USERPROFILE 'Projects\company-wiki\.source_catalog'
}
if (-not (Test-Path -LiteralPath $CatalogDir)) {
    throw "catalog directory not found: $CatalogDir"
}

$files = @('catalog.sqlite3', 'catalog.sqlite3-shm', 'catalog.sqlite3-wal')
$csv = Join-Path $OutDir 'catalog-companion-observation.csv'
$summary = Join-Path $OutDir 'catalog-companion-observation.json'
$header = 'sample,utc,local,mtime_ns_catalog|shm|wal,size_catalog|shm|wal,matching_processes'
$header | Set-Content -LiteralPath $csv -Encoding utf8

$started = Get-Date
$deadline = $started.AddSeconds($Seconds)
$sample = 0
$rows = @()

while ((Get-Date) -lt $deadline) {
    $sample++
    $now = Get-Date
    $mtimes = @()
    $sizes = @()
    foreach ($name in $files) {
        $p = Join-Path $CatalogDir $name
        if (Test-Path -LiteralPath $p) {
            $item = Get-Item -LiteralPath $p -Force
            $mtimes += $item.LastWriteTimeUtc.Ticks
            $sizes += $item.Length
        }
        else {
            $mtimes += -1
            $sizes += -1
        }
    }
    if ($mtimes[0] -eq -1) {
        throw "main catalog file missing under $CatalogDir"
    }
    $procs = @(Get-CimInstance Win32_Process -ErrorAction SilentlyContinue |
        Where-Object { $_.CommandLine -and $_.CommandLine -match 'company_wiki|source_catalog' } |
        ForEach-Object { "$($_.ProcessId):$($_.Name)" })
    $procField = ($procs -join '|')
    $row = [pscustomobject]@{
        sample    = $sample
        utc       = $now.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
        local     = $now.ToString('yyyy-MM-dd HH:mm:ss.fff')
        mtimes    = ($mtimes -join '|')
        sizes     = ($sizes -join '|')
        processes = $procField
    }
    $rows += $row
    "$sample,$($row.utc),$($row.local),$($row.mtimes),$($row.sizes),$procField" |
        Add-Content -LiteralPath $csv -Encoding utf8
    Start-Sleep -Seconds $IntervalSeconds
}

$changes = @()
for ($i = 1; $i -lt $rows.Count; $i++) {
    if ($rows[$i].mtimes -ne $rows[$i - 1].mtimes) {
        $changes += [pscustomobject]@{
            from_sample = $rows[$i - 1].sample
            to_sample   = $rows[$i].sample
            from_utc    = $rows[$i - 1].utc
            to_utc      = $rows[$i].utc
            from_mtime  = $rows[$i - 1].mtimes
            to_mtime    = $rows[$i].mtimes
        }
    }
}

[pscustomobject]@{
    started_utc         = $started.ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    finished_utc        = (Get-Date).ToUniversalTime().ToString('yyyy-MM-ddTHH:mm:ss.fffZ')
    seconds             = $Seconds
    interval_seconds    = $IntervalSeconds
    samples             = $rows.Count
    catalog_dir         = $CatalogDir
    files               = $files
    distinct_mtime_sets = ($rows | Select-Object -ExpandProperty mtimes -Unique).Count
    transitions         = $changes
    process_probe       = ($rows | Select-Object -ExpandProperty processes -Unique)
    cli_commands_run    = 0
    database_opened     = $false
} | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath $summary -Encoding utf8

Write-Output "samples=$($rows.Count) transitions=$($changes.Count) summary=$summary"
