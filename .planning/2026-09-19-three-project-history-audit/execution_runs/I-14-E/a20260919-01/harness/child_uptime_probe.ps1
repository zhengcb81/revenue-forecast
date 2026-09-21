param(
    [Parameter(Mandatory = $true)][string]$PythonExe,
    [Parameter(Mandatory = $true)][string]$ProjectRoot,
    [Parameter(Mandatory = $true)][string]$OutPath
)

# I-14-E probe: reproduce the supervisor's launch sequence and its uptime definition
# (source_catalog_worker.ps1: $StartedAt before Start-Process, -WindowStyle Hidden,
# stdout/stderr redirected into .source_catalog, handle materialised before the wait).
# It measures ONE child launch and writes the result as JSON; it runs no watchdog.
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $ProjectRoot
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'

$Catalog = Join-Path $ProjectRoot '.source_catalog'
New-Item -ItemType Directory -Path $Catalog -Force | Out-Null
$Arguments = @(
    '-m', 'company_wiki.source_catalog.cli',
    '--config', (Join-Path $ProjectRoot 'config/source_catalog.yaml'),
    'worker',
    '--worker-config', (Join-Path $ProjectRoot 'config/source_catalog_worker.yaml')
)

$StartedAt = Get-Date
$Child = Start-Process `
    -FilePath $PythonExe `
    -ArgumentList $Arguments `
    -WorkingDirectory $ProjectRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $Catalog 'probe_out.log') `
    -RedirectStandardError (Join-Path $Catalog 'probe_err.log') `
    -PassThru
$ChildHandle = $Child.Handle
$null = $Child.WaitForExit(60000)
$Child.Refresh()
$Uptime = ((Get-Date) - $StartedAt).TotalSeconds

[ordered]@{
    uptime_seconds = [math]::Round($Uptime, 3)
    exit_code      = [int]$Child.ExitCode
    child_pid      = $Child.Id
    started_at     = $StartedAt.ToUniversalTime().ToString('o')
} | ConvertTo-Json -Compress | Set-Content -LiteralPath $OutPath -Encoding UTF8
exit 0
