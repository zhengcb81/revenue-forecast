"""Final integrity self-check for the M05-M08 REM-21 batch.

Validates evidence.json parses, asserts its measured claims against the raw arm
outputs on disk, and confirms the boundary claims by hashing/re-hashing files.
"""
import hashlib
import json
import os
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATTEMPT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
BATCH = "M05-M08"
OUT = os.path.join(ATTEMPT, BATCH)
SCRATCH = os.path.join(ATTEMPT, "_scratch", BATCH)
CARDS = ["M05", "M06", "M07", "M08"]
problems = []


def need(cond, msg):
    if not cond:
        problems.append(msg)


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


ev = json.load(open(os.path.join(OUT, "evidence.json"), encoding="utf-8"))
rows = json.load(open(os.path.join(SCRATCH, "arms_raw.json"), encoding="utf-8"))
idx = {(r["arm"], r["card"]): r for r in rows}

# --- deliverable files exist and hashes match evidence.json ---
for name, key in (("run_card.py", "runner_after"), ("run_card_before.py", "runner_before")):
    p = os.path.join(OUT, name)
    need(os.path.exists(p), f"missing {name}")
    need(sha256_file(p) == ev[key]["sha256"], f"{name} sha256 != evidence.json {key}")
    need(os.path.getsize(p) == ev[key]["bytes"], f"{name} bytes != evidence.json {key}")
need(os.path.exists(os.path.join(OUT, "runner.diff")), "missing runner.diff")
need(sha256_file(os.path.join(OUT, "runner.diff")) == ev["diff_sha256"], "runner.diff sha256 mismatch")
need(ev["runner_before"]["sha256"] == "fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a",
     "runner_before sha256 not the frozen value")
need(ev["runner_before"]["bytes"] == 14758, "runner_before bytes != 14758")

# --- historical runners untouched (all four) ---
for c in CARDS:
    p = os.path.join(PLAN, "execution_runs", c, "a20260919-01", "scripts", "run_card.py")
    need(sha256_file(p) == "fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a",
         f"historical {c} runner changed")

# --- cards_cases_sha256 matches what the arms actually read ---
for c in CARDS:
    p = os.path.join(PLAN, "execution_runs", c, "a20260919-01", "evidence", c, "cases.json")
    need(sha256_file(p) == ev["cards_cases_sha256"][c], f"cards_cases_sha256[{c}] mismatch")
    # E arm cases.json must equal the frozen original
    need(idx[("E", c)]["cases_json_sha256"] == ev["cards_cases_sha256"][c],
         f"E/{c} cases.json != frozen original")
    need(idx[("B", c)]["cases_json_sha256"] == idx[("F", c)]["cases_json_sha256"],
         f"B/{c} != F/{c} cases.json")

# --- arm rcs match arm_card_matrix and the per-arm blocks ---
for arm in ("E", "F", "B", "G"):
    for c in CARDS:
        need(idx[(arm, c)]["raw_rc"] == ev["arm_card_matrix"][arm][c],
             f"{arm}/{c} rc != arm_card_matrix")
    need(ev["arms"][arm]["rc"] == ev["arm_card_matrix"][arm]["M05"],
         f"arms.{arm}.rc != matrix M05")

# --- arm B measured 0 -> historical_runner_already_gated must be false ---
need(ev["historical_runner_already_gated"] is False, "historical_runner_already_gated should be false")
need(ev["arm_B_rc_basis"]["measured_raw_rc"] == 0, "arm_B_rc_basis measured rc != 0")
need(ev["arms"]["B"]["rc"] == 0, "arms.B.rc != 0")

# --- isolated code root hashes ---
for f, want in (("model_registry.py", "9ec6529550f189a435aed2eaba9b915bc104736f3d660049b9e3999f6ee2d17f"),
                ("model_extensions.py", "9939480b717d5a49523b0d5af73211e5813a78e8436d08864ae6c8562089b911")):
    p = os.path.join(SCRATCH, "code_root", f)
    need(sha256_file(p) == want, f"code_root/{f} sha256 mismatch")
    need(ev["isolated_code_root_sha256"][f] == want, f"evidence code_root {f} mismatch")
need(len(os.listdir(os.path.join(SCRATCH, "code_root"))) == 2, "code_root should hold exactly 2 files")

# --- no pycache anywhere under ATTEMPT ---
pyc = []
for root, dirs, files in os.walk(ATTEMPT):
    for f in files:
        if f.endswith(".pyc"):
            pyc.append(os.path.join(root, f))
    if "__pycache__" in dirs:
        pyc.append(os.path.join(root, "__pycache__"))
need(not pyc, f"pycache/pyc found: {pyc[:3]}")
need(ev["no_pycache_created"]["pyc_files_under_attempt"] == 0, "evidence claims pyc count 0")

# --- historical mtimes all older than this session ---
import datetime
newest = None
for c in CARDS:
    for root, dirs, files in os.walk(os.path.join(PLAN, "execution_runs", c)):
        for f in files:
            t = os.path.getmtime(os.path.join(root, f))
            if newest is None or t > newest:
                newest = t
need(newest < datetime.datetime(2026, 9, 21).timestamp(),
     f"a file under execution_runs/M05..M08 is newer than 2026-09-21: {datetime.datetime.fromtimestamp(newest)}")
need(ev["historical_writes"] == [], "historical_writes not empty")
need(ev["boundaries_respected"] is True, "boundaries_respected not true")

print("evidence.json parses: OK")
print("newest mtime under execution_runs/M05..M08:", datetime.datetime.fromtimestamp(newest).isoformat())
print("arm rc matrix:", {a: [idx[(a, c)]["raw_rc"] for c in CARDS] for a in ("E", "F", "B", "G")})
print("historical_runner_already_gated:", ev["historical_runner_already_gated"])
print("problems:", len(problems))
for p in problems:
    print("  PROBLEM:", p)
sys.exit(1 if problems else 0)
