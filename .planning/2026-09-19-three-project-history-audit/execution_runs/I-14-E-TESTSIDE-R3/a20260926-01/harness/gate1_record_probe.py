"""I-14-E-TESTSIDE-R3 gate -1 record-only capability probe (NOT a gate).

The R3 dispatch narrowed gate -1 to "directly run the three-arm pytest"; this
probe only records the two S8-1 capability shapes for the evidence trail
(criteria themselves are applied by actually running pytest):

  S8-1-1  ctypes OpenProcess(0x1F0FFF) on self and on an own child
  S8-1-2  powershell Start-Process -RedirectStandard* -PassThru .Handle non-null

Raw output goes to stdout verbatim; nothing here decides pass/fail.
"""

from __future__ import annotations

import ctypes
import json
import os
import subprocess
import sys
import time

PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_QUERY_LIMITED_INFORMATION = 0x1000


def open_probe(pid: int, mask: int) -> dict:
    k32 = ctypes.WinDLL("kernel32", use_last_error=True)
    k32.OpenProcess.restype = ctypes.c_void_p
    handle = k32.OpenProcess(mask, False, pid)
    err = ctypes.get_last_error()
    close_ok = None
    if handle:
        close_ok = bool(k32.CloseHandle(ctypes.c_void_p(handle)))
    return {"pid": pid, "mask": hex(mask), "open_ok": bool(handle),
            "rc": int(handle or 0), "lasterr": err, "close_ok": close_ok}


def main() -> int:
    started = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    print(f"GATE1-RECORD session_pid={os.getpid()} python={sys.version.split()[0]} "
          f"started_utc={started}")
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(3)"])
    print(f"STEP1 spawn child pid={child.pid}")
    for pid in (os.getpid(), child.pid):
        print("STEP2-3 " + json.dumps(open_probe(pid, PROCESS_ALL_ACCESS)))
    for pid in (os.getpid(), child.pid):
        print("STEP2-3 " + json.dumps(open_probe(pid, PROCESS_QUERY_LIMITED_INFORMATION)))
    rc = child.wait()
    print(f"STEP4 wait child rc={rc}")

    out_path = os.path.join(os.environ.get("TEMP", "."), "g1probe_out.txt")
    err_path = os.path.join(os.environ.get("TEMP", "."), "g1probe_err.txt")
    ps = (
        "$o = Start-Process -FilePath powershell.exe -ArgumentList '-NoProfile','-Command',"
        "'Start-Sleep -Seconds 2' -RedirectStandardOutput "
        f"'{out_path}' -RedirectStandardError "
        f"'{err_path}' -PassThru; "
        "try { $h = $o.Handle; if ($null -eq $h) { Write-Output 'PSREDIRECT handle_nonnull=False' } "
        "else { Write-Output ('PSREDIRECT handle_nonnull=True handle=' + $h) } } "
        "catch { Write-Output ('PSREDIRECT handle_nonnull=False read_error=' + $_.Exception.Message) }; "
        "$o2 = Start-Process -FilePath powershell.exe -ArgumentList '-NoProfile','-Command',"
        "'Start-Sleep -Seconds 2' -PassThru; "
        "try { $h2 = $o2.Handle; if ($null -eq $h2) { Write-Output 'PNOREDIRECT handle_nonnull=False' } "
        "else { Write-Output ('PNOREDIRECT handle_nonnull=True handle=' + $h2) } } "
        "catch { Write-Output ('PNOREDIRECT handle_nonnull=False read_error=' + $_.Exception.Message) }"
    )
    out = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", ps],
                         capture_output=True, text=True, encoding="utf-8", errors="replace")
    print(f"STEP5 ps rc={out.returncode}")
    for line in (out.stdout or "").splitlines():
        if line.strip():
            print("STEP5 " + line.strip())
    if out.stderr and out.stderr.strip():
        print("STEP5 stderr: " + out.stderr.strip()[:500])
    return 0


if __name__ == "__main__":
    sys.exit(main())
