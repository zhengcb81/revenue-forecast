"""B5 REM-22: extract the REAL return-code paths of every batch runner (read-only)."""
import json
import os
import re

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
RUNS = os.path.join(PLAN, "execution_runs")
BATCHES = {
    "M01-M04": "M01", "M05-M08": "M05", "M09-M12": "M09", "M13-M16": "M13",
    "M17-M20": "M17", "M21-M24": "M21", "M25-M28": "M25", "M29-M31": "M29",
}
PAT = re.compile(
    r"(sys\.exit|SystemExit|^\s*return\s+(?:EXIT_|RC_)?\d|exit_code\s*=|"
    r"exit_code,|verdict,\s*rc|rc\s*=\s*(?:RC_|EXIT_)?\d|"
    r"raise\s+SystemExit|main\(\)|_finish\()",
)

out = {}
for label, rep in BATCHES.items():
    p = os.path.join(RUNS, rep, "a20260919-01", "scripts", "run_card.py")
    txt = open(p, encoding="utf-8").read()
    hits = []
    for i, line in enumerate(txt.splitlines(), 1):
        if PAT.search(line):
            s = line.rstrip()
            hits.append({"line": i, "text": s[:170]})
    out[label] = {"path": os.path.relpath(p, PLAN).replace("\\", "/"), "hits": hits}

dest = os.path.join(ATT, "evidence", "rc_return_paths.json")
os.makedirs(os.path.dirname(dest), exist_ok=True)
with open(dest, "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False)
print("wrote", dest)
for label, rec in out.items():
    print("=" * 60)
    print(label, rec["path"])
    for h in rec["hits"]:
        print("  L%-4d %s" % (h["line"], h["text"]))
