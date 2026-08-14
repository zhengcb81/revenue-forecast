"""ZR-003 golden corpus registry and verify guards.

The corpus registers the Zijin production counterexample samples as a
desensitized golden set: committed artifacts carry only anchors, relative
paths, hashes and expected entity/role/period metadata — never the sample
bytes and never absolute user paths.

Guards here pin:

- registry schema and frozen-triplet binding;
- desensitization invariants (only small JSON metadata files in the corpus
  dir; no committed artifact may contain a sample's bytes);
- the verify oracle on hermetic temp corpora: OK on intact samples,
  hash-mismatch on tampered bytes, problems on missing files, blocked-style
  problems on unresolved anchors, and leakage detection for a sample's bytes
  planted inside a scanned directory.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from conftest import REPO_ROOT

from uc.corpus import verify_golden_corpus

CORPUS_DIR = REPO_ROOT / "assurance" / "unified_completion" / "corpus"
CORPUS_PATH = CORPUS_DIR / "golden_corpus.json"

FROZEN_TRIPLET = {
    "revenue": "7716b876f503e980932d8873cdaec393ced3274b",
    "filing": "83c638e76e40890262746cdf02b6df495dcb4031",
    "wiki": "ef125ed63348c2b1cb41b2d7dd44f6d76b1ef875",
}

MANDATORY_ROLES = {
    "audited_filing",
    "broker_research",
    "company_release",
    "revenue_forecast_input",
    "revenue_forecast_result_draft",
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _corpus() -> dict:
    return json.loads(CORPUS_PATH.read_text(encoding="utf-8"))


def test_corpus_registry_exists_and_is_schema_valid() -> None:
    assert CORPUS_PATH.exists(), "golden_corpus.json is the mandatory ZR-003 artifact"
    data = _corpus()
    assert data["schema_version"] == 1
    assert data["unit"] == "ZR-003"
    assert data["triplet"] == FROZEN_TRIPLET
    anchors = set(data["anchors"])
    assert anchors, "anchors must be defined"
    samples = data["samples"]
    assert len(samples) == 12, (
        "12 samples: 2 annual + 7 broker + strategy + input/result"
    )
    for sample in samples:
        assert sample["sample_id"], sample
        assert sample["anchor"] in anchors, sample["sample_id"]
        assert sample["role"] in MANDATORY_ROLES, sample["sample_id"]
        assert isinstance(sample["entities"], list), sample["sample_id"]
        assert len(sample["sha256"]) == 64, sample["sample_id"]
        assert int(sample["sha256"], 16) > 0, sample["sample_id"]
        assert sample["byte_size"] > 0, sample["sample_id"]
        assert "period" in sample, sample["sample_id"]
        rel = sample["rel_path"]
        assert rel == rel.strip() and not rel.startswith("/"), sample["sample_id"]
        assert not rel[1:2] == ":", sample["sample_id"]  # no absolute windows path


def test_corpus_covers_all_mandatory_sample_families() -> None:
    data = _corpus()
    roles = {sample["role"] for sample in data["samples"]}
    assert MANDATORY_ROLES <= roles
    broker = [s for s in data["samples"] if s["role"] == "broker_research"]
    assert len(broker) == 7
    multi = [s for s in broker if len(s["entities"]) > 1]
    assert multi, "the Changjiang multi-entity comparison must be registered"
    negative = [
        s for s in data["samples"] if s["sample_id"] == "zijin_wrong_strategy_html"
    ]
    assert negative and negative[0]["entities"] == [], "negative identity sample"


def test_corpus_dir_contains_only_small_metadata_files() -> None:
    for path in CORPUS_DIR.rglob("*"):
        assert path.is_file(), f"unexpected non-file in corpus dir: {path}"
        assert path.suffix == ".json", f"non-JSON in corpus dir: {path}"
        assert path.stat().st_size < 1_048_576, f"embedded content suspected: {path}"


def test_no_sample_bytes_leak_into_committed_artifacts() -> None:
    data = _corpus()
    sample_hashes = {sample["sha256"] for sample in data["samples"]}
    receipt_dir = REPO_ROOT / "assurance" / "unified_completion" / "receipts" / "ZR-003"
    for base in (CORPUS_DIR, receipt_dir):
        for path in base.rglob("*"):
            if not path.is_file():
                continue
            assert _sha256_file(path) not in sample_hashes, (
                f"sample bytes leaked into committed artifact: {path}"
            )


def _build_tmp_corpus(tmp_path: Path, content: bytes) -> tuple[Path, Path, str]:
    sample = tmp_path / "sample.pdf"
    sample.write_bytes(content)
    corpus_path = tmp_path / "corpus.json"
    payload = {
        "schema_version": 1,
        "unit": "ZR-003-fixture",
        "triplet": FROZEN_TRIPLET,
        "anchors": {"tmp": {"kind": "explicit", "path": str(tmp_path)}},
        "samples": [
            {
                "sample_id": "fixture_sample",
                "anchor": "tmp",
                "role": "broker_research",
                "entities": ["Fixture Co"],
                "period": None,
                "published_date": None,
                "rel_path": "sample.pdf",
                "sha256": hashlib.sha256(content).hexdigest(),
                "byte_size": len(content),
                "notes": "hermetic fixture",
            }
        ],
    }
    corpus_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return sample, corpus_path, payload["samples"][0]["sha256"]


def test_verify_accepts_intact_hermetic_corpus(tmp_path: Path) -> None:
    _, corpus_path, _ = _build_tmp_corpus(tmp_path, b"%PDF-1.4 hermetic fixture bytes")
    assert verify_golden_corpus(corpus_path, leak_scan_dirs=[]) == []


def test_verify_rejects_tampered_bytes(tmp_path: Path) -> None:
    sample, corpus_path, _ = _build_tmp_corpus(tmp_path, b"%PDF-1.4 original")
    sample.write_bytes(b"%PDF-1.4 tampered")
    problems = verify_golden_corpus(corpus_path, leak_scan_dirs=[])
    assert any("sha256 mismatch" in problem for problem in problems)


def test_verify_reports_missing_sample(tmp_path: Path) -> None:
    sample, corpus_path, _ = _build_tmp_corpus(tmp_path, b"%PDF-1.4 original")
    sample.unlink()
    problems = verify_golden_corpus(corpus_path, leak_scan_dirs=[])
    assert any("missing" in problem for problem in problems)


def test_verify_reports_unresolved_anchor(tmp_path: Path) -> None:
    _, corpus_path, _ = _build_tmp_corpus(tmp_path, b"%PDF-1.4 original")
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    data["anchors"]["tmp"] = {"kind": "env", "var": "ZR003_FIXTURE_UNSET_VAR"}
    corpus_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    problems = verify_golden_corpus(corpus_path, leak_scan_dirs=[])
    assert any("unresolved" in problem for problem in problems)


def test_verify_detects_sample_bytes_inside_scanned_dir(tmp_path: Path) -> None:
    sample, corpus_path, sample_sha = _build_tmp_corpus(
        tmp_path, b"%PDF-1.4 leak fixture"
    )
    planted = tmp_path / "planted_copy.bin"
    planted.write_bytes(sample.read_bytes())
    problems = verify_golden_corpus(corpus_path, leak_scan_dirs=[tmp_path])
    assert any(sample_sha in problem for problem in problems)


def test_verify_env_anchor_resolution(tmp_path: Path, monkeypatch) -> None:
    sample, corpus_path, _ = _build_tmp_corpus(tmp_path, b"%PDF-1.4 env fixture")
    data = json.loads(corpus_path.read_text(encoding="utf-8"))
    data["anchors"]["tmp"] = {"kind": "env", "var": "ZR003_FIXTURE_ROOT"}
    corpus_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    monkeypatch.setenv("ZR003_FIXTURE_ROOT", str(tmp_path))
    assert verify_golden_corpus(corpus_path, leak_scan_dirs=[]) == []
