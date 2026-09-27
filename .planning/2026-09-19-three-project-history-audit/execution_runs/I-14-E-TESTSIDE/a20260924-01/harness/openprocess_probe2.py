"""Diagnostic: characterize the PROCESS_ALL_ACCESS denial (evidence for
oracle-addendum-C).  Compares three spawnee classes."""

from __future__ import annotations

import ctypes
import json
import subprocess
import sys
import time

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
OpenProcess = k32.OpenProcess
OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
OpenProcess.restype = ctypes.c_void_p
CloseHandle = k32.CloseHandle

MASKS = {
    "ALL_ACCESS_1F0FFF": 0x1F0FFF,
    "ALL_ACCESS_1FFFFF": 0x1FFFFF,
    "QUERY_INFORMATION": 0x0400,
    "QUERY_LIMITED": 0x1000,
    "TERMINATE": 0x0001,
    "DUP_HANDLE": 0x0040,
}


def try_open(tag: str, pid: int) -> dict:
    row = {"target": tag, "pid": pid}
    for name, mask in MASKS.items():
        handle = OpenProcess(mask, False, pid)
        row[name] = hex(handle) if handle else f"denied/winerror={ctypes.get_last_error()}"
        if handle:
            CloseHandle(handle)
    return row


def main() -> int:
    rows = []
    # 1. an unrelated, same-user process that this session did not spawn
    out = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                          "(Get-Process -Name explorer | Select-Object -First 1).Id"],
                         capture_output=True, text=True, encoding="utf-8")
    try:
        rows.append(try_open("explorer (not spawned by this session)",
                             int(out.stdout.strip().splitlines()[-1])))
    except Exception as exc:
        rows.append({"target": "explorer", "error": str(exc)})

    # 2. a child spawned by this sandboxed python
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(8)"])
    time.sleep(0.6)
    rows.append(try_open("child of sandboxed python", child.pid))
    child.kill()
    child.wait()

    # 3. the same child but probed from ITS OWN powershell (parent-of-child rights)
    script = (
        "$c = Start-Process -FilePath 'C:\\Miniconda\\python.exe' -ArgumentList "
        "@('-c','import time; time.sleep(8)') -WindowStyle Hidden -PassThru; "
        "$h = $null; try { $h = $c.Handle } catch { $h = 'threw' }; "
        "\"pid=$($c.Id) handle=$h\""
    )
    out2 = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                           script], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    line = out2.stdout.strip().splitlines()[-1]
    pid = int(line.split("pid=")[1].split()[0])
    rows.append(try_open("child of powershell (no redirect)", pid))
    rows[-1]["ps_reported"] = line
    subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                    f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
                   capture_output=True)

    print(json.dumps(rows, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
