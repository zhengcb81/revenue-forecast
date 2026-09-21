"""Reviewer mutation proof: re-verify the implementer's M1..M5 AND one mutation
the oracle did NOT list (M6), each applied in isolation to a fresh copy of the
fixed tree, with the declared red set checked against the observed red set.

M6 (reviewer-authored, NOT in oracle.md sections 5/r4):
    revert ONLY the "a present record is verified even when the label says
    unattested" clause of validate_publication_attestation, by short-circuiting
    on the label.  R2/R3/R4 carry no record, so the oracle's frozen expectation
    for them does not decide this clause, and R1/R7 carry the `host_signed`
    label, so they would still be caught.  Declared red set: {} (no frozen node
    moves) -- which is exactly the point: the frozen 12-node set CANNOT see this
    regression.  The reviewer therefore adds a 13th node (R13) that does, and
    requires M6 -> {R13} with every frozen node unchanged.
"""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(
    r"C:\Users\郑曾波\Projects\revenue-forecast\.planning"
    r"\2026-09-19-three-project-history-audit\execution_runs"
    r"\B1-I08C-product-fixes\a20260921-01"
)
FIXED = ATTEMPT / "iso" / "fixed" / "rf"
WORK = ATTEMPT / "reviewer" / "scratch" / "mutations"
PY = r"C:\Miniconda\python.exe"
TEST_FILE = ATTEMPT / "test_b1_rem.py"

MUTATIONS = {
    "M1": (
        "scripts/revenue_publication.py",
        "    if receipt.get(\"formal_output_mode\") == \"formal\":\n"
        "        validate_publication_attestation(result, receipt)\n",
        "",
    ),
    "M2": (
        "scripts/revenue_core.py",
        "    response = _run_attestation_provider(request)\n"
        "    if response is None:\n"
        "        return False\n"
        "    try:\n"
        "        _validate_attestation_response(request, response)\n"
        "    except ForecastInputError as exc:\n"
        "        _record_attestation_failure(str(exc))\n"
        "        return False\n"
        "    return True\n",
        "    return bool(os.environ.get(\"REVENUE_ATTESTATION_PROVIDER\"))\n",
    ),
    "M3": (
        "scripts/revenue_report.py",
        "    _validate_segment_opening_bases(result, parameter_index, years)\n",
        "",
    ),
    "M4": (
        "scripts/revenue_publication.py",
        "    \"\"\"Hash-consistency check on one publication receipt — **NOT a security boundary**.\n",
        "    \"\"\"Hash-consistency check on one publication receipt.\n",
    ),
    "M5": (
        "scripts/revenue_publication.py",
        "    request = publication_attestation_request(\n"
        "        request_id=record[\"request_id\"],\n"
        "        payload_sha256=record[\"payload_sha256\"],\n"
        "        result_sha256=SIGNED_RESULT_SHA256_SENTINEL,\n"
        "    )\n"
        "    message = canonical_sha256(request).encode(\"ascii\")\n"
        "    verify_ed25519_signature(record[\"fingerprint\"], record[\"signature\"], message)\n",
        "",
    ),
    # ---- reviewer-authored, NOT in the oracle -------------------------------
    "M6": (
        "scripts/revenue_publication.py",
        "    require(\n"
        "        record[\"payload_sha256\"] == receipt.get(\"validated_payload_sha256\"),",
        "    if not claims_signed:\n"
        "        # MUTATION M6: only a labelled claim is held to its record.\n"
        "        return\n"
        "    require(\n"
        "        record[\"payload_sha256\"] == receipt.get(\"validated_payload_sha256\"),",
    ),
}

DECLARED = {
    "M1": {"test_rem01_a_label_only_flip_is_rejected", "test_rem01_g_replayed_record_is_rejected"},
    "M2": {
        "test_rem01_b_to_d_file_existence_is_not_signing_capability[plain_txt]",
        "test_rem01_b_to_d_file_existence_is_not_signing_capability[bare_py]",
        "test_rem01_b_to_d_file_existence_is_not_signing_capability[sys_executable]",
        "test_rem01_f_untrusted_provider_is_not_host_signed",
    },
    "M3": {
        "test_rem03_forged_segment_base_revenue_is_rejected",
        "test_rem03_moving_base_and_total_together_is_still_rejected",
    },
    "M4": {"test_rem02_receipt_layer_is_documented_as_non_security"},
    "M5": {"test_rem01_g_replayed_record_is_rejected"},
    "M6": set(),
}

results = {}
WORK.mkdir(parents=True, exist_ok=True)
for name, (relpath, old, new) in MUTATIONS.items():
    target = WORK / name / "rf"
    if target.exists():
        shutil.rmtree(target, ignore_errors=True)
    shutil.copytree(FIXED, target)
    victim = target / relpath
    text = victim.read_text(encoding="utf-8")
    if text.count(old) != 1:
        results[name] = {"error": f"literal not found exactly once ({text.count(old)})"}
        print(f"{name}: ERROR literal count {text.count(old)}")
        continue
    victim.write_text(text.replace(old, new), encoding="utf-8")

    env = dict(os.environ)
    env["B1_REPO_ROOT"] = str(target)
    env["PYTHONPATH"] = f"{target / 'scripts'};{target / 'tests'}"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["REVENUE_PUBLICATION_REGISTRY"] = str(WORK / name / "registry.jsonl")
    env.pop("REVENUE_ATTESTATION_PROVIDER", None)
    env.pop("REVENUE_TRUSTED_SIGNER_PUBLIC_KEYS", None)
    (WORK / name).mkdir(parents=True, exist_ok=True)
    proc = subprocess.run(
        [PY, "-X", "utf8", "-B", "-m", "pytest", "-p", "no:cacheprovider",
         "-q", "--no-header", "-rA", str(TEST_FILE)],
        cwd=str(ATTEMPT), env=env, capture_output=True, text=True, timeout=900,
    )
    stdout = proc.stdout
    (WORK / name / "pytest.stdout.txt").write_text(stdout, encoding="utf-8")
    (WORK / name / "rc.txt").write_text(str(proc.returncode), encoding="ascii")
    observed = {
        line.split("::", 1)[1].split(" ")[0].strip()
        for line in stdout.splitlines()
        if line.startswith("FAILED ")
    }
    declared = DECLARED[name]
    results[name] = {
        "rc": proc.returncode,
        "observed_red": sorted(observed),
        "declared_red": sorted(declared),
        "missing": sorted(declared - observed),
        "unexpected": sorted(observed - declared),
        "isolated": declared == observed,
    }
    print(f"{name}: rc={proc.returncode} observed={sorted(observed)}")
    print(f"    declared={sorted(declared)} missing={sorted(declared - observed)} "
          f"unexpected={sorted(observed - declared)} isolated={declared == observed}")

(WORK / "reviewer_mutation_proof.json").write_text(
    json.dumps(results, indent=1, sort_keys=True), encoding="utf-8"
)
print("\nWROTE", WORK / "reviewer_mutation_proof.json")
