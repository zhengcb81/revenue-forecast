@echo off
rem I-08-A c3 runner: keeps the argv in a UTF-8 file so non-ASCII paths survive
rem the PowerShell/GBK console. Writes raw stdout/stderr with byte-faithful
rem cmd redirection (NOT PowerShell UTF-16 redirection).
setlocal
set "ATTEMPT=%~dp0.."
set "PY=%ATTEMPT%\iso\venv\Scripts\python.exe"
set "OUT=%ATTEMPT%\after\c3_probe.stdout.txt"
set "ERR=%ATTEMPT%\after\c3_probe.stderr.txt"
cd /d "%ATTEMPT%\iso"
"%PY%" -X utf8 -B probe_attestation.py 1> "%OUT%" 2> "%ERR%"
exit /b %ERRORLEVEL%
