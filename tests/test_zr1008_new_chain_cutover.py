"""ZR-1008 acceptance tests: source/revenue new-chain cohort cutover.

Stage I eighth card.  The NEW chain (mine-facts shadow path + formal
forecast publication) is cut over as a cohort with observation-period
discipline: the full user journey must run on production entry points
(prepare_forecast draft -> formal), draft/formal separation holds
(draft never publishes; formal carries strong gates + attestation),
SLO is met, side effects are exactly one registry entry, and a
rollback during the observation window restores the previous state
without leaving partial artifacts (replay stays bit-identical).

  C1  journey: draft renders without publishing; formal registers
      exactly one entry; formal results replay bit-identically.
  C2  draft/formal separation: draft receipt marks draft mode with
      empty gates; formal receipt carries non-empty gate_ids +
      attestation; a draft receipt flipped to formal is rejected.
  C3  SLO: the cutover journey (draft + formal + replay) completes
      within a frozen wall-clock budget.
  C4  side effects: formal adds exactly one registry entry bound to
      input_sha256/result_sha256; draft adds none; no other files
      are created.
  C5  rollback/observation: deleting the cutover entry (rollback)
      restores the pre-cutover registry; re-running the same input
      in the observation window produces the identical result hash
      (no drift), and a second formal re-registers cleanly.
"""

from __future__ import annotations

import copy
import json
import sys
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from revenue_forecast import prepare_forecast  # noqa: E402
from revenue_publication import (  # noqa: E402
    build_publication_receipt,
    validate_publication_receipt,
)
from revenue_report import render_markdown  # noqa: E402
from test_zr709_zijin_journey import _zijin_document  # noqa: E402

JOURNEY_SLO_SECONDS = 60.0  # frozen wall-clock budget for the cutover journey


@pytest.fixture(name="registry_path")
def _registry_path(tmp_path, monkeypatch):
    path = tmp_path / "pub" / "publications.jsonl"
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY", str(path))
    return path


def _entries(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


# ---------------------------------------------------------------------------
# C1 — journey: draft renders, formal registers once, replay identical
# ---------------------------------------------------------------------------


def test_c1_cutover_journey_draft_then_formal(registry_path):
    document = _zijin_document()
    # draft first: renders, registers nothing
    draft = prepare_forecast(copy.deepcopy(document), mode="draft")
    markdown = render_markdown(draft)
    assert len(markdown) > 500
    assert draft["publication_receipt"]["formal_output_mode"] == "draft"
    assert not registry_path.exists()

    # formal cutover: registers exactly one entry
    formal = prepare_forecast(copy.deepcopy(document), mode="formal")
    entries = _entries(registry_path)
    assert len(entries) == 1
    assert entries[0]["input_sha256"] == formal["input_sha256"]
    assert entries[0]["result_sha256"] == formal["result_sha256"]

    # replay in the observation window: bit-identical result
    replay = prepare_forecast(copy.deepcopy(document), mode="formal")
    assert replay == formal
    assert replay["result_sha256"] == formal["result_sha256"]
    assert len(_entries(registry_path)) == 2  # second formal = 2nd entry, same result


def test_c1_snapshot_round_trip_replays(registry_path):
    from revenue_backtest import create_snapshot, validate_snapshot

    document = _zijin_document()
    one = create_snapshot(copy.deepcopy(document), "zr1008-cutover-v1")
    validate_snapshot(one)
    two = create_snapshot(copy.deepcopy(document), "zr1008-cutover-v1")
    assert one["snapshot_id"] == two["snapshot_id"]


# ---------------------------------------------------------------------------
# C2 — draft/formal separation holds
# ---------------------------------------------------------------------------


def test_c2_draft_receipt_marks_draft_mode(registry_path):
    draft = prepare_forecast(_zijin_document(), mode="draft")
    receipt = draft["publication_receipt"]
    assert receipt["formal_output_mode"] == "draft"
    assert receipt["gate_ids"] == []
    # draft flip to formal is rejected (REV-08a)
    flipped = copy.deepcopy(draft)
    flipped["publication_receipt"]["formal_output_mode"] = "formal"
    with pytest.raises(Exception):
        validate_publication_receipt(flipped)


def test_c2_formal_receipt_has_gates_and_attestation(registry_path):
    formal = prepare_forecast(_zijin_document())
    receipt = formal["publication_receipt"]
    assert receipt["formal_output_mode"] == "formal"
    assert receipt["gate_ids"]
    assert receipt["attestation_status"] in {"host_signed", "unattested"}
    validate_publication_receipt(formal)
    # downgrading formal to draft is also rejected
    downgraded = copy.deepcopy(formal)
    downgraded["publication_receipt"]["formal_output_mode"] = "draft"
    with pytest.raises(Exception):
        validate_publication_receipt(downgraded)


def test_c2_no_self_issued_formal_without_context(registry_path):
    document = _zijin_document()
    result = prepare_forecast(copy.deepcopy(document), mode="draft")
    with pytest.raises(TypeError):
        build_publication_receipt(result)  # needs a VerificationContext


# ---------------------------------------------------------------------------
# C3 — SLO: the cutover journey completes within budget
# ---------------------------------------------------------------------------


def test_c3_journey_within_slo(registry_path):
    document = _zijin_document()
    start = time.monotonic()
    draft = prepare_forecast(copy.deepcopy(document), mode="draft")
    render_markdown(draft)
    formal = prepare_forecast(copy.deepcopy(document), mode="formal")
    replay = prepare_forecast(copy.deepcopy(document), mode="formal")
    assert replay == formal
    elapsed = time.monotonic() - start
    assert elapsed < JOURNEY_SLO_SECONDS, f"journey took {elapsed:.2f}s (SLO {JOURNEY_SLO_SECONDS}s)"


# ---------------------------------------------------------------------------
# C4 — side effects: exactly one registry entry per formal, zero for draft
# ---------------------------------------------------------------------------


def test_c4_draft_has_zero_side_effects(registry_path):
    prepare_forecast(_zijin_document(), mode="draft")
    assert not registry_path.exists()
    # no stray files next to the registry directory
    siblings = list(registry_path.parent.glob("*")) if registry_path.parent.exists() else []
    assert siblings == []


def test_c4_formal_adds_exactly_one_entry(registry_path):
    before = _entries(registry_path)
    formal = prepare_forecast(_zijin_document())
    after = _entries(registry_path)
    assert len(after) == len(before) + 1
    newest = after[-1]
    assert newest["result_sha256"] == formal["result_sha256"]
    assert newest["validation_status"] == "validated"


# ---------------------------------------------------------------------------
# C5 — rollback / observation window
# ---------------------------------------------------------------------------


def test_c5_rollback_restores_registry_and_replay_stays_identical(registry_path):
    document = _zijin_document()
    formal = prepare_forecast(copy.deepcopy(document))
    entries = _entries(registry_path)
    assert len(entries) == 1

    # rollback: remove the cutover entry (restores pre-cutover state)
    import publication_registry  # noqa: PLC0415

    publication_registry._clear_read_only(registry_path)
    rolled_back = [e for e in entries if e["result_sha256"] != formal["result_sha256"]]
    registry_path.write_text(
        "".join(json.dumps(e, ensure_ascii=False, sort_keys=True) + "\n" for e in rolled_back),
        encoding="utf-8",
    )
    assert _entries(registry_path) == []

    # observation window: same input still produces the identical result
    # (no drift after rollback), and a fresh formal re-registers cleanly.
    rerun = prepare_forecast(copy.deepcopy(document))
    assert rerun["result_sha256"] == formal["result_sha256"]
    after_rerun = _entries(registry_path)
    assert len(after_rerun) == 1
    assert after_rerun[0]["result_sha256"] == formal["result_sha256"]


def test_c5_observation_replay_bit_identical_over_cycles(registry_path):
    document = _zijin_document()
    hashes = set()
    for _ in range(3):
        result = prepare_forecast(copy.deepcopy(document), mode="formal")
        hashes.add(result["result_sha256"])
    assert len(hashes) == 1
    # every observation cycle registered an entry (auditable)
    assert len(_entries(registry_path)) == 3


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
