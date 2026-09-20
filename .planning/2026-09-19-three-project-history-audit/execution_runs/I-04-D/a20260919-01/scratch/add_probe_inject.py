"""Wire the probe-injection hook into the patcher's verdict function (rule-5 test)."""

from __future__ import annotations

import pathlib
import sys

PATCHER = pathlib.Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
    r"\execution_runs\I-04-D\a20260919-01\scratch\patch_i04d.py"
)

OLD = '''    recorded_boot = entry.get("boot_uuid")
    if pid == os.getpid() and recorded_boot == _boot_uuid():
        return _ProbeResult("self")  # rule 1: own incarnation, never spawn a probe
    try:'''
NEW = '''    recorded_boot = entry.get("boot_uuid")
    if pid == os.getpid() and recorded_boot == _boot_uuid():
        return _ProbeResult("self")  # rule 1: own incarnation, never spawn a probe
    injected = _probe_injection(pid)
    if injected is not None:
        # Test-only: a schedule can force one pid's probe to fail so the UNKNOWN
        # branch (ADR-4 rule 5) is reachable without breaking a real probe.
        return _ProbeResult("unknown", "", f"injected:{injected}")
    try:'''
text = PATCHER.read_text(encoding="utf-8")
if OLD not in text:
    print("PATTERN NOT FOUND")
    sys.exit(1)
text = text.replace(OLD, NEW, 1)

OLD2 = '''def _probe_entry_verdict(entry: dict[str, Any], *, probe_timeout: float) -> _ProbeResult:'''
NEW2 = '''def _probe_injection(pid: int) -> str | None:
    """I04D_PROBE_INJECT={"<pid>": "<reason>"} forces an UNKNOWN verdict for that pid."""
    raw = os.environ.get("I04D_PROBE_INJECT")
    if not raw:
        return None
    try:
        payload = json.loads(raw)
    except ValueError:
        return None
    if not isinstance(payload, dict):
        return None
    return payload.get(str(pid))


def _probe_entry_verdict(entry: dict[str, Any], *, probe_timeout: float) -> _ProbeResult:'''
if OLD2 not in text:
    print("PATTERN 2 NOT FOUND")
    sys.exit(1)
text = text.replace(OLD2, NEW2, 1)
PATCHER.write_text(text, encoding="utf-8")
print("probe injection installed")
