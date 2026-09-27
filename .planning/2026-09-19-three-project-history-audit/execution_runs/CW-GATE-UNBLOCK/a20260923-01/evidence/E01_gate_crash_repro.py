"""E01 - RC-1 repro for CW-GATE-UNBLOCK: gate print path under GBK stdout.

RED (current tools/pre_push_gate.py): _run() prints the child-output tail with
plain print() -> UnicodeEncodeError: 'gbk' codec can't encode '\u05a3' -> crash.
GREEN (fixed gate): payload prints (encoding-safe), and the child's step-failure
rc still propagates: repro exits with the child rc (3), proving rc semantics.

v2: the child reconfigures ITS stdout to utf-8 first, so a REAL non-GBK char
crosses the pipe (the gate decodes child output as utf-8, line 49-50), reaches
tail, and hits print(tail).  v1 failed to be RED because a GBK-locale child's
stderr write backslash-replaces the char (errors='backslashreplace') - see
E00_encoding_probe.log / 01-gate-crash-RED-v1-superseded.log.
"""
import sys
from pathlib import Path

ISO = Path(r"C:\Users\郑曾波\AppData\Local\Temp\cwgu1\repo")
sys.path.insert(0, str(ISO / "tools"))

import pre_push_gate as g  # noqa: E402

# Simulate the Windows GBK console (cp936, strict) on stdout BEFORE entering the
# gate's print path.  The fix must protect the print path itself, not the import.
sys.stdout.reconfigure(encoding="gbk", errors="strict")

child = [
    sys.executable,
    "-c",
    "import sys; sys.stdout.reconfigure(encoding='utf-8'); "
    "sys.stdout.write('payload \\u05a3 ok\\n'); sys.stdout.flush(); sys.exit(3)",
]
rc = g._run(child, "repro-step-non-gbk-payload")  # failing step: rc=3, tail contains real U+05A3
print(f"REPRO-RC={rc}")
sys.exit(rc)
