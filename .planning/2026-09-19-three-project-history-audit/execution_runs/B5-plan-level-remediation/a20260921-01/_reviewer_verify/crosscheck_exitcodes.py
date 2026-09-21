"""Reviewer cross-check: recorded arm rc vs the rc embedded in each arm's out_*.json.

For every batch/arm/card the implementer ran, read out_<CARD>.json and compare its
exit_code_semantics.exit_code with the rc claimed in evidence.json.
"""
import json
import os

ATTEMPT = (r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
           r"\2026-09-19-three-project-history-audit\execution_runs"
           r"\B5-plan-level-remediation\a20260921-01")
BATCHES = ["M05-M08", "M09-M12", "M13-M16", "M21-M24", "M25-M28", "M29-M31"]

for b in BATCHES:
    ev = json.load(open(os.path.join(ATTEMPT, b, "evidence.json"), encoding="utf-8"))
    cards = ev["cards"]
    claimed = {}
    rows = ev.get("arm_summary_rows") or {}
    for arm in "EFBG":
        v = (ev.get("arms") or {}).get(arm, {}).get("rc")
        if v is None and isinstance(rows.get(arm), dict):
            v = rows[arm].get("rc")
            if isinstance(v, dict):
                v = sorted(set(v.values()))
        claimed[arm] = v
    sdir = os.path.join(ATTEMPT, "_scratch", b)
    print("=" * 78)
    print("%s  evidence.json rc = %s" % (b, claimed))
    for arm in sorted(os.listdir(sdir)):
        armdir = os.path.join(sdir, arm)
        if not os.path.isdir(armdir):
            continue
        got = {}
        for card in cards:
            for cand in ("out_%s.json" % card, "%s_M%s.json" % ("out", card[1:])):
                p = os.path.join(armdir, cand)
                if os.path.exists(p):
                    try:
                        d = json.load(open(p, encoding="utf-8"))
                        got[card] = (d.get("exit_code_semantics") or {}).get("exit_code",
                                                                            d.get("exit_code"))
                    except Exception as exc:  # noqa: BLE001
                        got[card] = "ERR:%s" % type(exc).__name__
                    break
        if got:
            print("   raw %-10s embedded exit_code = %s" % (arm, got))
    print()
