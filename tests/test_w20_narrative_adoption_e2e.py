"""W20 end-to-end: the adoption observer against real CLI artifacts.

Real layer (never faked): ``tools/run_narrative_consumption_e2e.py`` running
the real consume adapter through a reader subprocess, ``scripts/
revenue_forecast.py`` producing real formal forecasts, ``scripts/
revenue_backtest.py`` creating a real snapshot, and this tool's CLI
(``tools/narrative_adoption_audit/cli.py``) as a real subprocess. Two driver
model families are covered: direct_revenue (scoped calibration fixture with
a narrative chain) and direct_growth (the biren e2e fixture).

Faked layer only: the CWP reader transport stub replays one synthetic public
wire (the DU11 pattern); every fixture source is explicitly synthetic and no
LLM, download, provider or ledger outside the owned temporary registry runs.
The in-process offline guard cannot reach subprocesses; every spawned entry
(consume tool, forecast/backtest CLIs, this CLI) is network-free by source
inspection, and the registry is pinned into the owned temporary tree.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import stat
import subprocess
import sys
import time
import urllib.request

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "tests"))

from fix_hashes import apply_hash_fixes  # noqa: E402
from test_du11_narrative_citation_wire import wire  # noqa: E402

FIXTURE_INPUT = ROOT / "tests/fixtures/scoped_calibration_support/valid_calibrated.json"
BIREN_INPUT = ROOT / "e2e/fixtures/biren_input.json"
SENTINEL = b"W20 NARRATIVE ADOPTION SENTINEL\n"
DRIVER_SLOT_PARAMETER = "0_base_2026"
UPSTREAM_PARAMETER = "reference_lower"

STUB = '''\
"""Local stand-in for the published CWP narrative transport CLI."""
import sys
from pathlib import Path

here = Path(__file__).resolve().parent      # .../cwp-stub/company_wiki/source_catalog
replay = here.parents[2] / "replay"
sys.stdin.buffer.read()
with (replay / "calls.log").open("a", encoding="utf-8") as log:
    log.write("read " + " ".join(sys.argv[1:]) + "\\n")
sys.stdout.buffer.write((replay / "bundle.json").read_bytes())
sys.stdout.buffer.flush()
sys.stderr.buffer.write((replay / "receipt.jsonl").read_bytes())
sys.stderr.buffer.flush()
'''


# ---------------------------------------------------------------------------
# Owned temporary tree: sentinel, existing entry, restore receipt
# ---------------------------------------------------------------------------

def snapshot(root: Path) -> dict[str, tuple[str, int]]:
    return {
        path.relative_to(root).as_posix(): (
            hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns
        )
        for path in sorted(root.rglob("*")) if path.is_file()
    }


def _unlink(path: Path) -> None:
    # The publication registry marks its file read-only after each append;
    # clearing the attribute is required before deleting it on Windows.
    for attempt in range(4):
        try:
            path.unlink()
            return
        except PermissionError:
            os.chmod(path, stat.S_IWRITE)
            if attempt == 3:
                raise
            time.sleep(0.1)


def _remove(root: Path, names) -> list[str]:
    removed = []
    for name in sorted(names, key=lambda item: item.count("/"), reverse=True):
        path = root / name
        if path.is_file():
            _unlink(path)
            removed.append(name)
    for path in sorted((item for item in root.rglob("*") if item.is_dir()),
                       key=lambda item: len(item.parts), reverse=True):
        if not any(path.iterdir()):
            removed.append(path.relative_to(root).as_posix() + "/")
            path.rmdir()
    return removed


@pytest.fixture
def owned(tmp_path):
    root = tmp_path / "w20-owned"
    root.mkdir()
    (root / "sentinel.bin").write_bytes(SENTINEL)
    (root / "out").mkdir()
    (root / "out" / "existing.json").write_text('{"existing": true}\n', encoding="utf-8")
    baseline = snapshot(root)
    yield root
    after = snapshot(root)
    for name, record in baseline.items():
        assert after[name] == record, f"pre-existing entry changed: {name}"
    created = sorted(set(after) - set(baseline))
    removed = _remove(root, created)
    assert snapshot(root) == baseline
    assert sorted(path.name for path in root.iterdir()) == ["out", "sentinel.bin"]
    restored = snapshot(root) == baseline
    for path in root.rglob("*"):
        if path.is_file():
            try:
                os.chmod(path, stat.S_IWRITE)
            except OSError:
                pass
    for attempt in range(4):
        try:
            shutil.rmtree(root)
            break
        except PermissionError:
            if attempt == 3:
                raise
            time.sleep(0.3)
    assert not root.exists()
    directory = os.environ.get("W20_PWF_RECEIPTS")
    test_name = os.environ.get("PYTEST_CURRENT_TEST", "")
    if directory and test_name:
        Path(directory).mkdir(parents=True, exist_ok=True)
        receipt = {
            "schema_version": "w20-e2e-restore-receipt/1",
            "test": test_name,
            "initial_files": sorted(baseline),
            "created": created,
            "removed": removed,
            "restored": restored,
            "root_removed": not root.exists(),
            "sentinel_sha256": hashlib.sha256(SENTINEL).hexdigest(),
        }
        name = hashlib.sha256(test_name.encode("utf-8")).hexdigest()[:16]
        target = Path(directory) / f"restore-{name}.json"
        target.write_text(json.dumps(receipt, ensure_ascii=False, indent=2)
                          + "\n", encoding="utf-8")


@pytest.fixture(autouse=True)
def offline_guard(monkeypatch):
    def refuse(*_args, **_kwargs):
        raise AssertionError("W20 E2E forbids network access")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    monkeypatch.setattr(socket, "create_connection", refuse)
    monkeypatch.setattr(urllib.request, "urlopen", refuse)


# ---------------------------------------------------------------------------
# subprocess helpers
# ---------------------------------------------------------------------------

def run_process(args, *, env_extra=None, timeout=300):
    env = dict(os.environ)
    env.update({
        "PYTHONDONTWRITEBYTECODE": "1",
        "PYTHONIOENCODING": "utf-8",
        "PYTHONUTF8": "1",
    })
    if env_extra:
        env.update(env_extra)
    result = subprocess.run(
        [sys.executable, "-B", "-X", "utf8", *[str(a) for a in args]],
        cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout, check=False, env=env,
    )
    return result


def run_forecast(input_path: Path, output: Path, registry: Path):
    result = run_process(
        [ROOT / "scripts/revenue_forecast.py", input_path, "--output", output],
        env_extra={"REVENUE_PUBLICATION_REGISTRY": str(registry)})
    assert result.returncode == 0, result.stderr[-3000:]
    return json.loads(output.read_text(encoding="utf-8"))


def run_audit(args):
    return run_process([ROOT / "tools/narrative_adoption_audit/cli.py", *args])


def prepare_wire(root: Path):
    """Write one synthetic public wire + the CWP reader stub that replays it."""
    request, body, receipt = wire("2")
    bundle = json.loads(body)
    assert bundle["source_ref"]["schema_version"] == "2.0"
    replay = root / "replay"
    replay.mkdir()
    (replay / "request.json").write_text(
        json.dumps(request, ensure_ascii=False), encoding="utf-8")
    (replay / "bundle.json").write_bytes(body)
    (replay / "receipt.jsonl").write_bytes(receipt)
    stub = root / "cwp-stub" / "company_wiki" / "source_catalog"
    stub.mkdir(parents=True)
    for package in (stub.parent, stub):
        (package / "__init__.py").write_text("", encoding="utf-8")
    (stub / "narrative_transport_cli.py").write_text(STUB, encoding="utf-8")
    (root / "catalog.json").write_text("{}", encoding="utf-8")
    return request, body, receipt


def link_input(root: Path, request: dict, body: bytes):
    """Adapt the synthetic-calibrated fixture to the wire parent, then bind."""
    bundle = json.loads(body)
    parent = bundle["source_ref"]
    spans = bundle["evidence_spans"]
    by_kind = {span["structured_value"]["unit_kind"]: span for span in spans}
    answer = next(s for s in spans
                  if s["structured_value"]["unit_kind"] == "transcript_speaker_block"
                  and s["raw_text"].startswith("[CEO]"))
    table_row = by_kind["table_row"]
    data = json.loads(FIXTURE_INPUT.read_text(encoding="utf-8"))
    data["as_of_date"] = request["as_of_date"]
    # Snapshot creation injects forecast_version into the input before
    # hashing, so the artifact and its snapshot must share the version up
    # front for the identity cross-check to bind.
    data["forecast_version"] = "w20-e2e"
    data["sources"][0]["capture"]["snapshot_sha256"] = parent["content_sha256"]
    apply_hash_fixes(data)
    base_input = root / "input.json"
    base_input.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")
    # table_row is support in two published views, so the binding must pick
    # one explicitly (the adapter refuses ambiguous support selections).
    groups = bundle["reading_context"]["groups"]
    table_group = next(g for g in groups
                       if table_row["span_id"] in g["evidence_ids"])
    bindings = [
        {"span_id": answer["span_id"], "claim_id": "w20_e2e_direct",
         "parameter_id": DRIVER_SLOT_PARAMETER, "support_type": "rationale_support"},
        {"span_id": table_row["span_id"], "claim_id": "w20_e2e_upstream",
         "parameter_id": UPSTREAM_PARAMETER, "support_type": "rationale_support",
         "citation_group_id": table_group["group_id"], "citation_view": 0},
    ]
    (root / "bindings.json").write_text(
        json.dumps(bindings, ensure_ascii=False), encoding="utf-8")
    return base_input, answer, table_row


def find_item(report, kind, item_id):
    matches = [i for i in report["items"] if i["kind"] == kind and i["id"] == item_id]
    assert len(matches) == 1, (kind, item_id, len(matches))
    return matches[0]


def codes(report):
    return [d["code"] for d in report["diagnostics"]]


# ---------------------------------------------------------------------------
# E2E-1: direct_revenue — real consume tool, real forecast CLI, real audit CLI
# ---------------------------------------------------------------------------

def test_direct_revenue_full_narrative_chain(owned):
    registry = owned / "registry"
    registry.mkdir()
    request, body, receipt = prepare_wire(owned)
    base_input, answer, table_row = link_input(owned, request, body)
    fixture_bytes = FIXTURE_INPUT.read_bytes()

    result = run_process([
        ROOT / "tools/run_narrative_consumption_e2e.py",
        "--input", owned / "input.json",
        "--narrative-request", owned / "replay/request.json",
        "--bindings", owned / "bindings.json",
        "--source-id", "filing",
        "--catalog-config", owned / "catalog.json",
        "--output-root", owned / "link",
    ], env_extra={"PYTHONPATH": str(owned / "cwp-stub")})
    assert result.returncode == 0, result.stderr[-3000:]
    linked_input = owned / "link/linked-input.json"
    consumption = owned / "link/consumption.json"
    assert json.loads(consumption.read_text(encoding="utf-8"))["status"] == "consumed"

    baseline = run_forecast(base_input, owned / "out/baseline.json", registry)
    linked = run_forecast(linked_input, owned / "out/linked.json", registry)
    # Narrative linking declares evidence; it must not move any number.
    assert linked["consolidated_forecast"] == baseline["consolidated_forecast"]
    assert linked["segments"] == baseline["segments"]
    assert linked["result_sha256"] != baseline["result_sha256"]
    claim_ids = {c["claim_id"] for c in linked["evidence_claims"]}
    assert {"w20_e2e_direct", "w20_e2e_upstream"} <= claim_ids

    audit_args = [
        "--forecast", owned / "out/linked.json",
        "--input", linked_input,
        "--consumption", consumption,
        "--narrative", owned / "replay/request.json", owned / "replay/bundle.json",
        owned / "replay/receipt.jsonl",
    ]
    report_path = owned / "out/report.json"
    started = time.perf_counter()
    result = run_audit([*audit_args, "--output", report_path])
    assert result.returncode == 0, result.stderr[-3000:]
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert report["schema_version"] == "rf-narrative-adoption-report/1"
    assert report["cross_checks"]["input_match"] is True

    direct = find_item(report, "span", answer["span_id"])
    assert direct["status"] == "used"
    slot = [c for c in direct["cited_by"]
            if c["node_type"] == "segment_scenario_driver"]
    assert slot and slot[0]["ids"]["parameter_id"] == DRIVER_SLOT_PARAMETER
    assert "used_via_segment_driver_slot" in direct["reasons"]

    upstream = find_item(report, "span", table_row["span_id"])
    assert upstream["status"] == "used"
    assert "used_via_derived_parameter" in upstream["reasons"]

    claim = find_item(report, "claim", "w20_e2e_direct")
    assert claim["status"] == "used"
    source = find_item(report, "source", "filing")
    assert source["status"] == "used"
    wire_spans = json.loads(body)["evidence_spans"]
    header = next(s for s in wire_spans
                  if s["structured_value"]["unit_kind"] == "table_header")
    question = next(s for s in wire_spans
                    if s["raw_text"].startswith("[Analyst]"))
    assert find_item(report, "span", header["span_id"])["status"] == \
        "not_used_when_provable"
    assert find_item(report, "span", question["span_id"])["status"] == \
        "not_observed"
    summary = find_item(report, "summary_claim", "claim-replay-000")
    assert summary["status"] == "used"  # its span (answer) is bound

    # Byte-stable rerun and untouched inputs.
    second = owned / "out/report-2.json"
    assert run_audit([*audit_args, "--output", second]).returncode == 0
    assert second.read_bytes() == report_path.read_bytes()
    assert FIXTURE_INPUT.read_bytes() == fixture_bytes
    assert consumption.read_text(encoding="utf-8")
    assert time.perf_counter() - started < 120

    # A real snapshot binds and cross-checks.
    snapshot_path = owned / "out/snapshot.json"
    created = run_process([
        ROOT / "scripts/revenue_backtest.py", "create", linked_input,
        "--version", "w20-e2e", "--output", snapshot_path,
    ], env_extra={"REVENUE_PUBLICATION_REGISTRY": str(registry)})
    assert created.returncode == 0, created.stderr[-3000:]
    cross = owned / "out/snapshot-report.json"
    result = run_audit([
        "--forecast", owned / "out/linked.json", "--snapshot", snapshot_path,
        "--output", cross,
    ])
    assert result.returncode == 0, result.stderr[-3000:]
    checked = json.loads(cross.read_text(encoding="utf-8"))
    assert checked["cross_checks"]["snapshot_match"] is True

    # Refusing to overwrite is a real process exit code.
    assert run_audit([*audit_args, "--output", owned / "out/existing.json"]
                     ).returncode == 2
    assert (owned / "out/existing.json").read_text(encoding="utf-8") == \
        '{"existing": true}\n'


# ---------------------------------------------------------------------------
# E2E-2: direct_growth — second driver model family, native-only observation
# ---------------------------------------------------------------------------

def unwired_variant(root: Path) -> Path:
    data = json.loads(BIREN_INPUT.read_text(encoding="utf-8"))
    capture = data["sources"][0]["capture"]
    data["parameters"].append({
        "parameter_id": "w20_unused_ratio", "kind": "analyst_assumption",
        "value": 1.05, "unit": "ratio", "period": "FY2026",
        "definition": "W20 synthetic unwired assumption", "dimension": "ratio",
        "time_basis": "annual", "source_ids": [data["sources"][0]["source_id"]],
        "claim_ids": ["w20_unused_claim"], "scenario": "none",
        "rationale": "synthetic: attached but never wired into any model",
    })
    data["evidence_claims"].append({
        "claim_id": "w20_unused_claim",
        "source_id": data["sources"][0]["source_id"],
        "target_type": "parameter", "target_id": "w20_unused_ratio",
        "support_type": "rationale_support",
        "locator": "loc:v1/synthetic/w20",
        "excerpt": "W20 synthetic rationale excerpt for an unwired parameter",
        "content_sha256": capture["snapshot_sha256"],
        "capture_receipt_sha256": capture["receipt_sha256"],
        "verification_status": "opened_and_checked",
        "verified_by": "w20-e2e", "verified_date": data["as_of_date"],
    })
    apply_hash_fixes(data)
    path = root / "biren-variant.json"
    path.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def test_direct_growth_native_observation(owned):
    registry = owned / "registry"
    registry.mkdir()
    fixture_bytes = BIREN_INPUT.read_bytes()
    forecast = run_forecast(BIREN_INPUT, owned / "out/biren.json", registry)
    years = {str(year) for year in forecast["forecast_years"]}
    result = run_audit([
        "--forecast", owned / "out/biren.json",
        "--output", owned / "out/biren-report.json",
    ])
    assert result.returncode == 0, result.stderr[-3000:]
    report = json.loads((owned / "out/biren-report.json").read_text(encoding="utf-8"))
    assert report["counts"]["items"] > 0
    assert report["node_index"]["wired_parameter_ids"]
    used = [i for i in report["items"] if i["status"] == "used"]
    assert used, "the biren artifact must show adopted claims"
    slot = [c for i in used for c in i["cited_by"]
            if c["node_type"] == "segment_scenario_driver"]
    assert slot and {c["ids"]["year"] for c in slot} <= years

    variant = unwired_variant(owned)
    variant_forecast = run_forecast(variant, owned / "out/variant.json", registry)
    assert variant_forecast["consolidated_forecast"] == \
        forecast["consolidated_forecast"], "an unwired parameter moves nothing"
    result = run_audit([
        "--forecast", owned / "out/variant.json",
        "--output", owned / "out/variant-report.json",
    ])
    assert result.returncode == 0, result.stderr[-3000:]
    variant_report = json.loads(
        (owned / "out/variant-report.json").read_text(encoding="utf-8"))
    unused = find_item(variant_report, "claim", "w20_unused_claim")
    assert unused["status"] == "not_used_when_provable"
    assert "parameter_not_wired_to_any_node" in unused["reasons"]
    assert BIREN_INPUT.read_bytes() == fixture_bytes  # fixture untouched
