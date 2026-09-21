"""B5+B6 boundary verification.

Proves (a) every historical M-card runner copy still hashes to its pre-existing value, and
(b) no file anywhere under the historical M-card attempt trees was modified after this card
started. Read-only.

The 68 expected runner hashes were measured BEFORE any batch worker was dispatched; the
CARD_START_UTC threshold is the instant this attempt began producing artifacts.
"""
import hashlib
import json
import os
import sys

PLAN = r"C:\Users\郑曾波\Projects\revenue-forecast\.planning\2026-09-19-three-project-history-audit"
ATT = os.path.join(PLAN, "execution_runs", "B5-plan-level-remediation", "a20260921-01")
RUNS = os.path.join(PLAN, "execution_runs")

CARD_START_UTC = "2026-09-21T20:19:00Z"  # first artifact of this attempt (b5_scan.py: 20:19:59Z)

CARDS = ["M%02d" % i for i in range(1, 32)]
BATCH_RUNNER_SHA = {
    "M01": "b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816",
    "M02": "b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816",
    "M03": "b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816",
    "M04": "b5fcc68563f563924529e06e2aeeba06938dcf51bd48b14f553f580191601816",
    "M05": "fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a",
    "M06": "fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a",
    "M07": "fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a",
    "M08": "fd3a11c9226a7bb14ea9ac91b00148a174219087e44f3cf18bb52d914e6f448a",
    "M09": "997c553b0b9e6452e9edfeb8bfec3a40ff55d10f2646e562456913feb9332fce",
    "M10": "997c553b0b9e6452e9edfeb8bfec3a40ff55d10f2646e562456913feb9332fce",
    "M11": "997c553b0b9e6452e9edfeb8bfec3a40ff55d10f2646e562456913feb9332fce",
    "M12": "997c553b0b9e6452e9edfeb8bfec3a40ff55d10f2646e562456913feb9332fce",
    "M13": "9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52cabc59c44e777ac0194",
    "M14": "9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52cabc59c44e777ac0194",
    "M15": "9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52cabc59c44e777ac0194",
    "M16": "9e4a6450d6ab6ad39230d2c409e4cce2f23c42ddcfd52cabc59c44e777ac0194",
    "M17": "94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252",
    "M18": "94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252",
    "M19": "94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252",
    "M20": "94619a98f5761752ec12f7bcca43e9ab4d1d11fe49800ea05f868e5c49f4a252",
    "M21": "a5ee7599c37e1e8ed5a2f3e212df22cae936fd1c1da29b9db0d44232f406b1a3",
    "M22": "a5ee7599c37e1e8ed5a2f3e212df22cae936fd1c1da29b9db0d44232f406b1a3",
    "M23": "a5ee7599c37e1e8ed5a2f3e212df22cae936fd1c1da29b9db0d44232f406b1a3",
    "M24": "a5ee7599c37e1e8ed5a2f3e212df22cae936fd1c1da29b9db0d44232f406b1a3",
    "M25": "eab0116220df3f3c925551183b65144ea2ffbdbebdfa33a57f155adda21b4fd6",
    "M26": "eab0116220df3f3c925551183b65144ea2ffbdbebdfa33a57f155adda21b4fd6",
    "M27": "eab0116220df3f3c925551183b65144ea2ffbdbebdfa33a57f155adda21b4fd6",
    "M28": "eab0116220df3f3c925551183b65144ea2ffbdbebdfa33a57f155adda21b4fd6",
    "M29": "9ea69c72dced41580aaf8c06481d766cd80dcc4b9fccac78b843d7d6095f42dd",
    "M30": "9ea69c72dced41580aaf8c06481d766cd80dcc4b9fccac78b843d7d6095f42dd",
    "M31": "9ea69c72dced41580aaf8c06481d766cd80dcc4b9fccac78b843d7d6095f42dd",
}


def sha_file(p):
    with open(p, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


report = {"runner_copies": {"checked": 0, "mismatches": []},
          "historical_mtime": {"threshold_utc": CARD_START_UTC, "scanned": 0,
                               "modified_after_start": [], "errors": []},
          "cases_json_unchanged": {"checked": 0, "mismatches": []}}

# (a) every historical run_card.py copy
for root, dirs, files in os.walk(RUNS):
    if "B5-plan-level-remediation" in root:
        continue
    if "run_card.py" not in files:
        continue
    for card in CARDS:
        if os.sep + card + os.sep in root + os.sep and os.sep + card + os.sep + "a20260919-01" + os.sep in root + os.sep:
            p = os.path.join(root, "run_card.py")
            got = sha_file(p)
            report["runner_copies"]["checked"] += 1
            if got != BATCH_RUNNER_SHA[card]:
                report["runner_copies"]["mismatches"].append(
                    {"path": os.path.relpath(p, PLAN).replace("\\", "/"),
                     "expected": BATCH_RUNNER_SHA[card], "got": got})
            break

# (a2) the batch-level iso copy: execution_runs/M05-M08/a20260919-01/iso/run_card.py
batch_iso = os.path.join(RUNS, "M05-M08", "a20260919-01", "iso", "run_card.py")
if os.path.exists(batch_iso):
    got = sha_file(batch_iso)
    report["runner_copies"]["checked"] += 1
    report["runner_copies"]["batch_level_iso_copy"] = {
        "path": os.path.relpath(batch_iso, PLAN).replace("\\", "/"),
        "expected": BATCH_RUNNER_SHA["M05"], "got": got, "ok": got == BATCH_RUNNER_SHA["M05"]}
    if got != BATCH_RUNNER_SHA["M05"]:
        report["runner_copies"]["mismatches"].append(report["runner_copies"]["batch_level_iso_copy"])

# (b) cases.json of all 31 cards vs the b5_scan baseline
base = json.load(open(os.path.join(ATT, "evidence", "b5_scan.json"), encoding="utf-8"))
for card in CARDS:
    p = os.path.join(RUNS, card, "a20260919-01", "evidence", card, "cases.json")
    rec = base["cases_expected_scan"].get(card) or {}
    if not rec.get("exists"):
        continue
    got = sha_file(p)
    report["cases_json_unchanged"]["checked"] += 1
    if got != rec["sha256"]:
        report["cases_json_unchanged"]["mismatches"].append(
            {"card": card, "expected": rec["sha256"], "got": got})

# (c) mtime scan over the historical M-card attempt trees
for card in CARDS:
    tree = os.path.join(RUNS, card)
    if not os.path.isdir(tree):
        continue
    for root, dirs, files in os.walk(tree):
        for fn in files:
            p = os.path.join(root, fn)
            report["historical_mtime"]["scanned"] += 1
            try:
                mt = os.path.getmtime(p)
            except OSError as exc:
                report["historical_mtime"]["errors"].append(
                    {"path": os.path.relpath(p, PLAN).replace("\\", "/"), "error": str(exc)})
                continue
            iso = __import__("datetime").datetime.utcfromtimestamp(mt).strftime("%Y-%m-%dT%H:%M:%SZ")
            if iso > CARD_START_UTC:
                report["historical_mtime"]["modified_after_start"].append(
                    {"path": os.path.relpath(p, PLAN).replace("\\", "/"), "mtime_utc": iso})

report["PASS"] = (
    not report["runner_copies"]["mismatches"]
    and not report["cases_json_unchanged"]["mismatches"]
    and not report["historical_mtime"]["modified_after_start"]
)
dest = os.path.join(ATT, "evidence", "boundary_verification.json")
with open(dest, "w", encoding="utf-8") as fh:
    json.dump(report, fh, indent=1, ensure_ascii=False)
print("runner copies checked:", report["runner_copies"]["checked"],
      "mismatches:", len(report["runner_copies"]["mismatches"]))
print("cases.json checked:", report["cases_json_unchanged"]["checked"],
      "mismatches:", len(report["cases_json_unchanged"]["mismatches"]))
print("historical files scanned:", report["historical_mtime"]["scanned"],
      "modified after start:", len(report["historical_mtime"]["modified_after_start"]))
for m in report["historical_mtime"]["modified_after_start"][:20]:
    print("   MODIFIED:", m["path"], m["mtime_utc"])
print("PASS =", report["PASS"])
sys.exit(0 if report["PASS"] else 2)
