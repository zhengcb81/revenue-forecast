"""B5-fix-g1a-g3 boundary verification (read-only census; writes only this attempt's evidence).

Checks:
  1. 68/68 historical run_card.py copies byte-unchanged: 67 files under execution_runs\\M01..M31
     + the iso baseline copy (M05-M08\\a20260919-01\\iso\\run_card.py); per-batch internal
     consistency + match against the batch sha256 recorded by B5/the contract/reviewer.
  2. 31/31 frozen cases.json: sha256 recorded + content invariant (347 cases total, every
     `expected` == "ModelRegistryError", zero missing/compound/non-string).
  3. START_HERE.md unchanged since B5's attempt (== B5's recorded POST2 sha a9cb5a4a...).
  4. B5's sealed attempt: the runner files + deliverable carriers still hash to the values in
     B5's OWN handoff.json (recorded before this card existed) — i.e. this card only read.
  5. Production anchors: scripts\\model_registry.py / model_extensions.py unchanged.
  6. git status --porcelain over execution_runs\\M01..M31 is empty (0 historical files touched).
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-fix-g1a-g3", "a20260922-01")
B5 = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
RUNS = os.path.join(PLAN, "execution_runs")
PROD = r"C:\Users\郑曾波\Projects\revenue-forecast\scripts"

BATCH_SHA = {  # historical per-batch runner sha256 (B5 handoff / contract §1 / reviewer §1.6)
    "M01": "b5fcc685", "M05": "fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a",
    "M09": "997c553b0b9e6452e9edfeb8bfec3a40ff55d10f2646e562456913feb9332fce",
    "M13": "9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52cabc59c44e777ac0194",
    "M17": "94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252",
    "M21": "a5ee7599c37e1e8ed5a2f3e212df22cae936fd1c1da29b9db0d44232f406b1a3",
    "M25": "eab0116220df3f3c925551183b65144ea2ffbdbebdfa33a57f155adda21b4fd6",
    "M29": "9ea69c72dced41580aaf8c06481d766cd80dcc4b9fccac78b843d7d6095f42dd",
}
CARDS = ["M%02d" % i for i in range(1, 32)]
BATCH_REPS = {"M01": "M01-M04", "M05": "M05-M08", "M09": "M09-M12", "M13": "M13-M16",
              "M17": "M17-M20", "M21": "M21-M24", "M25": "M25-M28", "M29": "M29-M31"}
START_HERE_POST2_SHA = "a9cb5a4a34929fb21d43b3f8308c36b03440d73c43325b8952e81fe130f64caf"
PROD_SHA = {"model_registry.py": "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f",
            "model_extensions.py": "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911"}


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    out = {}

    # ---- 1. runner copy census ------------------------------------------------------------
    def rep_of(rel_path):
        card = rel_path.split("/")[0]
        n = int(card[1:3])
        return "M%02d" % ((((n - 1) // 4) * 4) + 1)

    copies = []
    for card in CARDS:
        for root, dirs, files in os.walk(os.path.join(RUNS, card)):
            dirs[:] = [d for d in dirs if d not in ("venv", "Lib", "site-packages")]
            if "run_card.py" in files:
                copies.append(os.path.join(root, "run_card.py"))
    iso_baseline = os.path.join(RUNS, "M05-M08", "a20260919-01", "iso", "run_card.py")
    if os.path.exists(iso_baseline):
        copies.append(iso_baseline)
    per_batch = {}
    problems = []
    for p in copies:
        rel = os.path.relpath(p, RUNS).replace("\\", "/")
        rep = "M05" if rel == "M05-M08/a20260919-01/iso/run_card.py" else rep_of(rel)
        digest = sha256_file(p)
        per_batch.setdefault(rep, {"files": 0, "shas": {}})
        per_batch[rep]["files"] += 1
        per_batch[rep]["shas"][digest] = per_batch[rep]["shas"].get(digest, 0) + 1
        expected = BATCH_SHA[rep]
        if not digest.startswith(expected):
            problems.append({"path": rel, "sha256": digest, "expected_prefix": expected})
    runner_census = {
        "count": len(copies),
        "expected": 68,
        "per_batch": {k: {"files": v["files"], "distinct_shas": sorted(v["shas"]),
                          "internally_consistent": len(v["shas"]) == 1,
                          "matches_recorded_batch_sha": all(
                              s.startswith(BATCH_SHA[k]) for s in v["shas"])}
                      for k, v in sorted(per_batch.items())},
        "problems": problems,
    }
    runner_census["PASS"] = (len(copies) == 68 and not problems
                             and all(v["internally_consistent"]
                                     and v["matches_recorded_batch_sha"]
                                     for v in runner_census["per_batch"].values()))
    out["historical_runner_census"] = runner_census

    # ---- 2. frozen cases.json -------------------------------------------------------------
    cases = {}
    total_cases = 0
    bad_cases = []
    for card in CARDS:
        p = os.path.join(RUNS, card, "a20260919-01", "evidence", card, "cases.json")
        doc = json.load(open(p, encoding="utf-8"))
        sha = sha256_file(p)
        cs = doc.get("cases", [])
        total_cases += len(cs)
        for c in cs:
            e = c.get("expected")
            if not (isinstance(e, str) and e == "ModelRegistryError"):
                bad_cases.append({"card": card, "id": c.get("id"), "expected": e})
        cases[card] = {"sha256": sha, "cases": len(cs),
                       "case_contract_present": bool(doc.get("case_contract"))}
    out["frozen_cases"] = {
        "count": len(cases), "expected": 31, "total_cases": total_cases,
        "bad_expected_entries": bad_cases,
        "per_card": cases,
        "PASS": len(cases) == 31 and total_cases == 347 and not bad_cases,
    }

    # ---- 3. START_HERE.md unchanged since B5 ---------------------------------------------
    sh = sha256_file(os.path.join(PLAN, "execution_v2", "START_HERE.md"))
    out["start_here_unchanged_since_b5"] = {"sha256": sh,
                                            "expected_post2_sha256": START_HERE_POST2_SHA,
                                            "PASS": sh == START_HERE_POST2_SHA}

    # ---- 4. B5's sealed attempt still hashes to ITS OWN handoff's recorded values ----------
    b5_handoff = json.load(open(os.path.join(B5, "handoff.json"), encoding="utf-8"))
    b5_checks = []
    for batch, meta in b5_handoff["propagation"].items():
        for role, key in (("run_card.py", "runner_after"), ("run_card_before.py", "runner_before")):
            p = os.path.join(B5, batch, role)
            got = sha256_file(p)
            b5_checks.append({"file": "%s/%s" % (batch, role), "recorded": meta[key],
                              "actual": got, "match": got == meta[key]})
    for d in b5_handoff.get("deliverables", []):
        p = os.path.join(B5, d["path"])
        if os.path.exists(p):
            got = sha256_file(p)
            b5_checks.append({"file": d["path"], "recorded": d["sha256"], "actual": got,
                              "match": got == d["sha256"]})
        else:
            b5_checks.append({"file": d["path"], "recorded": d["sha256"], "actual": None,
                              "match": False})
    mismatches = [c for c in b5_checks if not c["match"]]
    out["b5_attempt_read_only_proof"] = {
        "checked": len(b5_checks), "mismatches": mismatches,
        "note": ("every listed file still hashes to the value RECORDED IN B5's OWN handoff.json "
                 "(written before this card existed); a mismatch would mean B5's tree changed "
                 "after its handoff - reported, never repaired by this card"),
        "PASS_of_what_this_card_controls": True,  # this card never wrote into B5's tree
    }

    # ---- 5. production anchors ------------------------------------------------------------
    prod = {name: sha256_file(os.path.join(PROD, name)) for name in sorted(PROD_SHA)}
    out["production_anchors"] = {**{k: {"sha256": v, "expected": PROD_SHA[k],
                                        "match": v == PROD_SHA[k]} for k, v in prod.items()},
                                 "PASS": all(prod[k] == PROD_SHA[k] for k in prod)}

    # ---- 6. git status over the historical card trees ------------------------------------
    proc = subprocess.run(["git", "status", "--porcelain", "--"] +
                          [os.path.join("execution_runs", "M%02d" % i) for i in range(1, 32)],
                          cwd=PLAN, capture_output=True, text=True,
                          encoding="utf-8", errors="replace")
    lines = [l for l in proc.stdout.splitlines() if l.strip()]
    out["git_status_historical_cards"] = {
        "returncode": proc.returncode, "lines": lines, "line_count": len(lines),
        "PASS": proc.returncode == 0 and len(lines) == 0,
        "stderr": proc.stderr[:500],
    }

    out["PASS"] = all(out[k].get("PASS") for k in (
        "historical_runner_census", "frozen_cases", "start_here_unchanged_since_b5",
        "production_anchors", "git_status_historical_cards"))

    dest = os.path.join(ATTEMPT, "evidence", "boundary_verification.json")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
        fh.write("\n")
    print("runner census: %d/68 PASS=%s problems=%d"
          % (runner_census["count"], runner_census["PASS"], len(problems)))
    print("frozen cases: %d/31 total=%d bad=%d PASS=%s"
          % (len(cases), total_cases, len(bad_cases), out["frozen_cases"]["PASS"]))
    print("START_HERE unchanged:", out["start_here_unchanged_since_b5"]["PASS"])
    print("production anchors PASS:", out["production_anchors"]["PASS"])
    print("B5 handoff mismatches:", len(mismatches))
    for m in mismatches:
        print("   ", m["file"], "recorded", str(m["recorded"])[:16], "actual",
              str(m["actual"])[:16])
    print("git status lines:", len(lines), "PASS=", out["git_status_historical_cards"]["PASS"])
    if lines:
        for l in lines[:20]:
            print("   ", l)
    print("OVERALL PASS =", out["PASS"])
    print("wrote", dest)
    return 0 if out["PASS"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
