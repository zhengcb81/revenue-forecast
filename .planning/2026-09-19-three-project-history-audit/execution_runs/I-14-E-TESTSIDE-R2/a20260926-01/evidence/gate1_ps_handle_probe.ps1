
$ErrorActionPreference = 'Continue'
$py = $args[0]
$log = Join-Path $env:TEMP ('gate1_ps_out_' + $PID + '.log')
$err = Join-Path $env:TEMP ('gate1_ps_err_' + $PID + '.log')
# (2) WITH redirects — the product launcher's own shape (ps1:327-333)
$p = Start-Process -FilePath $py -ArgumentList @('-c','import time; time.sleep(3)') `
    -WorkingDirectory $env:TEMP -WindowStyle Hidden `
    -RedirectStandardOutput $log -RedirectStandardError $err -PassThru
$handleValue = $null
$handleReadError = $null
try { $handleValue = $p.Handle.ToString() } catch { $handleReadError = $_.Exception.Message }
$isNullOrEmpty = [string]::IsNullOrEmpty($handleValue)
Write-Output ('PSREDIRECT pid=' + $p.Id + ' handle_nonnull=' + (-not $isNullOrEmpty) +
    ' handle=' + $handleValue + ' read_error=' + $handleReadError)
try { if (-not $p.HasExited) { $null = $p.Kill(); $null = $p.WaitForExit(5000) } } catch {}
# contrast: WITHOUT redirect
$q = Start-Process -FilePath $py -ArgumentList @('-c','import time; time.sleep(3)') `
    -WorkingDirectory $env:TEMP -WindowStyle Hidden -PassThru
$hv2 = $null; $he2 = $null
try { $hv2 = $q.Handle.ToString() } catch { $he2 = $_.Exception.Message }
$n2 = [string]::IsNullOrEmpty($hv2)
Write-Output ('PNOREDIRECT pid=' + $q.Id + ' handle_nonnull=' + (-not $n2) +
    ' handle=' + $hv2 + ' read_error=' + $he2)
try { if (-not $q.HasExited) { $null = $q.Kill(); $null = $q.WaitForExit(5000) } } catch {}
