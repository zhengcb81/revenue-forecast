"""Diagnostic: which process-open rights does this sandbox allow, and on which
spawnee?  (Not a band arm — evidence for oracle-addendum-C.)"""

from __future__ import annotations

import ctypes
import subprocess
import sys
import time

k32 = ctypes.WinDLL("kernel32", use_last_error=True)
OpenProcess = k32.OpenProcess
OpenProcess.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_uint32]
OpenProcess.restype = ctypes.c_void_p
CloseHandle = k32.CloseHandle

PROCESS_ALL_ACCESS = 0x1F0FFF
PROCESS_QUERY_LIMITED = 0x1000


def probe(tag: str, pid: int) -> None:
    for name, mask in (("ALL_ACCESS", PROCESS_ALL_ACCESS),
                       ("QUERY_LIMITED", PROCESS_QUERY_LIMITED)):
        handle = OpenProcess(mask, False, pid)
        if handle:
            print(f"{tag} pid={pid} {name}: OK {hex(handle)}")
            CloseHandle(handle)
        else:
            print(f"{tag} pid={pid} {name}: FAIL winerror={ctypes.get_last_error()}")


def main() -> int:
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(8)"])
    time.sleep(0.6)
    probe("python-spawned", child.pid)
    child.kill()
    child.wait()

    script = (
        "Start-Process -FilePath 'C:\\Miniconda\\python.exe' -ArgumentList "
        "@('-c','import time; time.sleep(8)') -WindowStyle Hidden "
        "-RedirectStandardOutput \"$env:TEMP\\op_o.log\" "
        "-RedirectStandardError \"$env:TEMP\\op_e.log\" -PassThru | "
        "ForEach-Object { $_.Id }"
    )
    out = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                          script], capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    pid = int(out.stdout.strip().splitlines()[-1])
    time.sleep(0.6)
    probe("ps-redirect-spawned", pid)
    subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                    f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"],
                   capture_output=True)

    out2 = subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                           "Start-Process -FilePath 'C:\\Miniconda\\python.exe' "
                           "-ArgumentList @('-c','import time; time.sleep(8)') "
                           "-WindowStyle Hidden -PassThru | ForEach-Object { $_.Id }"],
                          capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    pid2 = int(out2.stdout.strip().splitlines()[-1])
    time.sleep(0.6)
    probe("ps-noredirect-spawned", pid2)
    subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                    f"Stop-Process -Id {pid2} -Force -ErrorAction SilentlyContinue"],
                   capture_output=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
