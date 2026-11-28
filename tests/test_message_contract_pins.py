"""Message-contract pins — verbatim text assertions (FIX-W06-GAPS P4-SCOPE).

SCENARIO: FIX-W06-GAPS (card FIX-W06-GAPS, owner ruling 「fail 的全部要修复」;
pin face 2 = the RF product test surface).  Replaces the loose
`match="not reviewed|blocked"` style coverage with VERBATIM, assertable pins
for the message contracts the OPEN5-DOUBT-PROBE sweep (evidence
04_blocked_message_sweep.md) found UNPINNED, so a one-byte wording change
turns these tests red instead of passing silently:

  #2  the former review block is superseded by verified-byte consumption;
  #5  the six demand/claim refusal texts (archived RF + CW processing_demand.py) —
      verbatim behavior pins AND cross-repo (RF/CW) equality (逐字同文);
  #8  the RF-owned SourceRef lowercase SHA-256 wire failure;
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
import json
import os
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
if not _CW_DEFAULT.is_dir():  # lanes worktree layout: sibling under ~/Projects
    _CW_DEFAULT = Path.home() / "Projects" / "company-wiki" / "src" / "company_wiki" / "source_catalog"

RF_SCRIPTS = Path(os.environ.get("GAPS_PIN_RF_SCRIPTS", _RF_DEFAULT))
RF_DEMAND = ROOT / "tools" / "legacy" / "processing_demand.py"
CW_DIR = Path(os.environ.get("GAPS_PIN_CW_DIR", _CW_DEFAULT))

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
    return _load_module(f"pin_rf_demand_{id(object())}", RF_DEMAND)


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


# --- #9: parser/llm counts fail-closed sentence ----------------------------


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


@pytest.mark.composition
def test_six_refusal_texts_cross_repo_equal_cw():
    if not (CW_DIR / "processing_demand.py").is_file():
        pytest.skip(f"company-wiki checkout not found at {CW_DIR}")
    texts = _drive_six_refusals(
        _load_module(f"pin_cw_demand_{id(object())}",
                     CW_DIR / "processing_demand.py"))
    assert texts == {case: verbatim for case, (_, verbatim)
                     in REFUSAL_CONTRACT.items()}


@pytest.mark.composition
def test_six_refusal_sources_verbatim_identical():
    if not (CW_DIR / "processing_demand.py").is_file():
        pytest.skip(f"company-wiki checkout not found at {CW_DIR}")
    for _, verbatim in REFUSAL_CONTRACT.values():
        rendered_literal = verbatim.split(" '")[0] if "'" in verbatim else verbatim
        # both repos must contain the same source-level message text
        rf_src = (RF_DEMAND).read_text(encoding="utf-8")
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


# --- #8: RF SourceRef lowercase SHA-256 -------------------------------------


def test_rf_source_ref_requires_a_lowercase_sha256_before_reader_io(tmp_path, monkeypatch):
    monkeypatch.syspath_prepend(str(RF_SCRIPTS))
    import company_wiki_source_reader_v2 as reader

    source = json.loads((ROOT / "tests" / "fixtures" / "cwp_source_ref_v2.json").read_text(encoding="utf-8"))
    source["content_sha256"] = "A" * 64

    def forbidden(*_args, **_kwargs):
        pytest.fail("invalid hash reached the source reader process")

    monkeypatch.setattr(reader, "_run_reader", forbidden)
    with pytest.raises(reader.SourceVersionTransportError) as failure:
        reader.open_source_version_v2(
            source_ref=source, catalog_config=tmp_path / "catalog.json",
            as_of_date="2026-07-18", expected_fiscal_year=2025,
        )
    assert str(failure.value) == "source_ref SHA-256 is invalid"


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
    for path in (RF_DEMAND,
                 CW_DIR / "processing_demand.py"):
        if path.is_file():
            assert "def resume" not in path.read_text(encoding="utf-8")
