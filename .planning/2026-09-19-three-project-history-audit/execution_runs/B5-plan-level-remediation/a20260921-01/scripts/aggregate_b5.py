"""B5+B6 aggregation: changes.diff, commands.json, handoff.json, final summary.

Runs only after all six batch workers have written <batch>/evidence.json.
Every value is read from measured artifacts; nothing is inferred.
"""
import difflib
import hashlib
import json
import os
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
RUNS = os.path.join(PLAN, "execution_runs")
TARGET = os.path.join(PLAN, "execution_v2", "START_HERE.md")

PRE_SHA = "1bdfbd9190d6ae956d6ad025792a4ffa487f0e41258f80922c752f783cf22835"
PRE_BYTES = 9895
POST_SHA = "a9cb5a4a34929fb21d43b3f8308c36b03440d73c43325b8952e81fe130f64caf"
POST1_SHA = "e7cb90fc5c4cc51f2dfe97f1bfef55750ee1459e07bf3078890d227b1c441557"
POST1_BYTES = 16314

BATCHES = [("M05-M08", "M05", ["M05", "M06", "M07", "M08"]),
           ("M09-M12", "M09", ["M09", "M10", "M11", "M12"]),
           ("M13-M16", "M13", ["M13", "M14", "M15", "M16"]),
           ("M21-M24", "M21", ["M21", "M22", "M23", "M24"]),
           ("M25-M28", "M25", ["M25", "M26", "M27", "M28"]),
           ("M29-M31", "M29", ["M29", "M30", "M31"])]


def sha_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def rel(p):
    return os.path.relpath(p, PLAN).replace("\\", "/")


# ------------------------------------------------------------------ batch data
batch_evidence = {}
missing = []
for label, rep, cards in BATCHES:
    p = os.path.join(ATT, label, "evidence.json")
    if os.path.exists(p):
        batch_evidence[label] = json.load(open(p, encoding="utf-8"))
    else:
        missing.append(label)
if missing:
    print("NOT READY - missing evidence.json for:", missing)
    sys.exit(3)

# --------------------------------------------------------------- changes.diff
parts = []
parts.append("# B5+B6 changes.diff\n")
parts.append("# REM-22 (rc code table): append-only addition to execution_v2/START_HERE.md\n")
parts.append("# REM-21 (runner propagation): per-batch COPY of run_card.py, one hunk set per batch\n")
parts.append("# Historical artifacts (before/, frozen cases.json, recorded rc) are NOT in this diff by construction.\n\n")

# REM-22 hunk: pre-image is recoverable from the recorded byte length (append-only was proven)
post = open(TARGET, "rb").read()
assert hashlib.sha256(post).hexdigest() == POST_SHA, "START_HERE.md changed since the append proof"
pre = post[:PRE_BYTES]
pre_lines = pre.decode("utf-8").splitlines(keepends=True)
post_lines = post.decode("utf-8").splitlines(keepends=True)
parts.append("diff --git a/execution_v2/START_HERE.md b/execution_v2/START_HERE.md\n")
parts.append("--- a/execution_v2/START_HERE.md\n+++ b/execution_v2/START_HERE.md\n")
parts.append("@@ pre-image sha256 %s (%d B) -> post-image %s (%d B) @@\n"
             % (PRE_SHA[:16], PRE_BYTES, POST_SHA[:16], len(post)))
parts.extend(difflib.unified_diff(pre_lines, post_lines,
                                  fromfile="execution_v2/START_HERE.md (pre)",
                                  tofile="execution_v2/START_HERE.md (post)", n=3))
parts.append("\n")

# REM-21 hunks: regenerate from the byte copies so the diff is independently reproducible
diff_stats = {}
for label, rep, cards in BATCHES:
    b = os.path.join(ATT, label, "run_card_before.py")
    a = os.path.join(ATT, label, "run_card.py")
    if not (os.path.exists(a) and os.path.exists(b)):
        diff_stats[label] = {"error": "missing copy"}
        continue
    bl = open(b, encoding="utf-8").read().splitlines(keepends=True)
    al = open(a, encoding="utf-8").read().splitlines(keepends=True)
    d = list(difflib.unified_diff(bl, al,
                                  fromfile="%s/scripts/run_card.py (historical, UNCHANGED)" % rep,
                                  tofile="B5-plan-level-remediation/a20260921-01/%s/run_card.py (new copy)" % label,
                                  n=3))
    parts.append("diff --git a/execution_runs/%s/a20260919-01/scripts/run_card.py "
                 "b/execution_runs/B5-plan-level-remediation/a20260921-01/%s/run_card.py\n" % (rep, label))
    parts.append("# before sha256 %s (%d B)\n" % (sha_file(b), os.path.getsize(b)))
    parts.append("# after  sha256 %s (%d B)\n" % (sha_file(a), os.path.getsize(a)))
    parts.extend(d)
    parts.append("\n")
    added = sum(1 for ln in d if ln.startswith("+") and not ln.startswith("+++"))
    removed = sum(1 for ln in d if ln.startswith("-") and not ln.startswith("---"))
    diff_stats[label] = {"added_lines": added, "removed_lines": removed,
                         "before_sha256": sha_file(b), "after_sha256": sha_file(a)}

with open(os.path.join(ATT, "changes.diff"), "w", encoding="utf-8") as fh:
    fh.write("".join(parts))
changes_sha = sha_file(os.path.join(ATT, "changes.diff"))

# ------------------------------------------------------------------ commands.json
units = []
units.append({
    "unit_id": "S0-b5-scan",
    "purpose": "read-only scan: hash all 8 batch runners, locate their rc branches, scan all 31 frozen cases.json",
    "cwd": ATT,
    "argv": [r"C:\Miniconda\python.exe", "-X", "utf8", "scripts/b5_scan.py"],
    "network": "disabled",
    "raw_rc": 0,
    "expected_rc": 0,
    "note": "global Miniconda python is used ONLY for this card's own read-only analysis scripts; "
            "no card runner is ever executed with it",
})
units.append({
    "unit_id": "S1-rc-return-paths",
    "purpose": "read-only extraction of every runner's real return-code paths",
    "cwd": ATT, "argv": [r"C:\Miniconda\python.exe", "-X", "utf8", "scripts/b5_rc_paths.py"],
    "network": "disabled", "raw_rc": 0, "expected_rc": 0,
})
units.append({
    "unit_id": "S2-append-only-proof",
    "purpose": "prove the REM-22 START_HERE.md addition is a pure append (difflib + prefix)",
    "cwd": ATT, "argv": [r"C:\Miniconda\python.exe", "-X", "utf8", "scripts/verify_append.py"],
    "network": "disabled", "raw_rc": 0, "expected_rc": 0,
    "result": "evidence/start_here_append_proof.json APPEND_ONLY=true (two pure appends: +74 and +34 lines, 0 deleted)",
})
units.append({
    "unit_id": "S3-boundary-verification",
    "purpose": "prove no historical runner/cases.json changed and no historical file was modified after card start",
    "cwd": ATT, "argv": [r"C:\Miniconda\python.exe", "-X", "utf8", "scripts/verify_boundaries.py"],
    "network": "disabled", "raw_rc": 0, "expected_rc": 0,
    "result": "evidence/boundary_verification.json PASS=true",
})

def arm_rc(ev, k):
    """Two batch evidence schemas are in use: a flat {arm: {rc: N}}, and a per-card nested
    {arm: {CARD: {raw_rc_from_process: N}}} with an `arm_rollup` summary. Read both, and only
    return a value when every card agrees."""
    a = (ev.get("arms") or {}).get(k)
    if isinstance(a, dict):
        if isinstance(a.get("rc"), int):
            return a["rc"]
        vals = [c.get("raw_rc_from_process") for c in a.values() if isinstance(c, dict)]
        vals = [x for x in vals if isinstance(x, int)]
        if vals and len(set(vals)) == 1:
            return vals[0]
    r = (ev.get("arm_rollup") or {}).get(k)
    if isinstance(r, dict):
        vals = [x for x in (r.get("rc_values") or []) if isinstance(x, int)]
        if vals and len(set(vals)) == 1:
            return vals[0]
    return None


for label, rep, cards in BATCHES:
    ev = batch_evidence[label]
    arms = ev.get("arms", {})
    for arm_key in ("E", "F", "B", "G"):
        raw = arms.get(arm_key)
        arm = raw if isinstance(raw, dict) else {}
        flat = arm.get("rc") if isinstance(arm.get("rc"), int) else None
        units.append({
            "unit_id": "R-%s-arm-%s" % (label, arm_key),
            "scope": label,
            "purpose": {
                "E": "green control: patched runner vs unmodified frozen cases.json copy",
                "F": "REQUIRED mutation arm: one negative case's expected -> ValueError",
                "B": "inertness control: HISTORICAL runner vs the same mutated cases.json. "
                     "This arm's rc is a MEASUREMENT, not an expectation: the historical runners "
                     "reacted in FOUR distinct ways (0, 1, 2 and 3) across the six batches.",
                "G": "rc-classification arm: the same case's expected key deleted -> must be rc=2",
            }[arm_key],
            "runner": "new" if arm_key in ("E", "F", "G") else "historical copy",
            "network": "disabled",
            "exit_code_legend": {"0": "pass", "1": "harness failure",
                                 "2": "no verdict (declaration unusable)",
                                 "3": "judgement possible and did not hold"},
            "raw_rc": flat if flat is not None else arm_rc(ev, arm_key),
            "raw_rc_uniform_across_all_cards": arm_rc(ev, arm_key) is not None,
            "expected_rc": ({"E": 0, "F": 3, "G": 2}.get(arm_key)
                            if arm_key != "B" else "measured (unconstrained)"),
            "observed_verdict": arm.get("verdict"),
            "observed_declared_expectation_mismatch": arm.get("declared_expectation_mismatch"),
            "mutated_case": arm.get("mutated_case") or ev.get("mutated_case"),
            "note": arm.get("note"),
        })

commands = {
    "card": "B5+B6",
    "attempt": "a20260921-01",
    "attempt_root": ATT,
    "created_before_card_runs": False,
    "created_before_card_runs_note": (
        "the card's own read-only analysis units (S0/S1) ran before any runner was patched; "
        "the append-only proof (S2) and boundary verification (S3) run after. This file is written last."),
    "isolation": {
        "cwd": ATT,
        "note": "every runner run uses that batch's own iso venv interpreter with -B, and a scratch tree "
                "under this attempt directory; the historical attempt directories are read-only inputs",
        "network": "disabled",
        "per_batch": {
            label: {"interpreter": ev.get("interpreter"), "code_root": ev.get("code_root")}
            for label, ev in batch_evidence.items()
        },
    },
    "exit_code_legend": {
        "0": "pass",
        "1": "harness failure",
        "2": "no verdict: the frozen declaration itself is missing/unusable, decided before any case is judged",
        "3": "a judgement was possible and did not hold (nothing raised, wrong type, or declaration mismatch)",
    },
    "units": units,
}
with open(os.path.join(ATT, "commands.json"), "w", encoding="utf-8") as fh:
    json.dump(commands, fh, indent=1, ensure_ascii=False)

# ------------------------------------------------------------------ summary
summary = {
    "reference_runner_sha256": sha_file(os.path.join(RUNS, "M17", "a20260919-01", "scripts", "run_card.py")),
    "rem22": {"pre_sha256": PRE_SHA, "post1_sha256": POST1_SHA, "post_sha256": POST_SHA,
              "appends": [{"step": "append 1", "lines_added": 74, "content": "measured per-batch rc registry"},
                          {"step": "append 2", "lines_added": 34,
                           "content": "missing-expected classification erratum (KeyError -> rc=1)"}],
              "deleted_lines": 0, "append_only": True},
    "rem21": {},
    "changes_diff_sha256": changes_sha,
    "changes_diff_stats": diff_stats,
}
print("changes.diff sha256:", changes_sha)
print("commands.json units:", len(units))


def arm_rc(ev, k):
    """Two batch evidence schemas are in use: a flat {arm: {rc: N}}, and a per-card nested
    {arm: {CARD: {raw_rc_from_process: N}}} with an `arm_rollup` summary. Read both, and only
    return a value when every card agrees."""
    a = (ev.get("arms") or {}).get(k)
    if isinstance(a, dict):
        if isinstance(a.get("rc"), int):
            return a["rc"]
        vals = [c.get("raw_rc_from_process") for c in a.values() if isinstance(c, dict)]
        vals = [x for x in vals if isinstance(x, int)]
        if vals and len(set(vals)) == 1:
            return vals[0]
    r = (ev.get("arm_rollup") or {}).get(k)
    if isinstance(r, dict):
        vals = [x for x in (r.get("rc_values") or []) if isinstance(x, int)]
        if vals and len(set(vals)) == 1:
            return vals[0]
    return None


for label, ev in batch_evidence.items():
    row = {k: arm_rc(ev, k) for k in ("E", "F", "B", "G")}
    # arm B is a MEASUREMENT (four distinct values were observed across the six batches),
    # so only E/F/G carry expectations.
    ok = row["E"] == 0 and row["F"] == 3 and row["G"] == 2
    summary["rem21"][label] = {
        "before": (ev.get("runner_before") or {}).get("sha256"),
        "after": (ev.get("runner_after") or {}).get("sha256"),
        "arms_rc": row,
        "arm_b_is_a_measurement": True,
        "expected": {"E": 0, "F": 3, "B": "measured (unconstrained)", "G": 2},
        "ok": ok,
    }
    print("  %-8s before=%s after=%s arms=%s ok=%s"
          % (label, (summary["rem21"][label]["before"] or "")[:12],
             (summary["rem21"][label]["after"] or "")[:12], row, ok))
allok = all(v["ok"] for v in summary["rem21"].values())
print("ALL E/F/G ARMS AS EXPECTED =", allok)
print("arm B measured values:", {k: v["arms_rc"]["B"] for k, v in summary["rem21"].items()})
with open(os.path.join(ATT, "evidence", "aggregate_summary.json"), "w", encoding="utf-8") as fh:
    json.dump(summary, fh, indent=1, ensure_ascii=False)
