"""Reviewer-independent re-verification driver for card I-14-F.

Written by the independent reviewer; does NOT import or reuse the implementer's
harness/run_placement.py.  Reproduces the frozen argv shape of oracle.md §0:

  <python> -X utf8 -B -m pytest -p no:cacheprovider --basetemp <run_dir>\\pytest -q
  <tree>/tests/contract/test_source_catalog_worker_bootstrap.py::<node>

cwd = run_dir.  Stripped env (PYTHONDONTWRITEBYTECODE, PYTHONUTF8, PYTHONPATH=<tree>\\src,
PATH, SYSTEMROOT, TEMP, TMP).  Strictly sequential by design (oracle Addendum A #3:
parallel load contaminates the child node).

Phases (all reviewer-owned run dirs, freshly created):
  R  RED      : pristine tree (no conftest.py), deep cwd 166, basetemp 173, logon node
  G  GREEN    : iso tree (with conftest.py),  deep cwd 166, basetemp 173, logon node
  M  MUTATION : iso tree, CW_SHORT_BASETEMP_DISABLE=1, cwd 167/166, basetemp 174/173,
                both nodes
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import shutil
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parent.parent
VENV_PY = ATTEMPT / "iso" / "venv" / "Scripts" / "python.exe"
ISO_TREE = ATTEMPT / "iso" / "tree"
PRISTINE_TREE = ATTEMPT / "rev" / "tree"
REVIEW_DIR = ATTEMPT / "review"
CAPTURES = REVIEW_DIR / "captures"

NODES = {
    "child_without_runtime": "test_child_without_runtime_session_is_terminated_and_restarted",
    "logon_wrapper_quoted": "test_logon_wrapper_detaches_a_live_supervisor_with_quoted_paths",
}
SUITE = "tests/contract/test_source_catalog_worker_bootstrap.py"
DECISION_RE = re.compile(r"CW-BASETEMP-DECISION (\{.*\})")
CLEANUP_RE = re.compile(r"CW-BASETEMP-CLEANUP (\{.*\})")
FALLBACK_ROOT = Path(os.environ["TEMP"]) / "cw-pytest-basetemp"

SIGNATURES = [
    ("WinError206", ("WinError 206",)),
    ("FileNotFound-launcher-events", ("worker_launcher_events.jsonl",)),
    ("timeout15s-band", ("TimeoutExpired", "timed out after")),
]


def classify(text: str, rc: int) -> str:
    if rc == 0:
        return "pass"
    for name, needles in SIGNATURES:
        if any(n in text for n in needles):
            return name
    return "other-failure"


def run_one(phase: str, tag: str, node_id: str, tree: Path, run_dir: Path,
            extra_env: dict[str, str] | None = None) -> dict:
    run_dir.mkdir(parents=True)
    basetemp = run_dir / "pytest"
    decision_file = run_dir / "basetemp_decision.json"
    env = {
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONUTF8": "1",
        "PYTHONPATH": str(tree / "src"),
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "TEMP": os.environ.get("TEMP", ""),
        "TMP": os.environ.get("TMP", ""),
        "CW_BASETEMP_DECISION_FILE": str(decision_file),
    }
    env.update(extra_env or {})
    argv = [
        str(VENV_PY), "-X", "utf8", "-B", "-m", "pytest", "-p", "no:cacheprovider",
        "--basetemp", str(basetemp), "-q",
        f"{tree / SUITE}::{NODES[node_id]}",
    ]
    proc = subprocess.run(argv, cwd=str(run_dir), stdout=subprocess.PIPE,
                          stderr=subprocess.STDOUT, env=env, timeout=300)
    text = proc.stdout.decode("utf-8", "replace")
    (run_dir / "stdout.txt").write_text(text, encoding="utf-8")
    (run_dir / "returncode.txt").write_text(str(proc.returncode), encoding="utf-8")
    decision = None
    match = DECISION_RE.search(text)
    if match:
        decision = json.loads(match.group(1))
    cleanup = None
    cmatch = CLEANUP_RE.search(text)
    if cmatch:
        cleanup = json.loads(cmatch.group(1))
    row = {
        "phase": phase,
        "tag": tag,
        "node": node_id,
        "tree": str(tree),
        "cwd": str(run_dir),
        "cwd_len": len(str(run_dir)),
        "basetemp": str(basetemp),
        "basetemp_len": len(str(basetemp)),
        "rc": proc.returncode,
        "signature": classify(text, proc.returncode),
        "decision": decision,
        "cleanup": cleanup,
        "last_line": text.strip().splitlines()[-1] if text.strip() else "",
    }
    # bring the raw capture into the attempt (stdout already written in run_dir,
    # which for mutation lives under %TEMP%)
    if not str(run_dir).startswith(str(ATTEMPT)):
        CAPTURES.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(run_dir / "stdout.txt", CAPTURES / f"{phase}-{tag}-stdout.txt")
        row["capture_copied_to"] = str(CAPTURES / f"{phase}-{tag}-stdout.txt")
    print(json.dumps({k: row[k] for k in
                      ("phase", "tag", "node", "cwd_len", "basetemp_len", "rc", "signature")},
                     ensure_ascii=False), flush=True)
    return row


def main() -> int:
    phases = sys.argv[1:] or ["R", "G", "M"]
    rows: list[dict] = []

    if "R" in phases or "G" in phases:
        # --- geometry: attempt root is 122 chars; review\deep\pad55 is 140 chars ---
        deep_root = REVIEW_DIR / "deep" / "pad55"
        if not deep_root.exists():
            deep_root.mkdir(parents=True, exist_ok=True)
        assert len(str(deep_root)) == 140, len(str(deep_root))

    if "R" in phases:
        # R: RED, pristine tree, cwd 166 / basetemp 173
        rows.append(run_one("R-red", "P0-logon_wrapper_quoted-1", "logon_wrapper_quoted",
                            PRISTINE_TREE, deep_root / "P0-logon_wrapper_quoted-1"))

    if "G" in phases:
        # G: GREEN, iso tree, cwd 166 / basetemp 173
        rows.append(run_one("G-green", "R1-logon_wrapper_quoted-1", "logon_wrapper_quoted",
                            ISO_TREE, deep_root / "R1-logon_wrapper_quoted-1"))

    if "M" in phases:
        # M: MUTATION, iso tree, disable env, cwd 167 / 166
        # TEMP(31) + "\i14f-rev-mut"(13) + "\"(1) + pad(95) = 140
        pad = "a" * 95
        mut_root = Path(os.environ["TEMP"]) / "i14f-rev-mut" / pad
        assert len(str(mut_root)) == 140, len(str(mut_root))
        if mut_root.exists():
            shutil.rmtree(mut_root)
        mut_root.mkdir(parents=True)
        assert len(str(mut_root / "P0-logon_wrapper_quoted-1")) == 166, \
            len(str(mut_root / "P0-logon_wrapper_quoted-1"))
        assert len(str(mut_root / "P0-child_without_runtime-1")) == 167, \
            len(str(mut_root / "P0-child_without_runtime-1"))
        dis = {"CW_SHORT_BASETEMP_DISABLE": "1"}
        rows.append(run_one("M-mut", "P0-logon_wrapper_quoted-1", "logon_wrapper_quoted",
                            ISO_TREE, mut_root / "P0-logon_wrapper_quoted-1", dis))
        rows.append(run_one("M-mut", "P0-child_without_runtime-1", "child_without_runtime",
                            ISO_TREE, mut_root / "P0-child_without_runtime-1", dis))

    print("\n--- fallback root contents after all phases ---")
    print(FALLBACK_ROOT, "exists:", FALLBACK_ROOT.exists(),
          "entries:", [p.name for p in FALLBACK_ROOT.iterdir()] if FALLBACK_ROOT.exists() else None)
    out = REVIEW_DIR / "reviewer_runs.json"
    prior = []
    if out.exists():
        try:
            prior = json.loads(out.read_text(encoding="utf-8")).get("rows", [])
        except json.JSONDecodeError:
            prior = []
    allrows = prior + rows
    out.write_text(json.dumps({"rows": allrows, "fallback_root": str(FALLBACK_ROOT),
                               "fallback_root_leftovers":
                                   [p.name for p in FALLBACK_ROOT.iterdir()]
                                   if FALLBACK_ROOT.exists() else []},
                              indent=2, ensure_ascii=False), encoding="utf-8")
    print("summary:", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
