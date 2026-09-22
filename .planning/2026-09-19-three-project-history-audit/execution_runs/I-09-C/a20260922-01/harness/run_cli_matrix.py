"""I-09-C P-C5 CLI / API compatibility matrix (card 按序动作 6).

Every arm runs against a FRESH isolated registry (never the real one):
  M1 formal JSON+Markdown via the real CLI            -> rc 0, committed, consumable
  M2 stdout-only formal                               -> explicitly rejected (I09-E08), rc 2
  M3 --markdown without --output (same rejection)     -> explicitly rejected, rc 2
  M4 direct library API (run_forecast)                -> row has no publication_id =>
                                                         commit_status identity_unknown (not commit-qualified)
  M5 --validate-only                                  -> rc 0, stdout 'valid', ZERO registry rows,
                                                         zero files written
  M6 --validate-only WITH --output                    -> still zero-write (draft path returns
                                                         before any member write)
  M7 snapshot compatibility (create_snapshot)         -> 2 rows (forecast + snapshot), snapshot row
                                                         carries no validation_status, chain intact
Frozen source for the matrix: I-09-A oracle C-12 / F9 / F10 rows + I-09-B's
stdout-only rejection; unsupported combinations must be rejected EXPLICITLY.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (  # noqa: E402
    ATTEMPT, ISO_RF, PY, case_dir, child_env, make_input_docs,
    read_json, sha256_file, write_json,
)

HARNESS = ATTEMPT / "harness"
CASE = "PC5_cli_matrix"
CIRC = case_dir(CASE)
SHARED = ATTEMPT / "evidence" / "shared_inputs"


def fresh_arm(name: str) -> dict:
    d = CIRC / name
    if d.exists():
        for root, dirs, files in os.walk(d):
            for n in files + dirs:
                try:
                    os.chmod(os.path.join(root, n), 0o666)
                except OSError:
                    pass
        shutil.rmtree(d, ignore_errors=True)
    (d / "state").mkdir(parents=True)
    for n in ("input_p0.json", "input_p1.json"):
        shutil.copyfile(SHARED / n, d / "state" / n)
    return {"name": name, "dir": d, "state": d / "state",
            "registry": d / "state" / "registry" / "publications.jsonl"}


def run_cli(arm, argv_extra, timeout=180):
    argv = [str(PY), str(ISO_RF / "scripts" / "revenue_forecast.py")] + argv_extra
    proc = subprocess.run(argv, cwd=str(ISO_RF), env=child_env(arm["registry"]),
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", timeout=timeout)
    return {"argv": argv, "raw_returncode": proc.returncode,
            "stdout": proc.stdout[:2000], "stderr": proc.stderr[:1000]}


def observe(arm, label):
    out = arm["dir"] / f"{label}.json"
    subprocess.run(
        [str(PY), str(HARNESS / "reader.py"),
         "--run-dir", str(arm["state"]), "--registry", str(arm["registry"]),
         "--out", str(out), "--label", label],
        cwd=str(ISO_RF), env=child_env(arm["registry"]),
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180,
    )
    return read_json(out)


def library_api_observation(arm) -> dict:
    """M4: direct library API call in a separate process — no CLI, no hooks."""
    script = f"""
import json, sys, os
sys.path.insert(0, r"{ISO_RF / 'scripts'}")
sys.path.insert(0, r"{ISO_RF / 'tests'}")
os.environ["REVENUE_PUBLICATION_REGISTRY"] = r"{arm['registry']}"
from pathlib import Path
from revenue_core import run_forecast
doc = json.loads(Path(r"{arm['state'] / 'input_p1.json'}").read_text(encoding="utf-8"))
result = run_forecast(doc)          # library API: registers immediately, writes no members
import publication_registry as PR
rows = PR._read_entries()
status = PR.commit_status(input_sha256=result["input_sha256"])
print(json.dumps({{
    "rows": len(rows),
    "row_publication_id": rows[-1].get("publication_id") if rows else None,
    "row_members": rows[-1].get("members") if rows else None,
    "commit_status_status": status.get("status"),
    "commit_status_problems": status.get("problems"),
    "member_files_on_disk": sorted(p.name for p in Path(r"{arm['state']}").glob("*.json") if p.name != "input_p1.json"),
}}, ensure_ascii=False))
"""
    proc = subprocess.run([str(PY), "-c", script], cwd=str(ISO_RF),
                          env=child_env(arm["registry"]), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=180)
    rec = {"raw_returncode": proc.returncode, "stderr": proc.stderr[:800]}
    try:
        rec.update(json.loads(proc.stdout.strip().splitlines()[-1]))
    except Exception as exc:
        rec["parse_error"] = f"{type(exc).__name__}: {exc}"
        rec["stdout"] = proc.stdout[:800]
    return rec


def snapshot_observation(arm) -> dict:
    script = f"""
import json, sys, os
sys.path.insert(0, r"{ISO_RF / 'scripts'}")
sys.path.insert(0, r"{ISO_RF / 'tests'}")
os.environ["REVENUE_PUBLICATION_REGISTRY"] = r"{arm['registry']}"
from pathlib import Path
from revenue_backtest import create_snapshot
from test_recognition_bridge import forecast_document
create_snapshot(forecast_document(), "i09c-snapshot-compat")
import publication_registry as PR
rows = PR._read_entries()
print(json.dumps({{
    "rows": len(rows),
    "artifact_types": [r.get("artifact_type") for r in rows],
    "snapshot_row_has_validation_status": [ "validation_status" in r for r in rows ],
    "publication_ids": [r.get("publication_id") for r in rows],
    "chain_ok_via_read_entries": True,
    "audit_problems": PR.audit(),
}}, ensure_ascii=False))
"""
    proc = subprocess.run([str(PY), "-c", script], cwd=str(ISO_RF),
                          env=child_env(arm["registry"]), capture_output=True,
                          text=True, encoding="utf-8", errors="replace", timeout=180)
    rec = {"raw_returncode": proc.returncode, "stderr": proc.stderr[:800]}
    try:
        rec.update(json.loads(proc.stdout.strip().splitlines()[-1]))
    except Exception as exc:
        rec["parse_error"] = f"{type(exc).__name__}: {exc}"
        rec["stdout"] = proc.stdout[:800]
    return rec


def main() -> int:
    if not (SHARED / "input_p1.json").exists():
        make_input_docs(SHARED)
    CIRC.mkdir(parents=True, exist_ok=True)
    arms = {}
    checks = []

    def check(name, expected, actual, why=""):
        checks.append({"item": name, "expected": expected, "actual": actual,
                       "ok": actual == expected, "why": why})

    # M1: formal JSON + Markdown
    a = fresh_arm("M1_json_markdown")
    r = run_cli(a, [str(a["state"] / "input_p1.json"),
                    "--output", str(a["state"] / "m1.json"),
                    "--markdown", str(a["state"] / "m1.md")])
    obs = observe(a, "reader_after")
    arms["M1"] = {"run": r, "obs_summary": {
        "chain_ok": obs["chain"]["ok"], "rows": obs["chain"]["rows"],
        "p1": {k: obs["packages"]["p1"].get(k) for k in
               ("consumable", "committed_rows", "logical_commits")}}}
    check("M1_rc", 0, r["raw_returncode"])
    check("M1_members_written", True,
          (a["state"] / "m1.json").exists() and (a["state"] / "m1.md").exists())
    check("M1_committed_and_consumable", True,
          obs["packages"]["p1"].get("consumable"))
    check("M1_chain_ok", True, obs["chain"]["ok"])

    # M2: stdout-only formal -> explicit rejection
    a = fresh_arm("M2_stdout_only")
    r = run_cli(a, [str(a["state"] / "input_p1.json")])
    obs = observe(a, "reader_after")
    arms["M2"] = {"run": r, "registry_rows": obs["chain"]["rows"]}
    check("M2_rc_rejected", 2, r["raw_returncode"])
    check("M2_explicit_rejection_message", True,
          "requires --output" in r["stderr"] or "stdout-only" in r["stderr"],
          r["stderr"][:200])
    check("M2_zero_registry_rows", 0, obs["chain"]["rows"])

    # M3: --markdown without --output -> same explicit rejection
    a = fresh_arm("M3_markdown_without_output")
    r = run_cli(a, [str(a["state"] / "input_p1.json"),
                    "--markdown", str(a["state"] / "m3.md")])
    obs = observe(a, "reader_after")
    arms["M3"] = {"run": r, "registry_rows": obs["chain"]["rows"]}
    check("M3_rc_rejected", 2, r["raw_returncode"])
    check("M3_explicit_rejection_message", True,
          "requires --output" in r["stderr"] or "stdout-only" in r["stderr"],
          r["stderr"][:200])
    check("M3_zero_registry_rows", 0, obs["chain"]["rows"])
    check("M3_no_markdown_written", True, not (a["state"] / "m3.md").exists())

    # M4: direct library API
    a = fresh_arm("M4_library_api")
    r = library_api_observation(a)
    obs = observe(a, "reader_after")
    arms["M4"] = {"run": r, "reader_p1_rows": obs["packages"]["p1"].get("rows_for_input")}
    check("M4_library_rc", 0, r.get("raw_returncode"))
    check("M4_row_without_publication_id", None, r.get("row_publication_id"),
          "C-12: library API row is not an addressable commit")
    check("M4_commit_status_not_commit_qualified", True,
          r.get("commit_status_status") in ("identity_unknown", "not_committed"),
          str(r.get("commit_status_status")))

    # M5: validate-only -> zero write
    a = fresh_arm("M5_validate_only")
    r = run_cli(a, [str(a["state"] / "input_p1.json"), "--validate-only"])
    obs = observe(a, "reader_after")
    arms["M5"] = {"run": r, "registry_rows": obs["chain"]["rows"]}
    check("M5_rc", 0, r["raw_returncode"])
    check("M5_stdout_valid", True, r["stdout"].strip().endswith("valid"), r["stdout"][:100])
    check("M5_zero_registry_rows", 0, obs["chain"]["rows"])
    check("M5_no_member_files", True,
          not any(p.name.startswith("m5") for p in a["state"].glob("m5*")))

    # M6: validate-only WITH --output -> still zero write (unsupported-to-write)
    a = fresh_arm("M6_validate_only_with_output")
    r = run_cli(a, [str(a["state"] / "input_p1.json"), "--validate-only",
                    "--output", str(a["state"] / "m6.json")])
    obs = observe(a, "reader_after")
    arms["M6"] = {"run": r, "registry_rows": obs["chain"]["rows"]}
    check("M6_rc", 0, r["raw_returncode"])
    check("M6_output_NOT_written", True, not (a["state"] / "m6.json").exists(),
          "validate-only must stay zero-write even when --output is present")
    check("M6_zero_registry_rows", 0, obs["chain"]["rows"])

    # M7: snapshot compatibility
    a = fresh_arm("M7_snapshot_compat")
    r = snapshot_observation(a)
    obs = observe(a, "reader_after")
    arms["M7"] = {"run": r, "chain_ok": obs["chain"]["ok"], "rows": obs["chain"]["rows"]}
    check("M7_rc", 0, r.get("raw_returncode"))
    check("M7_rows_2", 2, r.get("rows"), "F-10: create_snapshot => 1 forecast + 1 snapshot row")
    check("M7_artifact_types", ["forecast", "snapshot"], r.get("artifact_types"))
    check("M7_snapshot_row_without_validation_status", [True, False],
          r.get("snapshot_row_has_validation_status"),
          "old snapshot rows stay schema-compatible (key absent, not null)")
    check("M7_chain_ok_reader", True, obs["chain"]["ok"])
    check("M7_audit_problems", 0, len(r.get("audit_problems") or []))

    verdict = {"case_id": CASE, "card_point": "真实CLI/直接API/snapshot兼容矩阵 (P-C5)",
               "frozen_matrix_source": "I-09-A oracle C-12 + F9/F10 + I-09-B stdout-only rejection",
               "arms": arms, "checks": checks,
               "all_ok": all(c["ok"] for c in checks),
               "isolated_registries_only": True}
    write_json(CIRC / "verdict.json", verdict)
    print(f"PC5: all_ok={verdict['all_ok']} checks={len(checks)} "
          f"failed={sum(1 for c in checks if not c['ok'])}")
    for c in checks:
        if not c["ok"]:
            print(f"  FAIL {c['item']}: exp={c['expected']} act={c['actual']} {c['why']}")
    return 0 if verdict["all_ok"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
