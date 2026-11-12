"""Whole-card MB-RF closure evidence.

Covers the boundaries the B2 slice did not: retired canary distribution,
report/core dependency direction, historical publication profiles, owner
state without a database, and a canonical install into a temporary root.
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

CANARY = "scripts/processed_artifact_canary.py"


def _installable() -> set[str]:
    from installation_manifest import installable_files

    return {path.relative_to(ROOT).as_posix() for path in installable_files(ROOT)}


def _parent_map(tree: ast.AST) -> dict[ast.AST, ast.AST]:
    parents: dict[ast.AST, ast.AST] = {}
    for parent in ast.walk(tree):
        for child in ast.iter_child_nodes(parent):
            parents[child] = parent
    return parents


def _function_ancestor(node: ast.AST, parents: dict[ast.AST, ast.AST]) -> str | None:
    current = parents.get(node)
    while current is not None:
        if isinstance(current, (ast.FunctionDef, ast.AsyncFunctionDef)):
            return current.name
        current = parents.get(current)
    return None


def test_canary_is_retired_from_distribution_but_retained_as_history():
    installable = _installable()
    assert CANARY not in installable
    assert (ROOT / CANARY).is_file(), "historical review material must stay in the repository"
    from installation_manifest import manifest

    assert CANARY not in manifest(ROOT)


def test_no_runtime_module_references_the_retired_canary():
    candidates = [*SCRIPTS.rglob("*.py"), *(ROOT / "agents").rglob("*"),
                  *(ROOT / "config").rglob("*"), ROOT / "SKILL.md",
                  *(ROOT / "references").glob("*.md")]
    offenders: list[str] = []
    for path in candidates:
        # The manifest must name a retired file to exclude it; that is not a caller.
        if not path.is_file() or path.name in {"processed_artifact_canary.py",
                                               "installation_manifest.py"}:
            continue
        if path.suffix not in {".py", ".md", ".yaml", ".yml", ".json"}:
            continue
        if "processed_artifact_canary" in path.read_text(encoding="utf-8", errors="ignore"):
            offenders.append(path.relative_to(ROOT).as_posix())
    assert offenders == []


def test_report_consumes_leaf_modules_not_the_core_aggregate():
    tree = ast.parse((SCRIPTS / "revenue_report.py").read_text(encoding="utf-8"))
    core_imports = [node for node in ast.walk(tree)
                    if isinstance(node, ast.ImportFrom) and node.module == "revenue_core"]
    assert core_imports == []
    child = subprocess.run(
        [sys.executable, "-S", "-B", "-X", "utf8", "-c",
         "import sys; sys.path.insert(0, r'%s'); import revenue_report; "
         "print('core_loaded', 'revenue_core' in sys.modules)" % SCRIPTS],
        cwd=ROOT, capture_output=True, text=True, timeout=60)
    assert child.returncode == 0, child.stderr
    assert "core_loaded False" in child.stdout


def test_core_imports_report_only_through_its_runtime_callback():
    tree = ast.parse((SCRIPTS / "revenue_core.py").read_text(encoding="utf-8"))
    parents = _parent_map(tree)
    callbacks = [node for node in ast.walk(tree)
                 if isinstance(node, ast.ImportFrom) and node.module == "revenue_report"]
    assert callbacks, "core must still orchestrate the report validator"
    assert all(_function_ancestor(node, parents) for node in callbacks)
    assert not any(_function_ancestor(node, parents) is None for node in callbacks)


def test_core_reexports_the_moved_leaf_symbols_for_compatibility():
    import revenue_core
    from contracts.constants import ENGINE_VERSION, SKILL_VERSION
    from contracts.workflow_receipt import build_workflow_compliance_receipt

    assert revenue_core.ENGINE_VERSION == ENGINE_VERSION == SKILL_VERSION
    assert revenue_core.SKILL_VERSION == SKILL_VERSION
    assert revenue_core.build_workflow_compliance_receipt is build_workflow_compliance_receipt


@pytest.mark.parametrize("version", ["v1", "v2"])
def test_historical_publication_profile_paths_are_relative_and_versioned(version):
    from report_catalog_research_publication import publication_layout

    layout = publication_layout(version)
    for key in ("input", "forecast", "markdown", "snapshot", "closure", "review"):
        value = layout[key]
        assert isinstance(value, str) and value
        assert not value.startswith(("/", "\\"))
        assert ":" not in value and "\\" not in value
        assert "sqlite" not in value.lower() and "catalog.sqlite" not in value.lower()
    if version != "v1":
        assert layout["forecast"] == f"forecast/{version}/forecast.json"
        assert layout["closure"] == f"execution/publications/{version}/publication.json"


def test_historical_publication_owner_imports_no_cwp_or_database():
    source = (SCRIPTS / "report_catalog_research_publication.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    modules = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    modules |= {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                for alias in node.names}
    assert not any(name and ("sqlite" in name or "company_wiki" in name) for name in modules)
    from report_catalog import CatalogError
    from report_catalog_research_publication import publication_layout

    with pytest.raises(CatalogError):
        publication_layout("v0")


def test_owner_catalog_and_job_state_use_json_not_a_database(tmp_path):
    from report_catalog import ReportCatalog

    for name in ("report_catalog.py", "report_catalog_rf_job_import.py", "rf_job_facade.py"):
        tree = ast.parse((SCRIPTS / name).read_text(encoding="utf-8"))
        imports = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
        imports |= {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
                    for alias in node.names}
        assert "sqlite3" not in imports, name
    catalog = ReportCatalog(root=tmp_path, catalog_file=tmp_path / "catalog.jsonl")
    assert catalog.file.suffix == ".jsonl"
    assert not catalog.file.exists()


def test_installable_closure_excludes_repo_control_planes():
    installable = _installable()
    assert "SKILL.md" in installable
    assert "scripts/revenue_report.py" in installable
    assert "scripts/report_catalog.py" in installable
    assert "scripts/report_catalog_verified_compare_cli.py" in installable
    for prefix in ("tests/", "tools/", "assurance/", "audit_review/", ".github/"):
        assert not any(item.startswith(prefix) for item in installable), prefix
    assert CANARY not in installable


def test_canonical_installer_runs_in_a_temporary_empty_cwd(tmp_path):
    destination = tmp_path / "skills"
    command = [sys.executable, "-B", str(ROOT / "tools" / "sync_installations.py"),
               "--canonical", str(ROOT), "--destination", str(destination), "--apply", "--json"]
    applied = subprocess.run(command, cwd=tmp_path, capture_output=True, text=True, timeout=300)
    assert applied.returncode == 0, applied.stdout + applied.stderr
    install_root = destination / "revenue-forecast"
    assert (install_root / "SKILL.md").is_file()
    assert (install_root / "scripts" / "revenue_report.py").is_file()
    assert not (install_root / CANARY).exists()
    checked = subprocess.run(
        [sys.executable, "-B", str(ROOT / "tools" / "sync_installations.py"),
         "--canonical", str(ROOT), "--destination", str(destination), "--json"],
        cwd=tmp_path, capture_output=True, text=True, timeout=300)
    assert checked.returncode == 0, checked.stdout + checked.stderr


def _source_fixtures() -> tuple[dict, dict, str]:
    ref = json.loads((ROOT / "tests/fixtures/cwp_source_ref_v2.json").read_text(encoding="utf-8"))
    receipt = json.loads(
        (ROOT / "tests/fixtures/cwp_verified_open_receipt_normalized.json").read_text(
            encoding="utf-8"))
    receipt["policy_sha256"] = "a" * 64
    receipt["source_read_policy_sha256"] = "b" * 64
    receipt["read_at"] = "2026-02-21T12:00:00+00:00"
    body = "正文🙂 Revenue increased. EXPORT-V2-RAW-BYTES-SENTINEL End"
    assert hashlib.sha256(body.encode("utf-8")).hexdigest() == ref["content_sha256"]
    return ref, receipt, body


def _candidate(ref: dict, manifest: dict) -> dict:
    return {
        "capture_ready": True, "source_ref": ref, "document_id": ref["document_id"],
        "source_id": ref["source_id"], "snapshot_sha256": ref["content_sha256"],
        "byte_size": ref["byte_size"], "mime_type": ref["mime_type"],
        "title": manifest["title"], "document_kind": manifest["document_kind"],
        "fiscal_year": manifest["fiscal_year"], "fiscal_period": manifest["fiscal_period"],
        "published_date": manifest["published_date"], "https_url": manifest["source_url"],
        "retrieved_at": manifest["retrieved_at"], "provider": manifest["provider"],
        "provider_document_id": manifest["provider_document_id"],
        "prompt_injection_status": "not_reviewed",
        "company_identity": {"market": manifest["market"],
                             "security_id": manifest["security_id"]},
    }


def _run_public_source_entry(tmp_path: Path, *, fail: bool) -> dict:
    ref, receipt, body = _source_fixtures()
    candidate = _candidate(ref, receipt["manifest"])
    neighbor = tmp_path / "neighbor-owner"
    neighbor.mkdir()
    sentinel = neighbor / "catalog.sqlite3"
    sentinel.write_bytes(b"private upstream database must not be read")
    before = hashlib.sha256(sentinel.read_bytes()).hexdigest()

    reader = tmp_path / "opaque_public_reader.py"
    if fail:
        reader.write_text("import sys\nsys.stderr.write('public reader refused\\n')\nsys.exit(2)\n",
                          encoding="utf-8")
    else:
        reader.write_text(
            "import json, sys\n"
            f"sys.stdout.buffer.write({body!r}.encode('utf-8'))\n"
            f"sys.stderr.write(json.dumps({receipt!r}) + '\\n')\n",
            encoding="utf-8")
    launcher = tmp_path / "public_source_entry.py"
    launcher.write_text(
        "import json, sys\n"
        f"sys.path.insert(0, {str(SCRIPTS)!r})\n"
        "from pathlib import Path\n"
        "import source_preparation as prep\n"
        f"candidate = json.loads({json.dumps(candidate)!r})\n"
        "try:\n"
        "    result = prep.prepare_registered_source_result(\n"
        f"        candidate, as_of_date='2026-07-18', company_wiki_catalog_config=Path({str(tmp_path / 'absent.handle')!r}),\n"
        f"        source_reader_command=(sys.executable, {str(reader)!r}))\n"
        "    print(json.dumps({'ok': True, 'source_ref': result['source']['company_wiki_trace']['source_ref'],\n"
        "                      'cwp': 'company_wiki' in sys.modules, 'ff': 'filing_fetch' in sys.modules}))\n"
        "except Exception as exc:\n"
        "    print(json.dumps({'ok': False, 'type': type(exc).__name__, 'error': str(exc),\n"
        "                      'cwp': 'company_wiki' in sys.modules, 'ff': 'filing_fetch' in sys.modules}))\n",
        encoding="utf-8")
    child = subprocess.run([sys.executable, "-S", "-B", "-X", "utf8", str(launcher)],
                           cwd=tmp_path, capture_output=True, text=True, timeout=120)
    assert child.returncode == 0, child.stderr
    payload = json.loads(child.stdout.strip().splitlines()[-1])
    assert payload["cwp"] is False and payload["ff"] is False
    after = hashlib.sha256(sentinel.read_bytes()).hexdigest()
    assert after == before, "the public entry must not scan or open the neighbouring database"
    return payload


def test_public_source_entry_reads_without_cwp_or_ff_packages(tmp_path):
    payload = _run_public_source_entry(tmp_path, fail=False)
    assert payload["ok"] is True
    assert payload["source_ref"]["source_id"] == _source_fixtures()[0]["source_id"]


def test_public_source_entry_fails_closed_without_neighbour_fallback(tmp_path):
    payload = _run_public_source_entry(tmp_path, fail=True)
    assert payload["ok"] is False
    assert payload["type"] in {"SourceVersionTransportError", "FilingSourcePreparationError",
                               "RuntimeError"}
