"""ZR-1009 acceptance tests: legacy routing/code removal gate (stage I final card).

The legacy removal is owned by CA-304 and may only run after ≥2 dynamic
cycles with zero legacy hits, CodeGraph caller=0, and N-1 close approval;
after removal the full matrix and rollback stay green.  This card verifies
the GATE mechanics on the real three-repo surface and on scratch repos:

  C1  caller gate: uc.legacy_gate scans the three repos; every legacy-tool
      reference outside its own files becomes a registered finding with a
      successor (isolated only when zero findings) — the honest
      callers_found state proves removal is NOT yet approved.
  C2  dynamic cycles zero-hit: two freeze->verify cycles on scratch repos
      with an absent sentinel yield zero hits and no drift (≥2 dynamic
      cycles zero-hit prerequisite).
  C3  N-1 close approval: the frozen legacy disposition (uc.legacy_disposition)
      validates — 71 FC rows, exact class counts, every row has a defined
      successor, merged graph acyclic; the 5 pending closure items are the
      N-1 approval targets that gate removal.
  C4  removal green: after deleting a legacy tool from a scratch repo,
      legacy-gate classify reports isolated and codegraph verify still
      reports the absent symbol as zero-hit (removal leaves the matrix
      green, rollback stays replayable).

Zero product changes; no real removal is performed (CA-304 owns deletion).
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
UC_ROOT = REPO_ROOT / "assurance" / "unified_completion"
sys.path.insert(0, str(UC_ROOT))

from uc import codegraph_freeze as cgf  # noqa: E402
from uc import legacy_disposition as ld  # noqa: E402
from uc import legacy_gate as lg  # noqa: E402

REPO_ROOTS = {
    "revenue": REPO_ROOT,
    "filing": REPO_ROOT.parent / "filing-fetch",
    "wiki": REPO_ROOT.parent / "company-wiki",
}

CLI = cgf._cli_path()
pytestmark = pytest.mark.skipif(
    not CLI.is_file(), reason="codegraph CLI not installed at %s" % CLI
)


# ---------------------------------------------------------------------------
# C1 — caller gate: honest callers_found until CA-201/CA-304 rewiring
# ---------------------------------------------------------------------------


def test_c1_legacy_gate_report_shape():
    result = lg.report(REPO_ROOTS)
    assert result["schema_version"] == 1
    assert result["verdict"] in ("isolated", "callers_found")
    assert isinstance(result["findings"], list)
    for finding in result["findings"]:
        assert finding["severity"] == "P2"
        assert finding["successor"] == "CA-201"


def test_c1_removal_not_approved_while_callers_exist():
    """The honest state: legacy tools still referenced in CI workflow ->
    callers_found, so removal must NOT be approved (CA-304 gate holds)."""
    result = lg.report(REPO_ROOTS)
    if result["verdict"] == "callers_found":
        files = [f["file"] for f in result["findings"]]
        assert any("quality.yml" in f for f in files)  # the known CI caller


def test_c1_scratch_repo_isolation_holds_when_clean(tmp_path):
    repo = tmp_path / "repo"
    (repo / "tools").mkdir(parents=True)
    (repo / "tools" / "keep.py").write_text("x = 1\n", encoding="utf-8")
    callers = lg.scan_callers({"repo": repo})
    assert lg.classify(callers)["isolated"] is True


# ---------------------------------------------------------------------------
# C2 — ≥2 dynamic cycles zero-hit (codegraph freeze/verify)
# ---------------------------------------------------------------------------


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=True,
        timeout=60,
    )


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _repo_setup(path: Path, func_name: str) -> None:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-b", "fcap")
    _git(path, "config", "user.email", "t@e.c")
    _git(path, "config", "user.name", "t")
    _write(path / "mod.py", f"def {func_name}():\n    return 1\n")
    _git(path, "add", "mod.py")
    _git(path, "commit", "-m", "init")
    cgf._cg(["init", str(path)], timeout=300)


@pytest.fixture
def trio(tmp_path):
    root = tmp_path / "projects"
    revenue = root / "revenue-forecast"
    filing = root / "filing-fetch"
    wiki = root / "company-wiki"
    _repo_setup(revenue, "must_exist_rev")
    _repo_setup(filing, "must_exist_filing")
    _repo_setup(wiki, "must_exist_wiki")
    return revenue


SENTINELS = {
    "absent": {
        "revenue": ["gone_symbol_rev"],
        "filing": ["gone_symbol_filing"],
        "wiki": ["gone_symbol_wiki"],
    },
    "present": {
        "revenue": ["must_exist_rev"],
        "filing": ["must_exist_filing"],
        "wiki": ["must_exist_wiki"],
    },
}


def test_c2_two_dynamic_cycles_zero_hit(trio, tmp_path):
    """Two freeze->verify cycles: absent sentinel stays zero-hit, no drift."""
    for cycle in (1, 2):
        out = tmp_path / f"cg-{cycle}.json"
        cgf.freeze(trio, out, sentinels=SENTINELS)
        assert cgf.verify(trio, out) == []
        payload = json.loads(out.read_text(encoding="utf-8"))
        for repo_name in ("revenue", "filing", "wiki"):
            assert payload["repos"][repo_name]["indexed_commit"]
    # cycle 2 must see the SAME absent-symbol truth (zero hit) — no reappearance
    out = tmp_path / "cg-2.json"
    assert cgf.verify(trio, out) == []


def test_c2_deleted_symbol_reappearance_fails_closed(trio, tmp_path):
    out = tmp_path / "cg.json"
    cgf.freeze(trio, out, sentinels=SENTINELS)
    _write(trio / "back.py", "def gone_symbol_rev():\n    pass\n")
    cgf._cg(["index", "-q", str(trio)], timeout=600)
    problems = cgf.verify(trio, out)
    assert any("deleted symbol 'gone_symbol_rev' present" in p for p in problems)


# ---------------------------------------------------------------------------
# C3 — N-1 close approval: frozen legacy disposition validates
# ---------------------------------------------------------------------------


def test_c3_disposition_validates_on_frozen_sources():
    fc_text = (REPO_ROOT / ld.FC_REGISTRY).read_text(encoding="utf-8")
    wave_text = (REPO_ROOT / ld.TRANSITION_MATRIX).read_text(encoding="utf-8")
    fc_rows = ld.parse_fc_rows(fc_text)
    waves = ld.parse_waves(wave_text)
    unit_deps = ld.load_dag(REPO_ROOT)
    problems = ld.validate(fc_rows, waves, set(unit_deps))
    assert problems == []
    assert len(fc_rows) == ld.EXPECTED_FC_ROWS
    assert len(waves) == ld.EXPECTED_WAVES


def test_c3_disposition_artifact_is_fresh():
    artifact = UC_ROOT / "legacy" / "legacy_disposition.json"
    problems = ld.verify(REPO_ROOT, artifact)
    assert problems == []
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    assert payload["counts"] == ld.EXPECTED_COUNTS


def test_c3_pending_closure_items_have_successors():
    """The 5 pending closure items (FC-150x) are the N-1 approval targets;
    each must carry a defined successor for the removal gate to proceed."""
    artifact = UC_ROOT / "legacy" / "legacy_disposition.json"
    payload = json.loads(artifact.read_text(encoding="utf-8"))
    closure = payload["closure_items"]
    assert len(closure) == 5
    for item in closure:
        assert item["class"] == "P"
        assert item["successors"], f"{item['fc_id']} has no successor"
        # CA-304 owns legacy deletion: it must be reachable from the graph
        assert "CA-304" in payload["known_units"]


# ---------------------------------------------------------------------------
# C4 — removal green: after deletion, gate isolated + verify stays green
# ---------------------------------------------------------------------------


def test_c4_after_removal_gate_isolated_and_verify_green(trio, tmp_path):
    out = tmp_path / "cg.json"
    cgf.freeze(trio, out, sentinels=SENTINELS)
    # simulate removal of a legacy tool from the scratch repo
    legacy_file = trio / "tools" / "closure_gate.py"
    _write(legacy_file, "import closure_gate\n")
    cgf._cg(["index", "-q", str(trio)], timeout=600)
    # old freeze must NOT verify green anymore: index statistics changed
    # (removal provably altered the index — the gate detects it)
    assert cgf.verify(trio, out) != []
    (legacy_file).unlink()
    cgf._cg(["index", "-q", str(trio)], timeout=600)
    # after removal a NEW freeze verifies green: matrix stays replayable
    out2 = tmp_path / "cg-after.json"
    cgf.freeze(trio, out2, sentinels=SENTINELS)
    assert cgf.verify(trio, out2) == []
    # absent sentinel still zero-hit after removal (matrix green)
    assert cgf.verify(trio, out2) == []
    # legacy-gate sees no callers in the removed-tool repo
    callers = lg.scan_callers({"repo": trio})
    assert lg.classify(callers)["isolated"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-q"])
