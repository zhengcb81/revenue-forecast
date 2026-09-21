"""Mutation proof: revert each fix in an isolated copy and re-run the frozen tests.

Design.  For each mutation the harness declares, PER NODE, whether the node is
expected to go red (because it measures the reverted property) or to stay green
(positive controls and every node measuring a different fix).  Nothing is ever
patched in place: `iso/fixed/rf` is the reference and stays byte-stable, and each
mutation gets a fresh copy at `scratch/mutations/<id>/rf`.

A mutation PASSES its isolation claim when the observed outcome set equals the
declared one exactly — no extra red, no missing red.  A node that unexpectedly
goes red is reported as a DEPENDENCY (a second node the fix is load-bearing for),
not hidden; a node that unexpectedly goes green is reported as a FAILURE.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ATTEMPT = Path(sys.argv[1]).resolve()
FIXED = ATTEMPT / "iso" / "fixed" / "rf"
MUT_ROOT = ATTEMPT / "scratch" / "mutations"
PY = sys.executable
TEST_FILE = ATTEMPT / "test_b1_rem.py"

PUB = "scripts/revenue_publication.py"
CORE = "scripts/revenue_core.py"
REPORT = "scripts/revenue_report.py"

CAP_TXT = "test_rem01_b_to_d_file_existence_is_not_signing_capability[plain_txt]"
CAP_PY = "test_rem01_b_to_d_file_existence_is_not_signing_capability[bare_py]"
CAP_EXE = "test_rem01_b_to_d_file_existence_is_not_signing_capability[sys_executable]"

ALL_NODES = (
    "test_rem01_a_label_only_flip_is_rejected",
    CAP_TXT,
    CAP_PY,
    CAP_EXE,
    "test_rem01_e_trusted_provider_yields_verifiable_record",
    "test_rem01_f_untrusted_provider_is_not_host_signed",
    "test_rem01_g_replayed_record_is_rejected",
    "test_rem01_h_signed_record_is_repeatable_and_stable",
    "test_rem02_receipt_layer_is_documented_as_non_security",
    "test_rem03_forged_segment_base_revenue_is_rejected",
    "test_rem03_honest_package_still_accepted",
    "test_rem03_moving_base_and_total_together_is_still_rejected",
)

MUTATIONS: list[dict] = [
    {
        "id": "M1",
        "fix": "REM-01(a) — the label requires a verifying binding record",
        "file": PUB,
        "old": """    if receipt.get("formal_output_mode") == "formal":
        validate_publication_attestation(result, receipt)""",
        "new": """    if receipt.get("formal_output_mode") == "formal":
        pass  # MUTATION M1: record requirement removed""",
        "expected_red": [
            "test_rem01_a_label_only_flip_is_rejected",
            "test_rem01_g_replayed_record_is_rejected",
        ],
        "why": "R1 is the label-forgery node. R7 is red as a DECLARED DEPENDENCY, "
        "not as collateral: reverting the whole validate_publication_attestation call "
        "removes every record check, so the replayed/forged record is no longer "
        "rejected either. The capability nodes stay green because M1 does not touch "
        "the issuance side — that is what proves the two halves of REM-01 are "
        "separately load-bearing.",
    },
    {
        "id": "M2",
        "fix": "REM-01(b) — file existence is not signing capability",
        "file": CORE,
        "old": """    global _ATTESTATION_LAST_FAILURE
    _ATTESTATION_LAST_FAILURE = None
    from revenue_publication import (
        publication_attestation_request,
    )

    request = publication_attestation_request(
        request_id=secrets.token_hex(32),
        payload_sha256=hashlib.sha256(b"capability-probe").hexdigest(),
    )
    response = _run_attestation_provider(request)
    if response is None:
        return False
    try:
        _validate_attestation_response(request, response)
    except ForecastInputError as exc:
        _record_attestation_failure(str(exc))
        return False
    return True""",
        "new": """    # MUTATION M2: restored to the pre-fix file-existence semantics
    provider = os.environ.get("REVENUE_ATTESTATION_PROVIDER")
    if not provider:
        return False
    resolved = shutil.which(provider) or Path(provider).expanduser()
    return resolved is not None and os.path.isfile(resolved)""",
        "expected_red": [CAP_TXT, CAP_PY, CAP_EXE, "test_rem01_f_untrusted_provider_is_not_host_signed"],
        "why": "the three capability nodes are the direct measurement. R6 is a "
        "DECLARED DEPENDENCY: it asserts both that capability is False AND that the "
        "recorded failure code is provider_key_untrusted, and with file-existence "
        "capability the host never reaches the trust check. R1/R7/R5/R8 stay green, "
        "proving the consumption-side binding is independent of the issuance gate.",
    },
    {
        "id": "M3",
        "fix": "REM-03 — segments[i].base_revenue is bound by an output gate",
        "file": REPORT,
        "old": "    _validate_segment_opening_bases(result, parameter_index, years)",
        "new": "    pass  # MUTATION M3: opening-base gates removed",
        "expected_red": [
            "test_rem03_forged_segment_base_revenue_is_rejected",
            "test_rem03_moving_base_and_total_together_is_still_rejected",
        ],
        "why": "exactly the two REM-03 nodes; the honest positive control R11 and "
        "every REM-01/REM-02 node stay green.",
    },
    {
        "id": "M4",
        "fix": "REM-02 — the receipt layer is documented as non-security",
        "file": PUB,
        "old": '    """Hash-consistency check on one publication receipt — **NOT a security boundary**.',
        "new": '    """Hash-consistency check on one publication receipt.',
        "expected_red": ["test_rem02_receipt_layer_is_documented_as_non_security"],
        "why": "exactly the REM-02 node; every other node stays green, including the "
        "two nodes that assert the receipt layer still enforces the attestation binding.",
    },
    {
        "id": "M5",
        "fix": "REM-01(a) — a PRESENT record is actually verified",
        "file": PUB,
        "old": """    request = publication_attestation_request(
        request_id=record["request_id"],
        payload_sha256=record["payload_sha256"],
        result_sha256=SIGNED_RESULT_SHA256_SENTINEL,
    )
    message = canonical_sha256(request).encode("ascii")
    verify_ed25519_signature(record["fingerprint"], record["signature"], message)""",
        "new": """    # MUTATION M5: record contents are accepted without verification
    return""",
        "expected_red": ["test_rem01_g_replayed_record_is_rejected"],
        "why": "exactly the replay/forgery node. R1 stays green because E27 is a "
        "different require() in the same function, and R5/R8 stay green because they "
        "assert the record's presence and field set, which M5 leaves intact.",
    },
]

TREE_HASH_FILES = [PUB, CORE, REPORT, "scripts/contracts/evidence.py"]


def tree_hashes(root: Path) -> dict[str, str]:
    return {
        rel: hashlib.sha256((root / rel).read_bytes()).hexdigest()
        for rel in TREE_HASH_FILES
    }


def parse_outcomes(text: str) -> dict[str, str]:
    """Map node id -> status from pytest's `-rA` short summary (truncated keys)."""
    outcomes: dict[str, str] = {}
    for line in text.splitlines():
        for status in ("PASSED", "FAILED", "ERROR"):
            prefix = status + " "
            if line.startswith(prefix) and "::" in line:
                outcomes[line.split("::", 1)[1].strip()] = status
    return outcomes


def outcome_for(outcomes: dict[str, str], node: str) -> str:
    if node in outcomes:
        return outcomes[node]
    for key, status in outcomes.items():
        if key.startswith(node) or node.startswith(key):
            return status
    return "MISSING"


def main() -> int:
    MUT_ROOT.mkdir(parents=True, exist_ok=True)
    report: dict = {
        "reference_tree": str(FIXED),
        "reference_hashes": tree_hashes(FIXED),
        "frozen_test_file": str(TEST_FILE),
        "frozen_test_file_sha256": hashlib.sha256(TEST_FILE.read_bytes()).hexdigest(),
        "method": "for each mutation: fresh copy of the reference tree, one exact "
        "literal revert (verified present first), run the SAME unmodified frozen test "
        "file, compare the observed red set against the declared red set exactly",
        "mutations": [],
    }
    all_ok = True
    for spec in MUTATIONS:
        target = MUT_ROOT / spec["id"] / "rf"
        if target.parent.exists():
            shutil.rmtree(target.parent)
        target.parent.mkdir(parents=True)
        shutil.copytree(FIXED, target, ignore=shutil.ignore_patterns("__pycache__"))
        path = target / spec["file"]
        text = path.read_text(encoding="utf-8")
        if spec["old"] not in text:
            raise SystemExit(f"{spec['id']}: patch target not found in {spec['file']}")
        path.write_text(text.replace(spec["old"], spec["new"], 1), encoding="utf-8")

        outdir = MUT_ROOT / spec["id"]
        cmd = [
            PY, "-X", "utf8", "-B", "-m", "pytest", "-p", "no:cacheprovider",
            "-q", "--no-header", "-rA", str(TEST_FILE),
        ]
        env = {
            **os.environ,
            "B1_REPO_ROOT": str(target),
            "PYTHONDONTWRITEBYTECODE": "1",
            "REVENUE_PUBLICATION_REGISTRY": str(outdir / "registry.jsonl"),
            "PYTHONPATH": f"{target / 'scripts'}{os.pathsep}{target / 'tests'}",
        }
        completed = subprocess.run(cmd, capture_output=True, env=env, cwd=str(ATTEMPT), check=False)
        (outdir / "pytest.stdout.txt").write_bytes(completed.stdout)
        (outdir / "pytest.stderr.txt").write_bytes(completed.stderr)
        (outdir / "rc.txt").write_text(str(completed.returncode), encoding="ascii")
        outcomes = parse_outcomes(completed.stdout.decode("utf-8", "replace"))

        observed_red = sorted(
            node for node in ALL_NODES if outcome_for(outcomes, node) != "PASSED"
        )
        declared_red = sorted(spec["expected_red"])
        missing_red = [n for n in declared_red if n not in observed_red]
        extra_red = [n for n in observed_red if n not in declared_red]
        isolation_ok = not missing_red and not extra_red
        all_ok = all_ok and isolation_ok
        report["mutations"].append(
            {
                "id": spec["id"],
                "fix_reverted": spec["fix"],
                "file": spec["file"],
                "why": spec["why"],
                "patched_from_sha256": hashlib.sha256((FIXED / spec["file"]).read_bytes()).hexdigest(),
                "patched_to_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "pytest_raw_rc": completed.returncode,
                "declared_red": declared_red,
                "observed_red": observed_red,
                "missing_red": missing_red,
                "unexpected_red": extra_red,
                "isolation_of_proof_ok": isolation_ok,
                "evidence": f"scratch/mutations/{spec['id']}/pytest.stdout.txt + rc.txt",
            }
        )
        print(
            f"{spec['id']}: raw_rc={completed.returncode} observed_red={observed_red} "
            f"missing={missing_red} unexpected={extra_red} ISOLATED={isolation_ok}"
        )
    (MUT_ROOT / "mutation_proof.json").write_text(
        json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("ALL MUTATIONS ISOLATED:", all_ok)
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
