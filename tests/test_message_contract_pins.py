"""Message-contract pins — verbatim text assertions (FIX-W06-GAPS P4-SCOPE).

SCENARIO: FIX-W06-GAPS (card FIX-W06-GAPS, owner ruling 「fail 的全部要修复」;
pin face 2 = the RF product test surface).  Replaces the loose
`match="not reviewed|blocked"` style coverage with VERBATIM, assertable pins
for the message contracts the OPEN5-DOUBT-PROBE sweep (evidence
04_blocked_message_sweep.md) found UNPINNED, so a one-byte wording change
turns these tests red instead of passing silently:

  #2  the full blocked sentence (RF scripts/source_preparation.py) — verbatim;
  #5  the six demand/claim refusal texts (RF + CW processing_demand.py) —
      verbatim behavior pins AND cross-repo (RF/CW) equality (逐字同文);
  #8  the "{field} must be a lowercase SHA-256" family — verbatim behavior pins;
  #9  the parser/llm counts fail-closed sentence — verbatim.
  #3  `cases_json_declared_expectation_missing` = RUNNER vocabulary, not
      product vocabulary (per decision.md clarification): the correct state
      is ZERO hits in both repos — pinned as a structural zero-hit assertion.
  #6  resume refusal text: product surface is ABSENT (unbuilt interface,
      OPEN-5 C4 pending instantiation) — pinned as structural absence so the
      current state cannot drift unnoticed.

Path overrides for mutation testing (flip one byte in a copy, point the env
vars at the copy, expect RED):
  GAPS_PIN_RF_SCRIPTS  default <repo>/scripts
  GAPS_PIN_CW_DIR      default <repo>/../company-wiki/src/company_wiki/source_catalog
"""
from __future__ import annotations

import importlib.util
import os
import shutil
import sqlite3
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# Host-neutral defaults (host_assumption_guard: no host-absolute literals).
# The product tests/ dir and the attempt's iso copy both resolve via ROOT;
# attempt/mutation contexts override via GAPS_PIN_RF_SCRIPTS / GAPS_PIN_CW_DIR
# (see module docstring) — missing checkouts reach the skips below instead of
# a baked-in machine path.
_RF_DEFAULT = ROOT / "scripts"
_CW_DEFAULT = ROOT.parent / "company-wiki" / "src" / "company_wiki" / "source_catalog"

RF_SCRIPTS = Path(os.environ.get("GAPS_PIN_RF_SCRIPTS", _RF_DEFAULT))
CW_DIR = Path(os.environ.get("GAPS_PIN_CW_DIR", _CW_DEFAULT))

BLOCK_SENTENCE = (
    "prompt injection not reviewed — source preparation blocked per "
    "policy (prompt_injection_status=not_reviewed)"
)
COUNTS_SENTENCE = (
    "parser/llm counts absent from the resolution envelope — fail "
    "closed instead of fabricating 0"
)

# (case id, contract form, verbatim rendered text) — oracle M-P2 item 15.
REFUSAL_CONTRACT = {
    "missing": ('f"no demand {demand_id!r}"', "no demand 'pd-x'"),
    "not_claimable": ('f"demand {demand_id!r} is not claimable"',
                      "demand 'pd-0' is not claimable"),
    "backoff": ('f"demand {demand_id!r} is in backoff"',
                "demand 'pd-0' is in backoff"),
    "no_ready": ('"no ready demand to claim"', "no ready demand to claim"),
    "wrong_owner": ("f\"lease owned by {demand.lease_owner!r}\"",
                    "lease owned by 'w1'"),
    "lease_expired": ('"lease expired"', "lease expired"),
}


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod  # dataclasses need module registration
    spec.loader.exec_module(mod)
    return mod


def _load_rf_demand():
    return _load_module(f"pin_rf_demand_{id(object())}", RF_SCRIPTS / "processing_demand.py")


def _drive_six_refusals(mod) -> dict:
    texts: dict[str, str] = {}
    q = mod.DemandQueue(lease_seconds=10.0)
    try:
        q.claim(owner="w", now=1.0, demand_id="pd-x")
    except Exception as exc:  # noqa: BLE001
        texts["missing"] = str(exc)
    q = mod.DemandQueue(lease_seconds=10.0)
    d = q.enqueue(key="k", kind="review", now=0.0)
    q.claim(owner="tA", now=1.0, demand_id=d.demand_id)
    try:
        q.claim(owner="tB", now=2.0, demand_id=d.demand_id)
    except Exception as exc:  # noqa: BLE001
        texts["not_claimable"] = str(exc)
    q = mod.DemandQueue(lease_seconds=10.0)
    d = q.enqueue(key="k", kind="review", now=0.0)
    q.claim(owner="tA", now=0.0, demand_id=d.demand_id)
    q.fail(demand_id=d.demand_id, owner="tA", now=1.0)
    try:
        q.claim(owner="tA", now=2.0, demand_id=d.demand_id)
    except Exception as exc:  # noqa: BLE001
        texts["backoff"] = str(exc)
    q = mod.DemandQueue(lease_seconds=10.0)
    try:
        q.claim(owner="w", now=1.0)
    except Exception as exc:  # noqa: BLE001
        texts["no_ready"] = str(exc)
    q = mod.DemandQueue(lease_seconds=10.0)
    d = q.enqueue(key="k", kind="review", now=0.0)
    q.claim(owner="w1", now=1.0, demand_id=d.demand_id)
    try:
        q.complete(demand_id=d.demand_id, owner="w2", now=2.0)
    except Exception as exc:  # noqa: BLE001
        texts["wrong_owner"] = str(exc)
    q = mod.DemandQueue(lease_seconds=10.0)
    d = q.enqueue(key="k", kind="review", now=0.0)
    q.claim(owner="w1", now=0.0, demand_id=d.demand_id)
    try:
        q.complete(demand_id=d.demand_id, owner="w1", now=20.0)
    except Exception as exc:  # noqa: BLE001
        texts["lease_expired"] = str(exc)
    return texts


def _load_cw_pair(tmp_path: Path):
    """prompt_injection + prompt_injection_guard as a real mini package."""
    pkg = tmp_path / "pi_pkg"
    if not pkg.exists():
        pkg.mkdir()
        (pkg / "__init__.py").write_text("", encoding="utf-8")
        for name in ("prompt_injection.py", "prompt_injection_guard.py"):
            shutil.copy2(CW_DIR / name, pkg / name)
    sys.path.insert(0, str(tmp_path))
    try:
        pi = importlib.import_module("pi_pkg.prompt_injection")
        guard = importlib.import_module("pi_pkg.prompt_injection_guard")
    finally:
        sys.path.remove(str(tmp_path))
    return pi, guard


# --- #2: the full blocked sentence, verbatim --------------------------------


def test_block_sentence_pinned_verbatim():
    import ast

    source = (RF_SCRIPTS / "source_preparation.py").read_text(encoding="utf-8")
    constants = [
        node.value for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    assert BLOCK_SENTENCE in constants, (
        "the full blocked sentence drifted from its pinned verbatim text")
    assert constants.count(BLOCK_SENTENCE) == 1


# --- #9: parser/llm counts fail-closed sentence, verbatim -------------------


def test_counts_sentence_pinned_verbatim():
    import ast

    source = (RF_SCRIPTS / "source_preparation.py").read_text(encoding="utf-8")
    constants = [
        node.value for node in ast.walk(ast.parse(source))
        if isinstance(node, ast.Constant) and isinstance(node.value, str)
    ]
    assert COUNTS_SENTENCE in constants


# --- #5: six demand/claim refusal texts, verbatim + cross-repo equality ------


def test_six_refusal_texts_pinned_verbatim_rf():
    texts = _drive_six_refusals(_load_rf_demand())
    assert texts == {case: verbatim for case, (_, verbatim)
                     in REFUSAL_CONTRACT.items()}


def test_six_refusal_texts_cross_repo_equal_cw():
    if not (CW_DIR / "processing_demand.py").is_file():
        pytest.skip(f"company-wiki checkout not found at {CW_DIR}")
    texts = _drive_six_refusals(
        _load_module(f"pin_cw_demand_{id(object())}",
                     CW_DIR / "processing_demand.py"))
    assert texts == {case: verbatim for case, (_, verbatim)
                     in REFUSAL_CONTRACT.items()}


def test_six_refusal_sources_verbatim_identical():
    if not (CW_DIR / "processing_demand.py").is_file():
        pytest.skip(f"company-wiki checkout not found at {CW_DIR}")
    for _, verbatim in REFUSAL_CONTRACT.values():
        rendered_literal = verbatim.split(" '")[0] if "'" in verbatim else verbatim
        # both repos must contain the same source-level message text
        rf_src = (RF_SCRIPTS / "processing_demand.py").read_text(encoding="utf-8")
        cw_src = (CW_DIR / "processing_demand.py").read_text(encoding="utf-8")
        token = {
            "no demand 'pd-x'": "no demand {demand_id!r}",
            "demand 'pd-0' is not claimable": "is not claimable",
            "demand 'pd-0' is in backoff": "is in backoff",
            "no ready demand to claim": "no ready demand to claim",
            "lease owned by 'w1'": "lease owned by {demand.lease_owner!r}",
            "lease expired": '"lease expired"',
        }[verbatim]
        assert token in rf_src and token in cw_src, rendered_literal


# --- #8: "{field} must be a lowercase SHA-256" family, verbatim -------------


def test_lowercase_sha256_family_pinned(tmp_path):
    pi, guard = _load_cw_pair(tmp_path)
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE documents (document_id TEXT PRIMARY KEY, metadata_json TEXT)")
    con.execute("INSERT INTO documents VALUES('doc-1', '{}')")
    with pytest.raises(ValueError) as excinfo:
        pi.record_prompt_injection_review(
            con, "doc-1", status="not_detected", reviewer="r",
            evidence_sha256="ABC", now="2026-09-22T00:00:00Z")
    assert str(excinfo.value) == "evidence_sha256 must be a lowercase SHA-256"
    with pytest.raises(ValueError) as excinfo:
        guard.scan_text("x", ruleset_hash="ABC")
    assert str(excinfo.value) == "ruleset_hash must be a lowercase SHA-256"
    with pytest.raises(ValueError) as excinfo:
        guard.evaluate_review(
            con, "doc-1", source_sha256="ABC", policy_hash="b" * 64,
            now="2026-09-22T00:00:00Z", ttl_seconds=1.0)
    assert str(excinfo.value) == "source_sha256 must be a lowercase SHA-256"
    with pytest.raises(ValueError) as excinfo:
        guard.evaluate_review(
            con, "doc-1", source_sha256="b" * 64, policy_hash="ABC",
            now="2026-09-22T00:00:00Z", ttl_seconds=1.0)
    assert str(excinfo.value) == "policy_hash must be a lowercase SHA-256"


# --- #3: runner vocabulary is NOT product vocabulary (structural zero-hit) ---


def test_cases_json_declared_expectation_missing_absent_in_product():
    needle = "cases_json_declared_expectation_missing"
    for tree in (RF_SCRIPTS, CW_DIR):
        if not tree.is_dir():
            continue
        for path in tree.rglob("*.py"):
            assert needle not in path.read_text(encoding="utf-8", errors="replace"), (
                f"{needle!r} unexpectedly present in {path} — "
                f"it is RUNNER vocabulary (M01-M04 runner side), not product vocabulary")


# --- #6: resume surface is structurally ABSENT (OPEN-5 C4 pending) ----------


def test_resume_refusal_surface_structurally_absent():
    mod = _load_rf_demand()
    assert not hasattr(mod.DemandQueue, "resume")  # OPEN-5 C4: pending instantiation
    for path in (RF_SCRIPTS / "processing_demand.py",
                 CW_DIR / "processing_demand.py"):
        if path.is_file():
            assert "def resume" not in path.read_text(encoding="utf-8")
