"""I-09-C fault-injection harness — shared helpers (test-built code only).

This module never modifies product files.  All state lives under the attempt
directory (allowed_write_roots = this attempt only).
"""
from __future__ import annotations

import copy
import ctypes
import datetime
import hashlib
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
ISO_RF = ATTEMPT / "iso" / "rf"
SCRIPTS = ISO_RF / "scripts"
TESTS = ISO_RF / "tests"
PY = ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe"

# Harness kill exit code: a process terminated by this card exits with 4242.
# Any other non-zero code is the product's own exit code (e.g. 2).
KILL_EXIT_CODE = 4242


def setup_paths() -> None:
    for p in (str(SCRIPTS), str(TESTS), str(HERE)):
        if p not in sys.path:
            sys.path.insert(0, p)


def write_json(path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(obj, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def append_jsonl(path, obj) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as fh:
        fh.write(json.dumps(obj, ensure_ascii=False, default=str) + "\n")


def sha256_file(path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def now() -> float:
    return time.time()


def hard_kill(pid: int, code: int = KILL_EXIT_CODE) -> dict:
    """Real process termination (TerminateProcess) — Python finally blocks do
    NOT run.  Callers must have verified the PID is present in this run's
    new_run manifest (pid_<pid>.json) before calling."""
    PROCESS_TERMINATE = 0x0001
    k32 = ctypes.windll.kernel32
    handle = k32.OpenProcess(PROCESS_TERMINATE, False, int(pid))
    if not handle:
        return {"ok": False, "pid": pid, "error": "OpenProcess failed"}
    try:
        ok = bool(k32.TerminateProcess(handle, int(code)))
        return {"ok": bool(ok), "pid": int(pid), "exit_code_set": int(code)}
    finally:
        k32.CloseHandle(handle)


def make_input_docs(dest_dir) -> dict:
    """P0/P1: byte-identical across every case (same P0/P1 inputs, per card).

    P0 = the previous complete package (as_of_date shifted FORWARD one day —
    requests differing only in as_of_date are distinct identities, the frozen
    c09/c10 pattern.  Measured: shifting BACKWARD one day breaks validation
    with "claim verification date is outside the allowed information set"
    because the fixture's evidence claims are verified at the original date;
    a later as_of keeps every claim inside the allowed information set — the
    first attempt's rejection is preserved in this comment, not hidden).
    P1 = the package under fault (fixture date).
    """
    setup_paths()
    from test_recognition_bridge import forecast_document  # noqa: E402

    dest = Path(dest_dir)
    dest.mkdir(parents=True, exist_ok=True)
    base = forecast_document()
    p1 = copy.deepcopy(base)
    p0 = copy.deepcopy(base)
    asof = base.get("as_of_date")
    if not isinstance(asof, str):
        raise RuntimeError(f"forecast_document() has no as_of_date: {asof!r}")
    day = datetime.date.fromisoformat(asof[:10])
    p0["as_of_date"] = (day + datetime.timedelta(days=1)).isoformat()
    paths = {}
    for name, doc in (("p0", p0), ("p1", p1)):
        path = dest / f"input_{name}.json"
        path.write_text(json.dumps(doc, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        paths[name] = str(path)
    return paths


# Case-level evidence helpers -------------------------------------------------

def case_dir(case_id: str) -> Path:
    return ATTEMPT / "evidence" / "cases" / case_id


def registry_path_for(case_id: str) -> Path:
    return case_dir(case_id) / "state" / "registry" / "publications.jsonl"


def child_env(registry) -> dict:
    import os

    env = dict(os.environ)
    env["REVENUE_PUBLICATION_REGISTRY"] = str(registry)
    env["PYTHONIOENCODING"] = "utf-8"
    env.pop("REVENUE_ATTESTATION_PROVIDER", None)
    env.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)
    return env
