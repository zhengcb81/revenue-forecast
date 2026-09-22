"""Append the fix-round section to changes.diff (I-08-C-REFREEZE).

Produces REAL unified diffs, verified against recorded hashes:
  * the r3 test file is reconstructed from the frozen r4 file by reversing the
    four disclosed edits (oracle R4-5); the reconstruction is accepted ONLY if
    it hashes to the recorded r3 sha256 0072b160...
  * the r3 oracle file is bytes[0:22335]; accepted ONLY if it hashes to the
    recorded pre-append sha256 94a853e9...
  * production modification set re-checked (git status --porcelain == empty)

Run:  C:\\Miniconda\\python.exe -B scratch\\fixround\\make_changes_diff.py
Exit: 0 iff every hash assertion holds.
"""
from __future__ import annotations

import difflib
import hashlib
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parents[1]
REPO = Path(r"C:\Users\郑曾波\Projects\revenue-forecast")

TEST = ATTEMPT / "test_i08c_consumer_rejection.py"
ORACLE = ATTEMPT / "oracle.md"
CHANGES = ATTEMPT / "changes.diff"

R3_TEST_SHA = "0072b16019825b46e1fa27e2decec615675cb33336eb3968fae32fb8e0dfc7f5"
R4_TEST_SHA = "3f83fdf2b7d81aba9a0bbafeb08c6c5fdf9344607fce5e5a34bb920da6454fbb"
R3_ORACLE_BYTES = 22335
R3_ORACLE_SHA = "94a853e978e34f522820cc2e03548fffe8ee2e599725d7a0131f872c93add8b3"

PRODUCTION_ANCHORS = {
    "scripts/revenue_publication.py": "183803bbd1f884b62c9ccefb40cdabf35cdc6b9d50e10501febb78b1eec448ba",
    "scripts/revenue_core.py": "1821fd2a8a4efa2b7a63c3430d310f18e1f797e2ec2635254abb7761c4bfbeae",
    "scripts/revenue_report.py": "a85fb48482216dca3f9269ee81b6d8204f419b454b64aaac14412151f00d971f",
    "scripts/publication_registry.py": "29aaae4f9864d9c4dbb92720744daa49315a2980dfa158b0e3666cb86d886344",
    "artifacts/registry/publications.jsonl": "bc3256bbc7abca8c0ae28155a614237f50860bd914578a3d48d4f74ab62d1e91",
}

# r4 literal -> r3 literal (reverse-application order does not matter: the
# four literals are disjoint).
REVERSALS: list[tuple[str, str]] = [
    (
        '# Import-root override (fix-round addition, owner-approved re-freeze card\n'
        '# I-08-C-REFREEZE).  RF_IMPORT_ROOT unset => the ORIGINAL production path\n'
        '# below, byte-identical to every prior run of this file.  Set it to a tree\n'
        '# root containing scripts/ + tests/ to run this SAME suite against that tree\n'
        "# (e.g. B1's isolated fixed copy iso/fixed/rf).  Recorded with before/after\n"
        '# file hashes in binding.json / handoff.json.\n'
        'REPO = Path(os.environ.get("RF_IMPORT_ROOT") or r"C:\\Users\\郑曾波\\Projects\\revenue-forecast")\n',
        'REPO = Path(r"C:\\Users\\郑曾波\\Projects\\revenue-forecast")\n',
    ),
    (
        '    """E1 positive control (r4 re-freeze, owner A-2).\n'
        "\n"
        "    The LABEL assertion is now tree-conditional: B1 REM-01(b) retired\n"
        '    "file existence == signing capability", so on the fixed tree an honest\n'
        "    formal package issued with a provider that cannot complete the signing\n"
        "    handshake (sys.executable) carries the truthful `unattested` label and\n"
        "    no attestation record. The r1 assertion `== \"host_signed\"` pinned the\n"
        "    I-08-A \u00a77.1 false-green shape and is superseded (oracle R4-2, E1).\n"
        "    What must hold on EITHER tree: the honest package passes both consumer\n"
        "    entry points, twice.\n"
        '    """\n'
        "    import revenue_publication as _rp\n"
        "\n"
        "    receipt = S[\"publication_receipt\"]\n"
        '    if hasattr(_rp, "validate_publication_attestation"):  # B1 fixed tree\n'
        '        assert receipt["attestation_status"] == "unattested"\n'
        '        assert "publication_attestation" not in receipt\n'
        "    else:  # production / production-identical unfixed bytes: legacy issuance\n"
        '        assert receipt["attestation_status"] == "host_signed"\n',
        '    assert S["publication_receipt"]["attestation_status"] == "host_signed"\n',
    ),
    (
        '    """E13 (r4 re-freeze, owner A-2): a self-hash-consistent forgery of\n'
        "    `segments[0].base_revenue` MUST be rejected by the strong dispatcher.\n"
        "    B1 REM-03 implements the gate; frozen rejection reason:\n"
        "    `segment base revenue mismatch`. The receipt layer still ACCEPTS it \u2014\n"
        "    that F2/REM-02 limitation (hash-consistency only, documentation fix) is\n"
        "    unchanged and stays pinned as a limitation, not a security claim.\n"
        "    Node id renamed from `..._not_bound_by_output_gates` (oracle R4-3).\n"
        '    """\n'
        "    forged = copy.deepcopy(S)\n"
        '    forged["segments"][0]["base_revenue"] = forged["segments"][0]["base_revenue"] + 1\n'
        "    _rehash(forged)\n"
        "    validate_publication_receipt(forged)  # F2 limitation: receipt layer is hash-consistency only\n"
        '    with pytest.raises(ForecastInputError, match="segment base revenue mismatch"):\n'
        "        validate_forecast_output(forged)\n",
        '    """E13 (pinned gap, oracle): self-hash-consistent segment base forgery\n'
        "    passes even the strong dispatcher (empirical, reported to reviewer).\"\"\"\n"
        "    forged = copy.deepcopy(S)\n"
        '    forged["segments"][0]["base_revenue"] = forged["segments"][0]["base_revenue"] + 1\n'
        "    _rehash(forged)\n"
        "    validate_publication_receipt(forged)\n"
        "    validate_forecast_output(forged)  # pinned: accepted by current gates\n",
    ),
    (
        '    """E11 (r4 re-freeze, owner A-2): a self-hash-consistent package that\n'
        "    CLAIMS `attestation_status='host_signed'` while carrying no\n"
        "    `publication_attestation` binding record MUST be rejected by BOTH consumer\n"
        "    entry points. B1 REM-01(a) implements the gate; frozen rejection reason:\n"
        "    `attestation_missing_record` (E27). Node id renamed from\n"
        "    `..._is_not_bound_at_consumption`, whose name asserted the retired gap\n"
        "    (oracle R4-3).\n"
        '    """\n'
        "    assert attestation_capability() is False  # issuance gate present\n"
        "    flipped = copy.deepcopy(U)\n"
        '    assert flipped["publication_receipt"]["attestation_status"] == "unattested"\n'
        '    flipped["publication_receipt"]["attestation_status"] = "host_signed"\n'
        "    _rehash(flipped)\n"
        '    with pytest.raises(ForecastInputError, match="attestation_missing_record"):\n'
        "        validate_publication_receipt(flipped)\n"
        '    with pytest.raises(ForecastInputError, match="attestation_missing_record"):\n'
        "        validate_forecast_output(flipped)\n",
        '    """KNOWN GAP (oracle E11): the label is only set-membership checked; no\n'
        '    consumption-side attestation verification exists in this tree."""\n'
        "    assert attestation_capability() is False  # issuance gate present\n"
        "    flipped = copy.deepcopy(U)\n"
        '    assert flipped["publication_receipt"]["attestation_status"] == "unattested"\n'
        '    flipped["publication_receipt"]["attestation_status"] = "host_signed"\n'
        "    _rehash(flipped)\n"
        "    validate_publication_receipt(flipped)  # GAP: label forgery accepted at receipt layer\n"
        "    validate_forecast_output(flipped)  # GAP: strong dispatcher does not bind the label\n",
    ),
    # node-id renames (r4 -> r3 names)
    (
        "def test_e11_host_signed_label_flip_is_rejected_at_consumption(U):",
        "def test_e11_host_signed_label_flip_is_not_bound_at_consumption(U):",
    ),
    (
        "def test_e13_segment_base_revenue_forgery_is_rejected_by_output_gates(S):",
        "def test_e13_segment_base_revenue_not_bound_by_output_gates(S):",
    ),
]


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def main() -> int:
    errors: list[str] = []

    r4_test = TEST.read_bytes()
    if sha256(r4_test) != R4_TEST_SHA:
        errors.append("current test file does not hash to the frozen r4 sha")

    r3_test_text = r4_test.decode("utf-8")
    for i, (new, old) in enumerate(REVERSALS, 1):
        if r3_test_text.count(new) != 1:
            errors.append(f"reversal {i}: r4 literal not found exactly once")
            continue
        r3_test_text = r3_test_text.replace(new, old, 1)
    r3_test = r3_test_text.encode("utf-8")
    r3_ok = sha256(r3_test) == R3_TEST_SHA
    if not r3_ok:
        errors.append(
            f"reconstructed r3 test file hashes to {sha256(r3_test)}, expected {R3_TEST_SHA}"
        )

    oracle = ORACLE.read_bytes()
    r3_oracle = oracle[:R3_ORACLE_BYTES]
    r3_oracle_ok = sha256(r3_oracle) == R3_ORACLE_SHA
    if not r3_oracle_ok:
        errors.append(
            f"oracle prefix [0:{R3_ORACLE_BYTES}] hashes to {sha256(r3_oracle)}, expected {R3_ORACLE_SHA}"
        )
    append_region = oracle[R3_ORACLE_BYTES:]

    porcelain = subprocess.run(
        ["git", "status", "--porcelain", "--", "scripts/", "artifacts/", "tests/", "config/"],
        cwd=REPO,
        capture_output=True,
        text=True,
    )
    prod_empty = porcelain.returncode == 0 and porcelain.stdout.strip() == ""
    if not prod_empty:
        errors.append(f"production not clean: rc={porcelain.returncode} {porcelain.stdout!r}")

    anchor_lines = []
    for rel, want in PRODUCTION_ANCHORS.items():
        got = sha256((REPO / rel).read_bytes())
        ok = got == want
        if not ok:
            errors.append(f"production anchor changed: {rel}")
        anchor_lines.append(f"#      {got}  {rel}  {'OK' if ok else 'CHANGED!'}")

    test_diff = "".join(
        difflib.unified_diff(
            r3_test.decode("utf-8").splitlines(keepends=True),
            r4_test.decode("utf-8").splitlines(keepends=True),
            fromfile="test_i08c_consumer_rejection.py (r3 frozen, sha256 "
            + R3_TEST_SHA
            + ")",
            tofile="test_i08c_consumer_rejection.py (r4 fix-round, sha256 "
            + R4_TEST_SHA
            + ")",
        )
    )

    section = f"""
# ===========================================================================
# FIX-ROUND ADDENDUM (card I-08-C-REFREEZE, append-only section; everything
# above this line is the unchanged r3 changes.diff record)
# ===========================================================================
#
# 1. PRODUCTION MODIFICATION SET IS STILL THE EMPTY SET (re-checked after all
#    four fix-round runs):
#      git status --porcelain -- scripts/ artifacts/ tests/ config/  -> EMPTY, rc 0
{chr(10).join(anchor_lines)}
#    (no git write command executed in this round either)
#
# 2. B1's attempt was executed-from READ-ONLY: after the runs, the newest
#    mtime anywhere under B1-I08C-product-fixes/a20260921-01 is
#    2026-09-21 23:14:47 (B1's own files); the fixed tree still hashes
#    revenue_publication bc2bb4a3... / revenue_core 8a761498... /
#    revenue_report 212f0059..., and iso/rf still equals production.
#    Measures: -B + PYTHONDONTWRITEBYTECODE=1 (no __pycache__ writes),
#    -p no:cacheprovider (no .pytest_cache), --basetemp inside this attempt,
#    cwd = this attempt.
#
# 3. ATTEMPT-SIDE MODIFICATION SET (this round): oracle.md append-only r4,
#    test_i08c_consumer_rejection.py (4 disclosed edits, diff below),
#    handoff.json / binding.json / commands.json / decision.md updates,
#    recovery/README.md new, scratch/fixround/** evidence, new run stdouts.
#
#    3a. oracle.md: PURE APPEND. r3 file == bytes[0:{R3_ORACLE_BYTES}] (sha256
#        {R3_ORACLE_SHA}
#        verified this round); appended region = {len(append_region)} bytes,
#        sha256 {sha256(append_region)}. The full appended text lives in
#        oracle.md itself (revision r4), so it is referenced here, not
#        duplicated.
#
#    3b. test file r3 -> r4: the reconstructed r3 side below was ACCEPTED only
#        because it hashes to {R3_TEST_SHA}
#        (the hash recorded at the r3 freeze); the r4 side hashes to
#        {R4_TEST_SHA}.
#        The four edits are exactly those disclosed in oracle.md R4-5.
#
# BEGIN UNIFIED DIFF: test file r3 -> r4 (verified reconstruction)
{test_diff}# END UNIFIED DIFF: test file r3 -> r4
#
# Modification set for this fix round outside this attempt: {{}} (empty).
# Promotion of B1's fix and acceptance of I-08-C remain SEPARATE steps.
"""

    if errors:
        print({"ok": False, "errors": errors})
        return 1

    with CHANGES.open("a", encoding="utf-8") as fh:
        fh.write(section)
    print(
        {
            "ok": True,
            "r3_test_reconstructed_sha256": sha256(r3_test),
            "r3_oracle_prefix_sha256": sha256(r3_oracle),
            "oracle_append_region_bytes": len(append_region),
            "oracle_append_region_sha256": sha256(append_region),
            "production_porcelain_empty": True,
            "changes_diff_bytes_now": CHANGES.stat().st_size,
            "changes_diff_sha256_now": sha256(CHANGES.read_bytes()),
        }
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
