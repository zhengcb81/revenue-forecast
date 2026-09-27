"""E00 - encoding-chain probe (why E01-v1 did not crash)."""
import os
import subprocess
import sys

print("parent stdout:", repr(sys.stdout.encoding), repr(getattr(sys.stdout, "errors", None)))
print("parent stderr:", repr(sys.stderr.encoding), repr(getattr(sys.stderr, "errors", None)))
print("PYTHONIOENCODING:", repr(os.environ.get("PYTHONIOENCODING")),
      "PYTHONUTF8:", repr(os.environ.get("PYTHONUTF8")))

# Probe 1: does reconfigure(gbk, strict) actually crash on U+05A3?
try:
    sys.stdout.reconfigure(encoding="gbk", errors="strict")
    sys.stdout.write("X\u05a3Y\n")
    print("PROBE1-NO-CRASH")
except UnicodeEncodeError as exc:
    print(f"PROBE1-CRASH {exc}")  # via stderr-safe path? no: stderr separately configured

# Probe 2: what does a child's stdout/stderr carry for U+05A3?
child = [sys.executable, "-c",
         "import sys; sys.stderr.write('E\\u05a3F\\n'); sys.stderr.flush(); "
         "sys.stdout.write('O\\u05a3G\\n'); sys.stdout.flush()"]
r = subprocess.run(child, capture_output=True, text=True,
                   encoding="utf-8", errors="replace")
print("child rc:", r.returncode)
print("child stderr repr:", repr(r.stderr))
print("child stdout repr:", repr(r.stdout))
