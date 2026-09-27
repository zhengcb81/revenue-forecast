"""R3 one-shot: verify delivered changes.diff continuity with R1 + write drift disclosure."""
import hashlib
import json
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
R1 = (ATTEMPT.parents[1] / "I-14-E-TESTSIDE" / "a20260924-01")


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


r1d = sha(R1 / "after" / "changes.diff")
m3 = sha(ATTEMPT / "after" / "changes.diff")
print("R1 changes.diff sha256 :", r1d)
print("R3 changes.diff sha256 :", m3)
print("identical_to_R1        :", r1d == m3)

drift = {
    "title": "post-copy real-repo advance on company-wiki/tests (NOT this card's change)",
    "copy_source": "execution_runs/I-14-E-TESTSIDE/a20260924-01/iso (dispatch option 1)",
    "iso_tests_manifest_this_attempt": "369aa19eb61c469dc4040ce92c80dae7dde779b3ba5e80ba8c42fc8aaa3a1c8e",
    "r1_iso_tests_manifest": "369aa19eb61c469dc4040ce92c80dae7dde779b3ba5e80ba8c42fc8aaa3a1c8e",
    "r1_cw_tests_manifest_at_copy_time": "369aa19eb61c469dc4040ce92c80dae7dde779b3ba5e80ba8c42fc8aaa3a1c8e",
    "r3_cw_tests_manifest_now": "4c65f0370261755a6fcc4fe3daa6ad62566e8642b3f37936849ba66083af80a3",
    "conclusion": ("my iso/tests is byte-faithful to the copy source and to CW/tests as of "
                   "the copy time; current CW/tests differs because the real repo advanced "
                   "after the copy (2 modified + 1 added modules)"),
    "anchor_unchanged": {
        "file": "tests/contract/test_source_catalog_worker_bootstrap.py",
        "sha256": "32515aa60d5fbfbca0778ee68e778ada7ff3bcf238f91930bb621d84aec005c1",
        "note": ("the pinned SUT anchor is still the current real-repo value; "
                 "the drift is on unrelated modules"),
    },
    "drifted_files": [
        {"path": "tests/contract/test_source_catalog_evidence_query.py", "kind": "modified",
         "r1_sha256_16": "3ca10d3bd81f9c19", "r1_bytes": 14390,
         "current_cw_sha256_16": "0dabf89144df7d67", "current_cw_bytes": 16229},
        {"path": "tests/unit/test_error_taxonomy.py", "kind": "modified",
         "r1_sha256_16": "b29c2bdfb75ac87a", "r1_bytes": 4089,
         "current_cw_sha256_16": "4c966e85a92be593", "current_cw_bytes": 4616},
        {"path": "tests/unit/test_retire_source_catalog_db.py", "kind": "added_after_copy",
         "r1_sha256_16": None, "r1_bytes": 0,
         "current_cw_sha256_16": "ec4fbf7c73a832ce", "current_cw_bytes": 10993},
    ],
    "impact_on_this_cards_runs": (
        "none of the drifted modules is collected by the single-node runs "
        "(suite::node = test_source_catalog_worker_bootstrap.py::"
        "test_child_without_runtime_session_is_terminated_and_restarted); collection "
        "inputs (bootstrap test, launcher, conftest.py, pytest.ini) are all "
        "anchor-verified and byte-equal to the copy source"),
    "boundary_check_note": (
        "after/boundary_check.json verdict string is BOUNDARY_BREACH driven solely by "
        "check iso_tests_copy_was_faithful (iso/tests vs CURRENT CW/tests); every P1 face "
        "(CW/src, CW/scripts, CW/tests, CW/pytest.ini, CW/conftest.py, iso/src, iso/scripts, "
        "iso/config, iso/pytest.ini, iso/conftest.py) is before==after equal "
        "(all_required_equal=true) and iso/tests_changed_files = exactly the application file"),
}
(ATTEMPT / "after" / "disclosure-drift.json").write_text(
    json.dumps(drift, indent=2, ensure_ascii=False), encoding="utf-8")
print("wrote after/disclosure-drift.json")
