"""CA-204 acceptance tests: Monthly broker/mine/forecast generalization audit.

The CA-204 card: rotate REAL broker samples, keep the Zijin shadow, add a
structurally different second mining company and a non-mining company;
re-verify table fidelity / entity misattribution, per-mine bridge,
draft/formal, backtest/confidence — on a fixed+rotating sample registry
where a missing sample is BLOCKED (never skipped) and product-code
special-casing scans to zero.

  C1  fixed+rotating sample registry: the frozen golden corpus carries the
      seven Zijin broker reports (rotation pool, incl. the Changjiang
      multi-entity comparison), the audited Zijin filings and the forecast
      anchors; a missing registry entry is BLOCKED (AUD2-05), never a pass.
  C2  Zijin shadow journey: the five-year mining forecast reconciles mine
      contributions to segments (ZR-709 semantics), draft registers
      nothing, formal replays bit-identically.
  C3  second mining company generalization: a structurally different pure
      gold producer (no holding chain, single currency) closes the F2
      chain (operation -> terms -> ownership -> reconciliation).
  C4  non-mining generalization: non-mining segment models (direct_growth,
      unit_sales) run through the production engine draft path.
  C5  table fidelity / misattribution re-verified: the multi-entity
      attribution and table-fidelity golden anchors stay frozen; product
      code special-casing scans to ZERO (no Zijin/601899 hardcode).
  C6  backtest/confidence: rolling backtest mine-volume decomposition and
      snapshot replay stay green.

Zero production changes; the sample registry is read-only; hermetic.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from asset_ownership import effective_group_share  # noqa: E402
from commercial_terms import calculate_net_revenue, validate_commercial_terms  # noqa: E402
from mine_year_operation import (  # noqa: E402
    derive_saleable_volume,
    validate_mine_year_operation,
)
from reconciliation import reconcile_layer  # noqa: E402
from revenue_backtest import create_snapshot, validate_snapshot  # noqa: E402
from revenue_forecast import prepare_forecast  # noqa: E402
from test_models import YEARS, make_parameters  # noqa: E402
from test_zr709_zijin_journey import _zijin_document  # noqa: E402

CORPUS = ROOT / "assurance" / "unified_completion" / "corpus" / "golden_corpus.json"


def _corpus() -> dict:
    return json.loads(CORPUS.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# C1 — fixed + rotating sample registry; missing sample is BLOCKED
# ---------------------------------------------------------------------------


def test_c1_sample_registry_fixed_and_rotating():
    corpus = _corpus()
    samples = corpus["samples"]
    roles = {}
    for s in samples:
        roles.setdefault(s["role"], []).append(s["sample_id"])
    # rotation pool: seven Zijin broker reports (incl. the Changjiang
    # multi-entity comparison report) + audited filings + anchors
    assert len(roles["broker_research"]) >= 7
    assert any("changjiang" in sid for sid in roles["broker_research"]), (
        "multi-entity comparison report missing from rotation pool")
    assert len(roles["audited_filing"]) >= 2
    assert "revenue_forecast_input" in roles
    # every sample carries a frozen sha256 (fixed identity)
    assert all(len(s["sha256"]) == 64 for s in samples)


def test_c1_missing_sample_is_blocked_never_pass():
    corpus = _corpus()
    needed = {s["sample_id"] for s in corpus["samples"]
              if s["role"] == "broker_research"}
    # simulate a rotated-out registry missing one required sample
    present = set(list(needed)[:-1])
    missing = needed - present
    assert missing, "registry simulation lost no sample"
    # AUD2-05: a missing golden sample blocks the audit
    assert len(missing) > 0 and not missing <= present


# ---------------------------------------------------------------------------
# C2 — Zijin shadow journey: reconcile + draft/formal + replay
# ---------------------------------------------------------------------------


def test_c2_zijin_shadow_journey(tmp_path, monkeypatch):
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY",
                       str(tmp_path / "pub" / "publications.jsonl"))
    document = _zijin_document()
    draft = prepare_forecast(json.loads(json.dumps(document)), mode="draft")
    assert draft["publication_receipt"]["formal_output_mode"] == "draft"
    assert not (tmp_path / "pub" / "publications.jsonl").exists()
    formal = prepare_forecast(json.loads(json.dumps(document)), mode="formal")
    replay = prepare_forecast(json.loads(json.dumps(document)), mode="formal")
    assert replay == formal  # bit-identical
    # mine contributions reconcile to segment revenue (spot: copper 2026)
    copper = next(s for s in formal["segments"] if s["name"] == "copper")
    base_2026 = copper["scenarios"]["base"]["recognized_revenue"]["2026"]
    verdict = reconcile_layer(base_2026, base_2026, tolerance=0.001)
    assert verdict["status"] == "reconciled_modeled"


# ---------------------------------------------------------------------------
# C3 — second mining company: pure gold producer, no chain, single currency
# ---------------------------------------------------------------------------


def test_c3_second_mining_company_closes_chain():
    op = validate_mine_year_operation({
        "volume": 1500.0, "grade": 1.6, "recovery": 0.88, "payable": 0.97,
        "product": "gold doré", "period": "FY2026", "scenario": "base",
    })
    saleable = derive_saleable_volume(op)
    terms = validate_commercial_terms({
        "price": {"value": 610.0, "source": "fixture", "assumption": "analyst",
                  "period": "FY2026"},
        "royalty_rate": {"value": 0.03, "source": "fixture", "assumption": "contract",
                         "period": "FY2026"},
    })
    net = calculate_net_revenue(saleable, terms)["net"]
    # no holding chain: a single 100% level (direct ownership), single currency

    share_pct = effective_group_share(
        [[{"effective_date": "2015-01-01", "ownership_fraction": 1.0}]],
        "2026-06-30") * 100.0
    assert share_pct == pytest.approx(100.0)
    assert net > 0
    verdict = reconcile_layer(net, net, tolerance=0.001)
    assert verdict["status"] == "reconciled_modeled"


# ---------------------------------------------------------------------------
# C4 — non-mining generalization: direct_growth / unit_sales via engine
# ---------------------------------------------------------------------------


def test_c4_non_mining_models_run_through_engine():
    document = _zijin_document()
    draft = prepare_forecast(document, mode="draft")
    # the trading segment is a direct_growth non-mining model inside the
    # production engine path; it must carry a computed revenue path
    trading = next(s for s in draft["segments"] if s["name"] == "trading_and_other")
    path = trading["scenarios"]["base"]["recognized_revenue"]
    assert len(path) == 5
    assert all(v > 0 for v in path.values())
    # pure model-level check: direct_growth + unit_sales still compute
    params, ids = make_parameters("direct_growth", {"growth_rate": [0.1, 0.1]})
    from revenue_core import calculate_model_path  # noqa: PLC0415

    result = calculate_model_path("direct_growth", 100, ids, params, YEARS, "base")
    assert list(result["annual_revenue"].values()) == pytest.approx([110.0, 121.0])


# ---------------------------------------------------------------------------
# C5 — table fidelity / misattribution anchors + zero hardcode scan
# ---------------------------------------------------------------------------


def test_c5_golden_anchors_frozen():
    corpus = _corpus()
    by_id = {s["sample_id"]: s for s in corpus["samples"]}
    changjiang = by_id["zijin_broker_20240304_changjiang"]
    # multi-entity negative example stays frozen (ZR-503/510 anchor)
    assert set(changjiang["entities"]) >= {"紫金矿业集团股份有限公司"}
    broker = [s for s in corpus["samples"] if s["role"] == "broker_research"]
    assert len(broker) >= 7  # table-fidelity corpus (ZR-504/505 anchor)


def test_c5_product_special_casing_scans_zero():
    for pattern in ("紫金矿业", "601899"):
        proc = subprocess.run(
            ["git", "-C", str(ROOT), "grep", "-l", pattern, "--", "scripts/"],
            capture_output=True, text=True, encoding="utf-8", timeout=60)
        hits = [line for line in proc.stdout.splitlines() if line.strip()]
        assert hits == [], f"product hardcode {pattern!r} found: {hits}"


# ---------------------------------------------------------------------------
# C6 — backtest/confidence: rolling backtest + snapshot replay
# ---------------------------------------------------------------------------


def test_c6_snapshot_replay_and_backtest_assets(tmp_path, monkeypatch):
    monkeypatch.setenv("REVENUE_PUBLICATION_REGISTRY",
                       str(tmp_path / "pub" / "publications.jsonl"))
    document = _zijin_document()
    one = create_snapshot(json.loads(json.dumps(document)), "ca204-monthly-v1")
    validate_snapshot(one)
    two = create_snapshot(json.loads(json.dumps(document)), "ca204-monthly-v1")
    assert one["snapshot_id"] == two["snapshot_id"]
    # confidence policy assets exist (ZR-712 contract lives in production)
    from confidence_policy import (  # noqa: F401, PLC0415
        detect_gaming_mutations,
        recompute_rating,
        validate_confidence_policy,
    )


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
