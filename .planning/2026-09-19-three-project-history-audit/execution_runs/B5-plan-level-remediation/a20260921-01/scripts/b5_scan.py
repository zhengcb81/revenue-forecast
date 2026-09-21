"""B5+B6 REM-21 / REM-22 reconnaissance scan.

Read-only. Emits compact JSON evidence into <ATTEMPT>/evidence/.
Never writes to any historical artifact.
"""
import hashlib
import json
import os
import re

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
EV = os.path.join(ATT, "evidence")
RUNS = os.path.join(PLAN, "execution_runs")

# batch label -> representative card whose attempt holds the batch's runner copy
BATCHES = {
    "M01-M04": "M01",
    "M05-M08": "M05",
    "M09-M12": "M09",
    "M13-M16": "M13",
    "M17-M20": "M17",
    "M21-M24": "M21",
    "M25-M28": "M25",
    "M29-M31": "M29",
}
ALL_CARDS = ["M%02d" % i for i in range(1, 32)]


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha256_file(p):
    with open(p, "rb") as fh:
        return sha256_bytes(fh.read())


def attempt_dir(card):
    return os.path.join(RUNS, card, "a20260919-01")


def read_text(p):
    with open(p, "rb") as fh:
        raw = fh.read()
    return raw.decode("utf-8"), raw


# ---------------------------------------------------------------- 1. runners
runner_scan = {}
for label, rep in BATCHES.items():
    p = os.path.join(attempt_dir(rep), "scripts", "run_card.py")
    txt, raw = read_text(p)
    entry = {
        "representative_card": rep,
        "path": os.path.relpath(p, PLAN).replace("\\", "/"),
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "sha256_12": sha256_bytes(raw)[:12],
        "line_count": txt.count("\n") + 1,
    }
    # explicit rc constants
    consts = {}
    for m in re.finditer(r"^(EXIT_\w+|RC_\w+)\s*=\s*(-?\d+)\s*$", txt, re.M):
        consts[m.group(1)] = int(m.group(2))
    entry["rc_constants"] = consts
    # every integer literal that reaches SystemExit / sys.exit / return in main
    exits = []
    for m in re.finditer(r"(SystemExit\(([^)]*)\)|sys\.exit\(([^)]*)\))", txt):
        arg = (m.group(2) or m.group(3) or "").strip()
        ln = txt[: m.start()].count("\n") + 1
        exits.append({"line": ln, "arg": arg})
    entry["exit_calls"] = exits
    # does it read cases.json[].expected at all?
    entry["reads_case_expected"] = bool(re.search(r'case(?:s)?(?:\[[^\]]*\])?\.get\(\s*["\']expected', txt)) or \
                                   bool(re.search(r'\[["\']expected["\']\]', txt))
    entry["compares_raised_to_expected"] = bool(
        re.search(r'raised\w*\s*==\s*(?:case|entry)?\s*\[?["\']?expected', txt))
    runner_scan[label] = entry

# ------------------------------------------------- 2. batch exit_code_semantics
semantics = {}
for label, rep in BATCHES.items():
    cp = os.path.join(attempt_dir(rep), "commands.json")
    rec = {"commands_json": os.path.relpath(cp, PLAN).replace("\\", "/")}
    try:
        with open(cp, "rb") as fh:
            doc = json.loads(fh.read().decode("utf-8"))
        rec["has_block"] = "exit_code_semantics" in doc
        rec["exit_code_semantics"] = doc.get("exit_code_semantics")
        units = doc.get("units") or []
        rcs = {}
        for u in units:
            if isinstance(u, dict) and "raw_rc" in u:
                rcs.setdefault(str(u["raw_rc"]), []).append(u.get("unit_id"))
        rec["observed_raw_rc_histogram"] = {k: len(v) for k, v in sorted(rcs.items())}
        rec["observed_raw_rc_examples"] = {k: v[:4] for k, v in sorted(rcs.items())}
    except Exception as exc:  # noqa: BLE001
        rec["error"] = "%s: %s" % (type(exc).__name__, exc)
    semantics[label] = rec

# ------------------------------------------------------- 3. cases.json scan
cases_scan = {}
compound = []
missing = []
for card in ALL_CARDS:
    p = os.path.join(attempt_dir(card), "evidence", card, "cases.json")
    rec = {"path": os.path.relpath(p, PLAN).replace("\\", "/")}
    if not os.path.exists(p):
        rec["exists"] = False
        cases_scan[card] = rec
        missing.append(card)
        continue
    txt, raw = read_text(p)
    doc = json.loads(txt)
    cases = doc.get("cases") or []
    vals = []
    for c in cases:
        v = c.get("expected")
        vals.append({"id": c.get("id"), "expected": v, "type": type(v).__name__})
    rec.update({
        "exists": True,
        "bytes": len(raw),
        "sha256": sha256_bytes(raw),
        "case_count": len(cases),
        "expected_values": vals,
        "distinct_expected": sorted({repr(v["expected"]) for v in vals}),
        "any_missing": any(v["expected"] is None for v in vals),
        "any_non_string": any(not isinstance(v["expected"], str) for v in vals),
        "any_compound": any(isinstance(v["expected"], str) and not v["expected"].isidentifier()
                            for v in vals),
    })
    if rec["any_compound"]:
        compound.append({"card": card, "values": rec["distinct_expected"]})
    cases_scan[card] = rec

out = {
    "plan_root": PLAN,
    "attempt_root": ATT,
    "runner_scan": runner_scan,
    "batch_exit_code_semantics": semantics,
    "cases_expected_scan": cases_scan,
    "cards_scanned": len(ALL_CARDS),
    "cards_with_missing_cases_json": missing,
    "cards_with_compound_expected": compound,
}
os.makedirs(EV, exist_ok=True)
with open(os.path.join(EV, "b5_scan.json"), "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1, ensure_ascii=False, sort_keys=True)

print("wrote", os.path.join(EV, "b5_scan.json"))
print("runners:", len(runner_scan))
for k, v in runner_scan.items():
    print("  %-8s %s bytes=%d consts=%s reads_expected=%s compares=%s"
          % (k, v["sha256_12"], v["bytes"], sorted(v["rc_constants"].items()),
             v["reads_case_expected"], v["compares_raised_to_expected"]))
print("cases.json scan: cards=%d missing=%s compound=%s"
      % (len(ALL_CARDS), missing, compound))
tot = sum(v.get("case_count", 0) for v in cases_scan.values() if v.get("exists"))
print("total cases:", tot)
