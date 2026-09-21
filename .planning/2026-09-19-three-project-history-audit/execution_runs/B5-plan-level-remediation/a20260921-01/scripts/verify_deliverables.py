"""B5+B6 final deliverable consistency check.

Asserts that every deliverable agrees with the LIVE bytes on disk, so that no artifact is a
stale snapshot of another (this card caught exactly that class of problem once already: the
M13-M16 worker rewrote its runner after the first aggregation pass).
"""
import hashlib
import json
import os
import re
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
RUNS = os.path.join(PLAN, "execution_runs")
START_HERE = os.path.join(PLAN, "execution_v2", "START_HERE.md")

POST2 = "a9cb5a4a34929fb21d43b3f8308c36b03440d73c43325b8952e81fe130f64caf"
REF = "94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252"
BATCHES = [("M05-M08", "M05"), ("M09-M12", "M09"), ("M13-M16", "M13"),
           ("M21-M24", "M21"), ("M25-M28", "M25"), ("M29-M31", "M29")]
DELIVERABLES = ["oracle.md", "handoff.json", "changes.diff", "binding.json",
                "commands.json", "decision.md", "PROPAGATION_CONTRACT.md"]


def sha(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


problems = []
report = {}

# 1. every deliverable exists and every JSON parses
for d in DELIVERABLES:
    p = os.path.join(ATT, d)
    if not os.path.exists(p):
        problems.append("MISSING deliverable: " + d)
        continue
    report[d] = {"bytes": os.path.getsize(p), "sha256": sha(p)}
    if d.endswith(".json"):
        try:
            json.load(open(p, encoding="utf-8"))
            report[d]["parses"] = True
        except Exception as exc:  # noqa: BLE001
            problems.append("UNPARSEABLE %s: %s" % (d, exc))
            report[d]["parses"] = False

# 2. per-batch artifacts exist
for label, rep in BATCHES:
    for f in ("run_card.py", "run_card_before.py", "runner.diff", "evidence.json"):
        p = os.path.join(ATT, label, f)
        if not os.path.exists(p):
            problems.append("MISSING %s/%s" % (label, f))

# 3. changes.diff's recorded after-hashes must equal the LIVE runner bytes
diff_txt = open(os.path.join(ATT, "changes.diff"), encoding="utf-8").read()
recorded = re.findall(r"# after  sha256 ([0-9a-f]{64})", diff_txt)
live = [sha(os.path.join(ATT, label, "run_card.py")) for label, _ in BATCHES]
report["changes_diff_after_hashes"] = {"recorded": len(recorded), "live": len(live),
                                       "match": sorted(recorded) == sorted(live)}
if sorted(recorded) != sorted(live):
    problems.append("changes.diff after-hashes do not match the live runners")
recorded_before = re.findall(r"# before sha256 ([0-9a-f]{64})", diff_txt)
live_before = [sha(os.path.join(ATT, label, "run_card_before.py")) for label, _ in BATCHES]
if sorted(recorded_before) != sorted(live_before):
    problems.append("changes.diff before-hashes do not match the local byte copies")
if diff_txt.count("diff --git") != 7:
    problems.append("changes.diff should carry 7 file diffs (6 runners + START_HERE), got %d"
                    % diff_txt.count("diff --git"))

# 4. handoff + binding must agree with the live runners
handoff = json.load(open(os.path.join(ATT, "handoff.json"), encoding="utf-8"))
for label, rep in BATCHES:
    rec = handoff["propagation"][label]["runner_after"]
    if rec != sha(os.path.join(ATT, label, "run_card.py")):
        problems.append("handoff.json runner_after stale for " + label)
    if handoff["propagation"][label]["runner_before"] != sha(
            os.path.join(ATT, label, "run_card_before.py")):
        problems.append("handoff.json runner_before stale for " + label)
    if not handoff["propagation"][label]["arms_match"]:
        problems.append("handoff.json arms_match false for " + label)

binding = json.load(open(os.path.join(ATT, "binding.json"), encoding="utf-8"))
# binding.json is the PRE-RUN binding, so the measured post-run state lives in post_run_refresh
for label, rec in (binding.get("post_run_refresh") or {}).get("runners", {}).items():
    cur = sha(os.path.join(ATT, label, "run_card.py"))
    if rec["sha256"] != cur:
        problems.append("binding.json post_run_refresh stale for " + label)
for label, rec in binding.get("per_batch_environment", {}).items():
    if "planned_not_yet_written_at_binding_time" not in str(rec.get("runner_after")):
        problems.append("binding.json per_batch_environment[%s].runner_after must stay 'planned' "
                        "(this file is the pre-run binding)" % label)

# 5. handoff status must not be a self-signature
if handoff.get("status") != "review_pending":
    problems.append("handoff.json status is not review_pending: %r" % handoff.get("status"))
if handoff.get("implementer_signed") is not False:
    problems.append("handoff.json implementer_signed must be false")

# 6. START_HERE must still be POST2 and the reference runner must be the r3 value
if sha(START_HERE) != POST2:
    problems.append("START_HERE.md no longer matches the recorded POST2 hash")
commands = json.load(open(os.path.join(ATT, "commands.json"), encoding="utf-8"))
if commands.get("exit_code_legend", {}).get("2") is None:
    problems.append("commands.json is missing the frozen exit_code_legend")

# 7. historical anchors must be untouched
anchors = {
    "scripts/model_registry.py": os.path.join(
        r"C:\Users\郑曾波\Projects\revenue-forecast", "scripts", "model_registry.py"),
}
for name, p in anchors.items():
    if sha(p) != "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f":
        problems.append("production anchor changed: " + name)
if sha(os.path.join(RUNS, "M17", "a20260919-01", "scripts", "run_card.py")) != REF:
    problems.append("reference runner M17-M20 changed")

report["problems"] = problems
report["PASS"] = not problems
with open(os.path.join(ATT, "evidence", "deliverable_consistency.json"), "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1, ensure_ascii=False)

print("deliverables:", len([d for d in DELIVERABLES if d in report]))
print("changes.diff hashes match live:", report["changes_diff_after_hashes"]["match"])
print("diff file blocks:", diff_txt.count("diff --git"))
print("PASS =", report["PASS"])
for p in problems:
    print("  PROBLEM:", p)
sys.exit(0 if report["PASS"] else 2)
