# -*- coding: utf-8 -*-
"""I-14-E-TESTSIDE-R2 — Gate -1 capability probe (runs BEFORE the oracle freeze).

Blocker being re-tested (from I-14-E-TESTSIDE/a20260924-01, reviewer VERDICT=blocked):
  ENV-OPENPROCESS-ALLACCESS-DENIED — this class of session could not obtain a
  PROCESS_ALL_ACCESS handle, so PowerShell ``Start-Process -RedirectStandard*``
  returned a Process whose ``.Handle`` is null, and the product launcher
  (source_catalog_worker.ps1:340-341, ``[CompanyWiki.KillOnCloseJob]::Assign``)
  threw before the watchdog ever ran.

Discipline 19: the parent's escalated probe succeeded (self pid=4028 ok=True
lasterr=0; child ok=True lasterr=0; VERDICT=UNBLOCKED, 2026-09-26 17:5x) but
"parent escalated OK" does NOT imply "this session OK" — so this probe is the
authoritative gate for THIS session.

Four steps per dispatch: spawn -> open -> close -> wait, for self + own child,
mask PROCESS_ALL_ACCESS (0x1F0FFF), with QUERY_LIMITED_INFORMATION (0x1000) as a
control.  Plus reviewer S8-1 criterion (2): PowerShell Start-Process with
-RedirectStandardOutput/-RedirectStandardError -PassThru must expose a non-null
.Handle (the exact product mechanism), with a no-redirect contrast row.

Writes: nothing outside this attempt's evidence/ dir (given via argv[1]) and the
OS temp scratch for the PS child logs.  No product bytes touched.
"""
from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000
k32 = ctypes.WinDLL("kernel32", use_last_error=True)
k32.OpenProcess.restype = wintypes.HANDLE
k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
k32.CloseHandle.argtypes = [wintypes.HANDLE]
k32.CloseHandle.restype = wintypes.BOOL

PS_HANDLE_PROBE = r"""
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
"""


def open_probe(pid: int, mask: int) -> dict:
    """Steps open -> close on one pid. rc = raw handle value (0 = failed)."""
    handle = k32.OpenProcess(mask, False, pid)
    lasterr = ctypes.get_last_error()
    ok = bool(handle)
    closed = None
    if ok:
        closed = bool(k32.CloseHandle(handle))
    return {
        "pid": pid,
        "mask": f"0x{mask:X}",
        "open_ok": ok,
        "rc": int(handle or 0),
        "lasterr": lasterr,
        "close_ok": closed,
    }


def main() -> int:
    evidence = Path(sys.argv[1])
    evidence.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    def emit(text: str) -> None:
        lines.append(text)
        print(text, flush=True)

    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    emit(f"GATE1 session_pid={os.getpid()} python={sys.version.split()[0]} "
         f"started_utc={started}")

    # step 1: spawn own child
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(8)"])
    emit(f"STEP1 spawn child pid={child.pid}")

    # steps 2-3: open + close
    rows = [
        open_probe(os.getpid(), PROCESS_ALL_ACCESS),                   # self, ALL_ACCESS
        open_probe(child.pid, PROCESS_ALL_ACCESS),                     # child, ALL_ACCESS
        open_probe(os.getpid(), PROCESS_QUERY_LIMITED_INFORMATION),    # control
        open_probe(child.pid, PROCESS_QUERY_LIMITED_INFORMATION),      # control
    ]
    for row in rows:
        emit("STEP2-3 " + json.dumps(row, ensure_ascii=False))

    # step 4: wait child
    child.wait(timeout=30)
    emit(f"STEP4 wait child rc={child.returncode}")

    # S8-1 criterion (2): the actual product mechanism (Start-Process + redirect)
    ps_script = evidence / "gate1_ps_handle_probe.ps1"
    ps_script.write_text(PS_HANDLE_PROBE, encoding="utf-8")
    proc = subprocess.run(
        ["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy",
         "Bypass", "-File", str(ps_script), sys.executable],
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding="utf-8", errors="replace", timeout=60,
    )
    ps_rows = {}
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if line.startswith("PSREDIRECT "):
            ps_rows["with_redirect"] = line
        elif line.startswith("PNOREDIRECT "):
            ps_rows["no_redirect_contrast"] = line
    emit(f"STEP5 ps rc={proc.returncode}")
    for key in ("with_redirect", "no_redirect_contrast"):
        emit(f"STEP5 {key}: {ps_rows.get(key, '<missing>')}")

    def ok_of(row_key: str) -> bool:
        text = ps_rows.get(row_key, "")
        return "handle_nonnull=True" in text

    self_ok = rows[0]["open_ok"] and rows[0]["lasterr"] == 0
    child_ok = rows[1]["open_ok"] and rows[1]["lasterr"] == 0
    ps_ok = ok_of("with_redirect")
    verdict = "UNBLOCKED" if (self_ok and child_ok and ps_ok) else "STILL_BLOCKED"
    emit(f"SELF_ALL_ACCESS_ok={self_ok} CHILD_ALL_ACCESS_ok={child_ok} "
         f"PS_REDIRECT_HANDLE_ok={ps_ok}")
    emit(f"VERDICT: {verdict}")
    if verdict == "STILL_BLOCKED":
        emit("DISPOSITION: stop immediately; report blocked (qualified result); "
             "no destructive substitute permitted.")

    payload = {
        "probe": "harness/gate1_openprocess_probe.py",
        "card": "I-14-E-TESTSIDE-R2",
        "started_utc": started,
        "finished_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "steps": rows,
        "child_wait_rc": child.returncode,
        "ps_probe_rc": proc.returncode,
        "ps_probe_raw": (proc.stdout or "").splitlines(),
        "self_all_access_ok": self_ok,
        "child_all_access_ok": child_ok,
        "ps_redirect_handle_ok": ps_ok,
        "verdict": verdict,
    }
    out = evidence / "gate-1-openprocess-result.json"
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (evidence / "gate-1-openprocess-raw.txt").write_text(
        "\n".join(lines) + "\n", encoding="utf-8")
    print(f"out: {out}")
    return 0 if verdict == "UNBLOCKED" else 2


if __name__ == "__main__":
    sys.exit(main())
