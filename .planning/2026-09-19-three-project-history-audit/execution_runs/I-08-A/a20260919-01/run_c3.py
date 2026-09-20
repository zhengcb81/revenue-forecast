"""I-08-A c3 runner (UTF-8 safe).

Runs the read-only behavioural probe in a child process and writes the child's
raw stdout/stderr to the attempt's after/ directory with byte-faithful
redirection.  Using file handles (instead of PowerShell's text pipeline) avoids
the UTF-16 re-encoding and the GBK console mojibake that would otherwise corrupt
non-ASCII paths in the recorded evidence.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent
PY = ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe"
PROBE = ATTEMPT / "iso" / "probe_attestation.py"
AFTER = ATTEMPT / "after"
AFTER.mkdir(parents=True, exist_ok=True)

env = dict(os.environ)
env["PYTHONDONTWRITEBYTECODE"] = "1"
env.pop("REVENUE_ATTESTATION_PROVIDER", None)
env.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)
env.pop("REVENUE_PUBLICATION_REGISTRY", None)

argv = [str(PY), "-X", "utf8", "-B", str(PROBE)]
with (AFTER / "c3_probe.stdout.txt").open("wb") as out, (
    AFTER / "c3_probe.stderr.txt"
).open("wb") as err:
    completed = subprocess.run(argv, cwd=str(ATTEMPT / "iso"), env=env, stdout=out, stderr=err)

print("argv=" + repr(argv))
print("cwd=" + str(ATTEMPT / "iso"))
print("c3_exit=" + str(completed.returncode))
sys.exit(completed.returncode)
