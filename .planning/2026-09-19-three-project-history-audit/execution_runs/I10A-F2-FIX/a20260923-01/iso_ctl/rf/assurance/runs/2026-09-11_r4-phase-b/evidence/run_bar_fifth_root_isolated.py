"""R3 (B.AR residual): a legitimate FIFTH root joins by CONFIG ONLY, inside an
isolated catalog (design gate G8), and is read end-to-end query -> open -> consumer.

WHY ISOLATED, NOT PRODUCTION
----------------------------
Registering a root is an INSERT into the catalog's ``roots`` table performed by the
scanner (``scanner.py:847-854``); with the production config that means writing
``company-wiki/.source_catalog/catalog.sqlite3`` (49,677,344,768 bytes).  That write is
not authorised in this run, and the read-only manifest's own isolation note says
behavioural probes "must NOT use the production catalog: they require the isolated copy
in gate G8" (``2026-09-11_r4-phase-a/command-manifest-readonly.json:108``).  So this
script builds that copy: a throw-away project root under ``%TEMP%``, a config whose
EVERY root path is asserted to live inside that workdir, and a fresh empty catalog.
No production command is run, and the production catalog is snapshotted before and
after to prove it.

WHY THE FIFTH ROOT IS NOT ``future_lake``
-----------------------------------------
The production config already declares ``future_lake`` as the FOURTH root (ZR-409 /
EX-08 fixture; ``future_lake/README.md:1`` = "ZR-409 fourth-root fixture").  Re-using it
would re-run exactly the shape the earlier audit rejected
("future_lake 为空占位 + 合成测试不等于真实第四 root", filing-audit.md:49).  The fifth
root therefore takes future_lake's SHAPE (kind ``directory`` + the registered
``sidecar_filing_v1`` adapter + ``read_only`` + ``reusable_for_filing``) under a new id,
which is what "a legitimate fifth root joins by config only" actually means.

LEGS (each recorded with argv/call, exit code, output bytes and output digest)
-----------------------------------------------------------------------------
pre       production catalog {size, mtime_ns} + -wal/-shm, the three repos'
          HEAD + ``git status --porcelain``, and a sha256 tree fingerprint of
          ``company-wiki/src`` (the zero-product-change oracle)
build     isolated project root: four stand-in roots (empty) + the fifth root
          holding two real sidecar-paired filings
scan      ``scan --root-id r4_fifth_root`` -> the scanner WRITES the roots row
          (this is the registration under test)
query     ``query --limit 20`` -> the new root's documents are visible
open      ``SourceResolver.read_verified_bytes(handle)`` -> the bytes are read
          ONCE and verified against the indexed digest
consumer  ``SourceResolver.resolve(exact)`` -> REUSED_EXACT with the canonical path
          under the fifth root, plus ``query_filing_candidates(root_ids=...)``,
          the seam filing-fetch reuses -> no consumer code change
deny      a SECOND isolated catalog whose fifth root declares
          ``reusable_for_filing: false`` -> reuse is not granted
unknown   an unregistered ``adapter_id`` -> fails closed at config load
unreg     an unknown root id in ``--root-id`` and in ``root_ids`` -> refused/empty
post      the same snapshots: production must be identical in every recorded field
          and all three repos must stay clean

Usage::

    python run_bar_fifth_root_isolated.py [--workdir PATH] [--out PATH] [--keep]
    python run_bar_fifth_root_isolated.py --verify     # re-check a recorded run
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import traceback
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "b-ar-fifth-root-isolated.json"
WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
REPOS = {
    "company-wiki": WIKI,
    "revenue-forecast": Path(r"C:\Users\郑曾波\Projects\revenue-forecast"),
    "filing-fetch": Path(r"C:\Users\郑曾波\Projects\filing-fetch"),
}
DEFAULT_PYTHON = Path(r"C:\Miniconda\python.exe")
PRODUCTION_DB = WIKI / ".source_catalog" / "catalog.sqlite3"
PRODUCTION_CONFIG = WIKI / "config" / "source_catalog.yaml"

FIFTH_ROOT_ID = "r4_fifth_root"
STAND_IN_ROOTS = ("company_raw", "dayu_portfolio", "dropbox_stock", "future_lake")
ADAPTER = "sidecar_filing_v1"
ENTITY = "R4BAR Acme"
SECURITY_ID = "R4BARACME"
MARKET = "US"
PROVIDER = "sec"

FIXTURES = (
    {
        "name": "2025-annual.pdf",
        "body": b"%PDF-1.4\n% r4-bar fifth-root fixture, FY2025 annual report\n",
        "fiscal_year": 2025,
        "period_end": "2025-12-31",
        "published_at": "2026-02-20",
        "provider_document_id": "r4bar-doc-2025",
        "source_url": "https://www.sec.gov/Archives/edgar/data/r4bar/2025-annual.htm",
    },
    {
        "name": "2024-annual.pdf",
        "body": b"%PDF-1.4\n% r4-bar fifth-root fixture, FY2024 annual report\n",
        "fiscal_year": 2024,
        "period_end": "2024-12-31",
        "published_at": "2025-02-21",
        "provider_document_id": "r4bar-doc-2024",
        "source_url": "https://www.sec.gov/Archives/edgar/data/r4bar/2024-annual.htm",
    },
)

CONFIG_TEMPLATE = """schema_version: "1.0"
catalog_dir: "${{PROJECT_ROOT}}/{catalog_dir}"
reusable_root_kinds: [company_raw, dayu_portfolio, directory]
roots:
  - root_id: company_raw
    kind: company_raw
    path: "${{PROJECT_ROOT}}/roots/company_raw"
    priority: 10
    privacy_class: public
  - root_id: dayu_portfolio
    kind: dayu_portfolio
    path: "${{PROJECT_ROOT}}/roots/dayu_portfolio"
    priority: 20
    privacy_class: public
  - root_id: dropbox_stock
    kind: directory
    path: "${{PROJECT_ROOT}}/roots/dropbox_stock"
    priority: 30
    privacy_class: public
  - root_id: future_lake
    kind: directory
    path: "${{PROJECT_ROOT}}/roots/future_lake"
    adapter_id: {adapter}
    read_only: true
    reusable_for_filing: true
    priority: 40
    privacy_class: public
  # R3: the FIFTH root.  New id, future_lake's shape, config only.
  - root_id: {fifth_id}
    kind: directory
    path: "${{PROJECT_ROOT}}/roots/fifth_root"
    adapter_id: {adapter}
    read_only: true
    reusable_for_filing: {reusable}
    priority: 50
    privacy_class: public
"""


# ---------------------------------------------------------------------------
# snapshots
# ---------------------------------------------------------------------------


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _stat_of(path: Path) -> dict:
    if not path.exists():
        return {"exists": False}
    info = path.stat()
    return {"exists": True, "size": info.st_size, "mtime_ns": info.st_mtime_ns}


def _catalog_snapshot() -> dict:
    catalog_dir = PRODUCTION_DB.parent
    return {
        name: _stat_of(catalog_dir / name)
        for name in ("catalog.sqlite3", "catalog.sqlite3-wal", "catalog.sqlite3-shm")
    }


def _repos_snapshot() -> dict:
    snapshot: dict[str, dict] = {}
    for name, path in REPOS.items():
        head = subprocess.run(
            ["git", "-C", str(path), "rev-parse", "HEAD"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        status = subprocess.run(
            ["git", "-C", str(path), "status", "--porcelain"],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
        )
        snapshot[name] = {
            "head": (head.stdout or "").strip(),
            "porcelain": (status.stdout or ""),
            "clean": (status.stdout or "").strip() == "",
        }
    return snapshot


def _tree_fingerprint(root: Path) -> dict:
    files: list[tuple[str, int, str]] = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        files.append((path.relative_to(root).as_posix(), path.stat().st_size,
                      _sha256_file(path)))
    digest = hashlib.sha256()
    for relative, size, file_digest in files:
        digest.update(f"{relative}\0{size}\0{file_digest}\n".encode())
    return {"file_count": len(files), "tree_sha256": digest.hexdigest()}


# ---------------------------------------------------------------------------
# isolated tree
# ---------------------------------------------------------------------------


def _sidecar(fixture: dict, *, omit_published_at: bool = False,
             break_hash: bool = False) -> dict:
    payload = {
        "schema_version": "1.0",
        "canonical_entity_id": "ent-r4bar-acme",
        "display_name": ENTITY,
        "market": MARKET,
        "security_id": SECURITY_ID,
        "document_kind": "annual_report",
        "fiscal_year": fixture["fiscal_year"],
        "period_end": fixture["period_end"],
        # The adapter maps `published_at` (not `filing_date`) into the document's
        # published_date/filing_date; without it the resolver refuses with
        # `matching_sources_have_unknown_published_date` (measured in run 2).
        "form_type": "10-K",
        "provider": PROVIDER,
        "provider_document_id": fixture["provider_document_id"],
        "source_url": fixture["source_url"],
        "content_sha256": _sha256_bytes(fixture["body"]),
        "language": "en",
    }
    if not omit_published_at:
        payload["published_at"] = fixture["published_at"]
    if break_hash:
        payload["content_sha256"] = _sha256_bytes(b"not the bytes on disk")
    return payload


def write_runtime_snapshot(work: Path, catalog_dir: str, config_text: str) -> dict:
    """Give the isolated catalog a v2 scan-shadow activation snapshot.

    No snapshot file = v1 (``scanner.py:1187-1198``), and v1 walks the directory: it
    indexed the ``.source.json`` sidecars as documents of their own and produced no
    adapter role.  A directory root with a registered adapter is meant to be scanned
    through that adapter, so the isolated catalog gets a snapshot built BY THE PRODUCT
    (``build_snapshot``, so the hash and the flag dependencies are the product's rules,
    not this script's).
    """
    from company_wiki.source_catalog.runtime_policy import build_snapshot

    target_dir = work / catalog_dir
    target_dir.mkdir(parents=True, exist_ok=True)
    snapshot = build_snapshot({
        "schema_version": "1.0",
        "flags": {
            "v2_scan_shadow": True,
            "v2_persist_assertions": False,
            "v2_resolve_shadow": False,
            "v2_resolve_active": False,
            "v2_bundle_active": False,
            "legacy_bridge_enabled": False,
        },
        "policy_hash": _sha256_bytes(config_text.encode("utf-8")),
        "current_epoch": "r4-bar-isolated",
        "active_cohorts": [],
        "updated_at": datetime.now(UTC).isoformat(),
    })
    path = target_dir / "runtime_policy.json"
    path.write_text(json.dumps(snapshot, ensure_ascii=False, sort_keys=True, indent=2) + "\n",
                    encoding="utf-8", newline="")
    return {"path": str(path), "snapshot_sha256": snapshot["snapshot_sha256"],
            "flags": snapshot["flags"]}


def build_isolated_tree(work: Path, *, fifth_id: str = FIFTH_ROOT_ID, adapter: str = ADAPTER,
                        reusable: str = "true", catalog_dir: str = ".source_catalog",
                        config_name: str = "source_catalog.yaml",
                        hibernate_snapshot: bool = False, omit_published_at: bool = False,
                        break_hash: bool = False) -> dict:
    """(Re)build the isolated project root; return its config and snapshot."""
    if work.exists():
        shutil.rmtree(work)
    (work / "config").mkdir(parents=True)
    for root_id in STAND_IN_ROOTS:
        (work / "roots" / root_id).mkdir(parents=True)
    (work / "roots" / "future_lake" / "README.md").write_text(
        "# future_lake stand-in (isolated copy)\n\nMirrors the production fourth-root\n"
        "fixture: an adapter fixture, read-only, reusable.  Never scanned here.\n",
        encoding="utf-8", newline="",
    )
    fifth = work / "roots" / "fifth_root" / "acme"
    fifth.mkdir(parents=True)
    for fixture in FIXTURES:
        primary = fifth / fixture["name"]
        primary.write_bytes(fixture["body"])
        sidecar = fifth / f"{fixture['name']}.source.json"
        sidecar.write_text(json.dumps(_sidecar(fixture, omit_published_at=omit_published_at,
                                               break_hash=break_hash),
                                      ensure_ascii=False, indent=2) + "\n",
                           encoding="utf-8", newline="")
    config_path = work / "config" / config_name
    config_text = CONFIG_TEMPLATE.format(catalog_dir=catalog_dir, adapter=adapter,
                                         fifth_id=fifth_id, reusable=reusable)
    config_path.write_text(config_text, encoding="utf-8", newline="")
    snapshot = None if hibernate_snapshot else write_runtime_snapshot(work, catalog_dir,
                                                                     config_text)
    return {"config_path": config_path, "runtime_snapshot": snapshot}


def _load_config(config_path: Path, project_root: Path):
    from company_wiki.source_catalog.config import load_catalog_config

    return load_catalog_config(config_path, project_root=project_root)


def guard_paths_are_isolated(work: Path, config_path: Path) -> dict:
    """A mechanical refusal: EVERY root path must live inside the workdir.

    Without this, a mistyped config could point the isolated run at a real root and hash
    (or, for the cloud-synced root, hydrate) the user's own files.  The check is on the
    LOADED config, not on the template text.
    """
    config = _load_config(config_path, work)
    offenders = []
    for root in config.roots:
        resolved = Path(root.path).resolve()
        if not resolved.is_relative_to(work.resolve()):
            offenders.append({"root_id": root.root_id, "path": str(resolved)})
    if offenders:
        raise SystemExit(f"refusing to run: root paths outside the isolated workdir: {offenders}")
    catalog_dir = Path(config.catalog_dir).resolve()
    if not catalog_dir.is_relative_to(work.resolve()):
        raise SystemExit(f"refusing to run: catalog_dir outside the workdir: {catalog_dir}")
    catalog_is_production = catalog_dir == PRODUCTION_DB.parent.resolve()
    if catalog_is_production:
        raise SystemExit("refusing to run: catalog_dir IS the production catalog dir")
    return {
        "root_paths": {root.root_id: str(Path(root.path).resolve()) for root in config.roots},
        "catalog_dir": str(catalog_dir),
        # Derived, not declared (F-R3-06): the same comparison that refuses the production
        # dir above is what the record reports.
        "catalog_is_production": catalog_is_production,
    }


# ---------------------------------------------------------------------------
# product entry points
# ---------------------------------------------------------------------------


def run_cli(python: Path, config_path: Path, argv: list[str], cwd: Path,
            timeout: int = 300) -> dict:
    proc = subprocess.run(
        [str(python), "-B", "-m", "company_wiki.source_catalog.cli",
         "--config", str(config_path), *argv],
        cwd=str(cwd), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout,
    )
    out = proc.stdout or ""
    return {
        "mode": "cli",
        "argv": argv,
        "exit_code": proc.returncode,
        "stdout_bytes": len(out.encode("utf-8")),
        "stdout_sha256": _sha256_bytes(out.encode("utf-8")),
        "stdout": out,
        "stdout_head": out[:1200],
        "stderr_tail": (proc.stderr or "")[-800:],
    }


def open_catalog(config_path: Path, work: Path):
    from company_wiki.source_catalog import SourceCatalog

    return SourceCatalog(_load_config(config_path, work))


def _read_only(db_path: Path) -> sqlite3.Connection:
    return sqlite3.connect(f"file:{db_path.as_posix()}?mode=ro", uri=True)


def _roots_rows(db_path: Path) -> list[dict]:
    connection = _read_only(db_path)
    try:
        connection.row_factory = sqlite3.Row
        rows = [dict(row) for row in connection.execute(
            "SELECT root_id,path,kind,priority,last_scan_run,last_scanned_at FROM roots "
            "ORDER BY priority")]
    finally:
        connection.close()
    return rows


def _catalog_rows(db_path: Path) -> dict:
    connection = _read_only(db_path)
    try:
        connection.row_factory = sqlite3.Row
        documents = [dict(row) for row in connection.execute(
            "SELECT document_id,title,document_kind,source_status,published_date,"
            "metadata_json FROM documents ORDER BY title")]
        locations = [dict(row) for row in connection.execute(
            "SELECT location_id,root_id,relative_path,absolute_path,role,location_status,"
            "observed_size FROM locations ORDER BY relative_path")]
        entities = [dict(row) for row in connection.execute(
            "SELECT entity_id,name,entity_kind FROM entities ORDER BY name")]
        links = [dict(row) for row in connection.execute(
            "SELECT document_id,entity_id,confidence,method FROM document_entities")]
    finally:
        connection.close()
    return {"documents": documents, "locations": locations, "entities": entities,
            "document_entities": links}


def _document_ids(stdout: str) -> list[str]:
    import re

    seen: list[str] = []
    for match in re.finditer(r'"document_id"\s*:\s*"([^"]+)"', stdout):
        if match.group(1) not in seen:
            seen.append(match.group(1))
    return seen


def resolve_exact(catalog, *, entity: str, fiscal_year: int, as_of_date: str,
                  provider_document_id: str) -> dict:
    from company_wiki.source_catalog import SourceRequest, SourceResolver

    result = SourceResolver(catalog).resolve(SourceRequest(
        entity=entity,
        document_kind="annual_report",
        fiscal_year=fiscal_year,
        market=MARKET,
        security_id=SECURITY_ID,
        provider=PROVIDER,
        provider_document_id=provider_document_id,
        as_of_date=as_of_date,
        mode="exact",
    ))
    return {
        "status": str(result.status.value if hasattr(result.status, "value") else result.status),
        "reason": result.reason,
        "download_required": result.download_required,
        "download_allowed": result.download_allowed,
        "match_count": len(result.matches),
        "canonical_paths": [match.canonical_path for match in result.matches],
        "content_sha256": [match.content_sha256 for match in result.matches],
        "capture_ready": [match.capture_ready for match in result.matches],
        "missing_capture_fields": [list(match.missing_capture_fields)
                                   for match in result.matches],
        "trace_tail": [str(item) for item in (result.debug_trace or [])][-6:],
        "handles": [match.to_dict() for match in result.matches],
    }


def read_verified(catalog, handle_dict: dict) -> dict:
    """`open`: hand the resolver's handle back and ask for verified bytes."""
    from company_wiki.source_catalog import SourceResolver
    from company_wiki.source_catalog.resolver import SourceHandle

    handle = SourceHandle(**handle_dict)
    result = SourceResolver(catalog).read_verified_bytes(handle)
    data = result.data
    return {
        "ok": result.ok,
        "status": result.status,
        "reason": result.reason,
        "detail": result.detail,
        "byte_size": result.byte_size,
        "content_sha256": result.content_sha256,
        "read_sha256_of_returned_bytes": _sha256_bytes(data) if data else None,
        "bytes_source": result.bytes_source,
        "read_at": result.read_at,
    }


def filing_candidates(catalog, *, root_ids: tuple[str, ...], limit: int = 20) -> dict:
    rows = catalog.query_filing_candidates(
        document_kind="annual_report",
        source_statuses=("active",),
        root_ids=root_ids,
        limit=limit,
    )
    return {
        "count": len(rows),
        "document_ids": [row.get("document_id") for row in rows],
        "titles": [row.get("title") for row in rows],
    }


def scan_status(db_path: Path) -> dict:
    connection = _read_only(db_path)
    try:
        connection.row_factory = sqlite3.Row
        counts = {}
        for table in ("roots", "documents", "sources", "locations", "scan_runs"):
            counts[table] = connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
    finally:
        connection.close()
    return counts


# ---------------------------------------------------------------------------
# main
# ---------------------------------------------------------------------------


def observe(work: Path, tree: dict, python: Path) -> dict:
    """Scan the fifth root in an isolated tree and ask the consumer about every anchor."""
    config_path = tree["config_path"]
    # F-R3-04: the guard runs on EVERY isolated tree, mutation paths included - a
    # mechanical refusal that only covers the happy path is defence in the wrong place.
    guard = guard_paths_are_isolated(work, config_path)
    scan = run_cli(python, config_path, ["scan", "--root-id", FIFTH_ROOT_ID], work)
    db_path = work / ".source_catalog" / "catalog.sqlite3"
    if not db_path.exists():
        suffix = config_path.read_text(encoding="utf-8").split('"')[1].rsplit("/", 1)[-1]
        db_path = work / suffix / "catalog.sqlite3"
    observation: dict = {
        "isolation_guard": guard,
        "scan_exit_code": scan["exit_code"],
        "scan_stderr_tail": scan["stderr_tail"],
        "counts": scan_status(db_path) if db_path.exists() else {},
        "roots_rows": _roots_rows(db_path) if db_path.exists() else [],
    }
    try:
        catalog = open_catalog(config_path, work)
        rows = _catalog_rows(db_path)
        observation["documents"] = [
            {"title": row["title"], "document_kind": row["document_kind"],
             "source_status": row["source_status"]} for row in rows["documents"]]
        observation["location_roles"] = [
            {"relative_path": row["relative_path"], "role": row["role"],
             "location_status": row["location_status"]} for row in rows["locations"]]
        statuses = []
        for document in rows["documents"]:
            metadata = json.loads(document["metadata_json"] or "{}")
            acquisition = metadata.get("acquisition") or {}
            try:
                fiscal_year = int(acquisition.get("fiscal_year"))
            except (TypeError, ValueError):
                continue
            names = [entity["name"] for entity in rows["entities"]
                     if any(link["document_id"] == document["document_id"]
                            and link["entity_id"] == entity["entity_id"]
                            for link in rows["document_entities"])]
            if not names:
                continue
            resolution = resolve_exact(
                catalog, entity=names[0], fiscal_year=fiscal_year, as_of_date="2026-03-01",
                provider_document_id=acquisition.get("provider_document_id"))
            statuses.append({"fiscal_year": fiscal_year, "status": resolution["status"],
                             "reason": resolution["reason"],
                             "capture_ready": resolution["capture_ready"],
                             "trace_tail": resolution["trace_tail"]})
        observation["resolutions"] = statuses
    except Exception as error:  # noqa: BLE001 - recorded, not swallowed
        observation["error"] = f"{type(error).__name__}: {error}"
    return observation


def run_mutations(args) -> int:
    """Prove the recorded legs discriminate: each mutation must change an observation.

    R3 changes no product code, so the mutation proof belongs to the HARNESS: a leg that
    answers the same way with the mechanism broken would be decoration, not evidence.
    """
    work_root = Path(tempfile.gettempdir()) / "r4-bar-fifth-root-mutations"
    results: list[dict] = []

    # M1 — the isolation guard itself: a root path outside the workdir must be refused.
    def m1():
        work = work_root / "path_outside"
        tree = build_isolated_tree(work)
        text = tree["config_path"].read_text(encoding="utf-8")
        tree["config_path"].write_text(
            text.replace('path: "${PROJECT_ROOT}/roots/fifth_root"',
                         'path: "${PROJECT_ROOT}/../../roots/fifth_root"'),
            encoding="utf-8", newline="")
        try:
            guard_paths_are_isolated(work, tree["config_path"])
        except SystemExit as error:
            return {"killed": "outside the isolated workdir" in str(error),
                    "detail": str(error)[:200]}
        return {"killed": False, "detail": "guard did NOT refuse a path outside the workdir"}

    results.append({"id": "M1", "mutation": "fifth-root path moved outside the workdir",
                    "expectation": "the isolation guard refuses (SystemExit)",
                    "observed": m1()})
    results[-1]["killed"] = results[-1]["observed"]["killed"]
    print(f"M1: killed={results[-1]['killed']} {results[-1]['observed'].get('detail', '')}")

    # M2 — the deny leg must not be a constant: flipping the flag back to reusable has to
    # turn `missing` into `reused_exact`, otherwise the deny observation proves nothing.
    m2_work = work_root / "deny_flipped"
    m2 = observe(m2_work, build_isolated_tree(m2_work, reusable="true",
                                              catalog_dir=".source_catalog"), args.python)
    m2_statuses = [item["status"] for item in m2.get("resolutions", [])]
    results.append({"id": "M2", "mutation": "the denied root flipped to reusable_for_filing: true",
                    "expectation": "the consumer serves it (reused_exact), so the real deny "
                                   "leg's `missing` is discriminating",
                    "observed": {"statuses": m2_statuses},
                    "killed": all(status == "reused_exact" for status in m2_statuses)
                    and bool(m2_statuses),
                    "detail": f"statuses={m2_statuses}"})
    print(f"M2: killed={results[-1]['killed']} statuses={m2_statuses}")

    # M3 — a sidecar without published_at must stop the reuse answer.
    m3_work = work_root / "no_published_at"
    m3 = observe(m3_work, build_isolated_tree(m3_work, omit_published_at=True), args.python)
    m3_statuses = [item["status"] for item in m3.get("resolutions", [])]
    results.append({"id": "M3", "mutation": "sidecar without published_at",
                    "expectation": "the consumer no longer answers reused_exact",
                    "observed": {"statuses": m3_statuses,
                                 "reasons": [item["reason"] for item in m3.get("resolutions", [])]},
                    "killed": bool(m3_statuses) and all(status != "reused_exact"
                                                        for status in m3_statuses),
                    "detail": f"statuses={m3_statuses}"})
    print(f"M3: killed={results[-1]['killed']} statuses={m3_statuses}")

    # M4 — a sidecar whose declared hash does not match the bytes.
    m4_work = work_root / "hash_mismatch"
    m4 = observe(m4_work, build_isolated_tree(m4_work, break_hash=True), args.python)
    m4_statuses = [item["status"] for item in m4.get("resolutions", [])]
    results.append({"id": "M4", "mutation": "sidecar content_sha256 does not match the file",
                    "expectation": "the consumer no longer answers reused_exact (or the scan "
                                   "refuses the candidate)",
                    "observed": {"statuses": m4_statuses,
                                 "location_roles": m4.get("location_roles")},
                    "killed": (bool(m4_statuses) and all(status != "reused_exact"
                                                         for status in m4_statuses))
                    or m4.get("counts", {}).get("documents") in (0, None),
                    "detail": f"statuses={m4_statuses} "
                              f"documents={m4.get('counts', {}).get('documents')}"})
    print(f"M4: killed={results[-1]['killed']} statuses={m4_statuses}")

    # M5 — remove the activation snapshot: the scan falls back to the v1 directory walk,
    # which indexes the sidecars as documents of their own.
    m5_work = work_root / "no_snapshot"
    m5 = observe(m5_work, build_isolated_tree(m5_work, hibernate_snapshot=True), args.python)
    m5_titles = [item["title"] for item in m5.get("documents", [])]
    results.append({"id": "M5", "mutation": "no runtime_policy.json (v1 legacy walk)",
                    "expectation": "the adapter path is gone: the sidecars are indexed as "
                                   "documents, so the run's document set differs",
                    "observed": {"documents": m5.get("documents"),
                                 "counts": m5.get("counts")},
                    "killed": any(title.endswith(".source") for title in m5_titles),
                    "detail": f"titles={m5_titles}"})
    print(f"M5: killed={results[-1]['killed']} titles={m5_titles}")

    payload = {
        "artifact": "r3-fifth-root-mutations",
        "purpose": ("prove the R3 legs discriminate: each mutation must change an observation "
                    "(R3 changes no product code, so the harness is the unit under test)"),
        "ran_at_utc": datetime.now(UTC).isoformat(),
        "python": str(args.python),
        "work_root": str(work_root),
        "cases": results,
        "all_killed": all(entry["killed"] for entry in results),
        "prod_guard": {"production_catalog": _catalog_snapshot(),
                       "repos": _repos_snapshot()},
    }
    out = args.out.with_name("b-ar-fifth-root-mutations.json")
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                   encoding="utf-8", newline="")
    print(f"wrote {out}")
    print(f"mutants killed: {sum(1 for entry in results if entry['killed'])}/{len(results)}")
    if not args.keep:
        shutil.rmtree(work_root, ignore_errors=True)
    return 0 if payload["all_killed"] else 1


def _fresh_workdir() -> Path:
    return Path(tempfile.gettempdir()) / "r4-bar-fifth-root"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workdir", type=Path, default=_fresh_workdir())
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--keep", action="store_true", help="keep the isolated tree")
    parser.add_argument("--verify", action="store_true",
                        help="re-check a recorded run against the live filesystem")
    parser.add_argument("--mutations", action="store_true",
                        help="run the mutation matrix instead of the main run")
    args = parser.parse_args(argv)

    if args.mutations:
        return run_mutations(args)
    if args.verify:
        return verify(args.out)
    if not PRODUCTION_CONFIG.is_file():
        raise SystemExit(f"production config not found: {PRODUCTION_CONFIG}")

    work = args.workdir
    record: dict = {
        "artifact": "r3-fifth-root-isolated",
        "run_id": "2026-09-11_r4-phase-b",
        "purpose": ("R3: register a legitimate FIFTH root by config only in an isolated "
                    "catalog (gate G8) and read it end-to-end query -> open -> consumer"),
        "authorisation_basis": ("owner choices 2026-09-18, recorded in "
                               "owner-scope-decisions-2026-09-18.md: (A) isolated copy, and "
                               "the fifth root takes the future_lake placeholder SHAPE under "
                               "a new id (future_lake is already the FOURTH root). "
                               "Production catalog writes remain forbidden by the standing "
                               "objective"),
        "isolation": {"workdir": str(work), "inside_a_repo": None},
        "python": str(args.python),
        "legs": [],
        "fixtures": [],
    }
    record["isolation"]["inside_a_repo"] = [
        name for name, repo in REPOS.items() if work.resolve().is_relative_to(repo.resolve())
    ]

    print("pre-snapshot ...")
    record["pre"] = {
        "production_catalog": _catalog_snapshot(),
        "repos": _repos_snapshot(),
        "wiki_src": _tree_fingerprint(WIKI / "src"),
    }

    print(f"building isolated tree at {work} ...")
    tree = build_isolated_tree(work)
    config_path = tree["config_path"]
    record["config_path"] = str(config_path)
    record["config_text"] = config_path.read_text(encoding="utf-8")
    record["runtime_snapshot"] = tree["runtime_snapshot"]
    record["isolation"].update(guard_paths_are_isolated(work, config_path))
    if record["isolation"]["inside_a_repo"]:
        raise SystemExit(f"refusing to run: workdir inside a repo: {record['isolation']}")
    from company_wiki.source_catalog.scanner import v2_scan_shadow_from_snapshot

    record["scan_mode"] = {
        "v2_scan_shadow_from_snapshot": bool(
            v2_scan_shadow_from_snapshot(record["isolation"]["catalog_dir"])),
        "note": ("no snapshot = v1 legacy walk (scanner.py:1187-1198); the snapshot above "
                 "selects the adapter path this root is declared for"),
    }
    fixture_dir = work / "roots" / "fifth_root"
    record["fixtures"] = [
        {"relative_path": path.relative_to(fixture_dir).as_posix(),
         "byte_size": path.stat().st_size, "content_sha256": _sha256_file(path)}
        for path in sorted(fixture_dir.rglob("*")) if path.is_file()
    ]
    db_path = Path(record["isolation"]["catalog_dir"]) / "catalog.sqlite3"

    # --- scan: the registration -------------------------------------------------
    print("leg scan (registers the fifth root) ...")
    before = scan_status(db_path) if db_path.exists() else {}
    scan_leg = run_cli(args.python, config_path, ["scan", "--root-id", FIFTH_ROOT_ID], work)
    scan_leg.update({"id": "scan", "purpose": "the scanner writes the roots row (registration)",
                     "counts_before": before, "counts_after": scan_status(db_path)})
    record["legs"].append(scan_leg)
    print(f"  exit={scan_leg['exit_code']} counts_after={scan_leg['counts_after']}")
    record["roots_rows"] = _roots_rows(db_path)
    rows = _catalog_rows(db_path)
    record["catalog_rows"] = rows
    print(f"  roots={[row['root_id'] for row in record['roots_rows']]} "
          f"documents={len(rows['documents'])} locations={len(rows['locations'])}")

    # --- status + query ---------------------------------------------------------
    status_leg = run_cli(args.python, config_path, ["status"], work)
    status_leg.update({"id": "status", "purpose": "catalog counts after registration"})
    record["legs"].append(status_leg)
    query_leg = run_cli(args.python, config_path, ["query", "--limit", "20"], work)
    query_leg.update({"id": "query", "purpose": "the new root's documents are visible",
                      "document_ids": _document_ids(query_leg["stdout_head"])})
    record["legs"].append(query_leg)
    print(f"leg query exit={query_leg['exit_code']} ids={len(query_leg['document_ids'])}")

    # The query leg above keeps the whole stdout; this is the same read through the
    # product API, so the document list is machine-checkable without parsing text.
    catalog = None
    try:
        catalog = open_catalog(config_path, work)
        listing = catalog.query(limit=20)
        listing_rows = listing if isinstance(listing, list) else listing.get("documents", [])
        record["query_api"] = {
            "mode": "api", "call": "SourceCatalog.query(limit=20)",
            "count": len(listing_rows),
            "document_ids": [row.get("document_id") for row in listing_rows],
            "titles": [row.get("title") for row in listing_rows],
        }
    except Exception as error:  # noqa: BLE001 - recorded, not swallowed
        record["query_api"] = {"mode": "api", "call": "SourceCatalog.query(limit=20)",
                               "error": f"{type(error).__name__}: {error}"}
    query_leg["document_ids"] = _document_ids(query_leg["stdout"])

    # --- the request identity is DISCOVERED from the catalog, not guessed -------
    anchors = []
    for document in rows["documents"]:
        metadata = json.loads(document["metadata_json"] or "{}")
        acquisition = metadata.get("acquisition") or {}
        names = [entity["name"] for entity in rows["entities"]
                 if any(link["document_id"] == document["document_id"]
                        and link["entity_id"] == entity["entity_id"]
                        for link in rows["document_entities"])]
        fiscal_year = acquisition.get("fiscal_year") or (
            (metadata.get("dayu_meta") or {}).get("fiscal_year"))
        try:
            # The sidecar adapter maps fiscal_year through str() ("_normalized_from_sidecar"),
            # so the indexed value is text; SourceRequest requires an int.
            fiscal_year = int(fiscal_year) if fiscal_year is not None else None
        except (TypeError, ValueError):
            fiscal_year = None
        if names and fiscal_year:
            anchors.append({"document_id": document["document_id"], "entity": names[0],
                            "fiscal_year": fiscal_year,
                            "provider_document_id": acquisition.get("provider_document_id"),
                            "title": document["title"]})
    record["anchors"] = anchors
    print(f"  anchors={[(item['title'], item['fiscal_year']) for item in anchors]}")

    record["consumers"] = []
    record["opens"] = []
    if catalog is None or not anchors:
        record["consumers"].append({
            "skipped": "the isolated catalog could not be opened"
            if catalog is None else "no anchored document in the isolated catalog"})
    for anchor in anchors:
        print(f"leg consumer (resolve, exact, FY{anchor['fiscal_year']}) ...")
        resolution = resolve_exact(catalog, entity=anchor["entity"],
                                   fiscal_year=anchor["fiscal_year"],
                                   as_of_date="2026-03-01",
                                   provider_document_id=anchor["provider_document_id"])
        resolution.update({"id": f"consumer-resolve-FY{anchor['fiscal_year']}", "mode": "api",
                           "call": "SourceResolver.resolve(SourceRequest(mode='exact'))",
                           "anchor": anchor,
                           "purpose": "the filing-fetch reuse seam answers for the new root"})
        record["consumers"].append(resolution)
        print(f"  status={resolution['status']} matches={resolution['match_count']} "
              f"ready={resolution['capture_ready']}")
        if resolution["handles"]:
            opened = read_verified(catalog, resolution["handles"][0])
            opened.update({"id": f"open-FY{anchor['fiscal_year']}", "mode": "api",
                           "call": "SourceResolver.read_verified_bytes(handle)",
                           "anchor_document_id": anchor["document_id"],
                           "purpose": "bytes read once and verified against the digest"})
        else:
            opened = {"id": f"open-FY{anchor['fiscal_year']}", "mode": "api",
                      "skipped": "resolve returned no handle", "status": resolution["status"]}
        record["opens"].append(opened)
        print(f"  open ok={opened.get('ok')} status={opened.get('status')}")

    candidates = filing_candidates(catalog, root_ids=(FIFTH_ROOT_ID,))
    candidates.update({"id": "consumer-candidates", "mode": "api",
                       "call": "SourceCatalog.query_filing_candidates(root_ids=(...))",
                       "purpose": "SQL-pushdown candidate listing scoped to the new root"})
    record["consumer_candidates"] = candidates
    print(f"  candidates={candidates['count']}")

    # --- unknowns and deny ------------------------------------------------------
    print("leg unregistered-root ...")
    unregistered_cli = run_cli(args.python, config_path,
                               ["scan", "--root-id", "does_not_exist"], work)
    unregistered_cli.update({"id": "unregistered-root-cli",
                             "purpose": "an unknown --root-id must be refused"})
    record["legs"].append(unregistered_cli)
    record["unregistered_root"] = {
        "cli_exit_code": unregistered_cli["exit_code"],
        "cli_stdout_head": unregistered_cli["stdout_head"],
        "cli_stderr_tail": unregistered_cli["stderr_tail"],
    }
    try:
        catalog = open_catalog(config_path, work)
        record["unregistered_root"]["candidates"] = filing_candidates(
            catalog, root_ids=("does_not_exist",))
    except Exception as error:  # noqa: BLE001
        record["unregistered_root"]["candidates_error"] = f"{type(error).__name__}: {error}"
    record["unregistered_root"]["roots_rows_roots"] = [row["root_id"]
                                                       for row in _roots_rows(db_path)]
    # F-R3-01/C5: with a MIXED --root-id set the selection is non-empty, so the scan takes
    # the dedicated unknown-id branch (scanner.py:762-765) instead of the empty-selection
    # one (:760-761) that a wholly unknown id hits.  Both are recorded; the record does not
    # claim the unregistered id was refused by the unknown-id branch when it was not.
    mixed_cli = run_cli(args.python, config_path,
                        ["scan", "--root-id", FIFTH_ROOT_ID, "--root-id", "does_not_exist"],
                        work)
    mixed_cli.update({"id": "mixed-root-id-cli",
                      "purpose": "a partially unknown --root-id set must be refused by the "
                                 "unknown-id branch, with the valid root NOT scanned"})
    record["legs"].append(mixed_cli)
    record["unregistered_root"]["mixed_cli_exit_code"] = mixed_cli["exit_code"]
    record["unregistered_root"]["mixed_cli_stderr_tail"] = mixed_cli["stderr_tail"]
    record["unregistered_root"]["mixed_cli_counts"] = scan_status(db_path)
    print(f"  mixed exit={mixed_cli['exit_code']} "
          f"stderr={mixed_cli['stderr_tail'].strip()[:120]}")
    print(f"  cli exit={unregistered_cli['exit_code']} "
          f"candidates={record['unregistered_root'].get('candidates', {}).get('count')}")

    print("leg unknown-adapter ...")
    unknown_tree = build_isolated_tree(work / "unknown_adapter", adapter="not_registered_v1",
                                       catalog_dir=".source_catalog_unknown")
    unknown_config = unknown_tree["config_path"]
    try:
        _load_config(unknown_config, work / "unknown_adapter")
        unknown = {"id": "unknown-adapter", "mode": "api", "failed_closed": False,
                   "error": None, "call": "load_catalog_config(adapter_id=not_registered_v1)"}
    except Exception as error:  # noqa: BLE001
        unknown = {"id": "unknown-adapter", "mode": "api", "failed_closed": True,
                   "error": f"{type(error).__name__}: {error}",
                   "call": "load_catalog_config(adapter_id=not_registered_v1)"}
    record["unknown_adapter"] = unknown
    print(f"  failed_closed={unknown['failed_closed']} error={unknown['error']}")

    print("leg deny (reusable_for_filing: false) ...")
    deny_tree = build_isolated_tree(work / "deny", reusable="false",
                                    catalog_dir=".source_catalog_deny")
    deny_config = deny_tree["config_path"]
    deny_work = work / "deny"
    deny_scan = run_cli(args.python, deny_config, ["scan", "--root-id", FIFTH_ROOT_ID], deny_work)
    deny_scan.update({"id": "deny-scan", "purpose": "register the denied root in its own catalog"})
    deny_db = deny_work / ".source_catalog_deny" / "catalog.sqlite3"
    deny: dict = {"scan": {k: v for k, v in deny_scan.items() if k != "stdout"},
                  "runtime_snapshot": deny_tree["runtime_snapshot"],
                  "roots_rows": _roots_rows(deny_db) if deny_db.exists() else []}
    try:
        from company_wiki.source_catalog.policy_2x import export_policy_2x

        _digest, policy = export_policy_2x(_load_config(deny_config, deny_work))
        deny["policy_reusable_roots"] = sorted(
            entry["root_id"] for entry in policy["roots"]
            if entry.get("reusable_for_filing") is True)
        deny["policy_fifth_root"] = next(
            (entry for entry in policy["roots"] if entry["root_id"] == FIFTH_ROOT_ID), None)
    except Exception as error:  # noqa: BLE001
        deny["policy_error"] = f"{type(error).__name__}: {error}"
    # The deny leg asks the SAME questions as the positive leg, on the same bytes, with
    # one field different (`reusable_for_filing: false`), so the comparison is exact.
    deny["resolutions"] = []
    try:
        deny_catalog = open_catalog(deny_config, deny_work)
        for anchor in anchors:
            resolution = resolve_exact(
                deny_catalog, entity=anchor["entity"], fiscal_year=anchor["fiscal_year"],
                as_of_date="2026-03-01",
                provider_document_id=anchor["provider_document_id"])
            resolution.update({"anchor_fiscal_year": anchor["fiscal_year"]})
            resolution.pop("handles", None)
            deny["resolutions"].append(resolution)
        deny["candidates"] = filing_candidates(deny_catalog, root_ids=(FIFTH_ROOT_ID,))
        # F-R3-01 (independent review, P2): the deny above is a RESOLVER-scoped decision.
        # The product's byte entry point gates on root containment only
        # (`resolver.py:2016-2041` calls `_inside_configured_roots`) and never consults
        # reusability, so this run MEASURES that path instead of implying it is denied.
        # The handle is rebuilt from the DENY catalog's own location row, so containment is
        # checked against the deny catalog's configured roots - not against the positive one.
        deny_locations = _catalog_rows(deny_db)["locations"]
        byte_reads = []
        for consumer in record["consumers"]:
            for handle in consumer.get("handles") or []:
                basename = Path(handle["canonical_path"]).name
                location = next(
                    (row for row in deny_locations
                     if Path(row["relative_path"]).name == basename
                     and row["role"] == "original_primary"), None)
                if location is None:
                    continue
                deny_handle = dict(handle)
                deny_handle["canonical_location_id"] = location["location_id"]
                deny_handle["canonical_path"] = location["absolute_path"]
                result = read_verified(deny_catalog, deny_handle)
                result.update({
                    "call": ("SourceResolver.read_verified_bytes(handle rebuilt from the "
                             "DENY catalog's own location row)"),
                    "handle_source": "deny catalog location row",
                    "deny_root_location": {
                        "location_id": location["location_id"],
                        "relative_path": location["relative_path"],
                        "absolute_path": location["absolute_path"],
                        "role": location["role"],
                    },
                })
                byte_reads.append(result)
        deny["byte_entry_point"] = {
            "measured": byte_reads,
            "finding": ("F-R3-01, measured: the DECISION is denied (resolve -> missing) while "
                        "the byte primitive still serves the bytes, because it gates on root "
                        "containment and not on reusable_root_ids"),
        }
    except Exception as error:  # noqa: BLE001
        deny["error"] = f"{type(error).__name__}: {error}"
    record["deny"] = deny
    print(f"  policy_reusable={deny.get('policy_reusable_roots')} "
          f"resolutions={[item.get('status') for item in deny['resolutions']]}")

    # --- post -------------------------------------------------------------------
    print("post-snapshot ...")
    record["post"] = {
        "production_catalog": _catalog_snapshot(),
        "repos": _repos_snapshot(),
        "wiki_src": _tree_fingerprint(WIKI / "src"),
    }
    positive_statuses = [item.get("status") for item in record["consumers"]]
    record["summary"] = {
        "fifth_root_id": FIFTH_ROOT_ID,
        "fifth_root_registered": any(row["root_id"] == FIFTH_ROOT_ID
                                     for row in record["roots_rows"]),
        "query_documents": len(record.get("query_api", {}).get("document_ids", [])),
        "consumer_statuses": positive_statuses,
        "consumer_reused": [status for status in positive_statuses
                            if status and status.startswith("reused")],
        "opens_verified": sum(1 for item in record["opens"] if item.get("ok") is True),
        "candidates_from_fifth_root": record.get("consumer_candidates", {}).get("count"),
        "deny_statuses": [item.get("status") for item in deny["resolutions"]],
        "deny_policy_reusable": deny.get("policy_reusable_roots"),
        "unknown_adapter_failed_closed": unknown["failed_closed"],
        "unregistered_root_cli_exit": unregistered_cli["exit_code"],
        "unregistered_root_mixed_cli_exit": mixed_cli["exit_code"],
        "unregistered_root_mixed_cli_error": mixed_cli["stderr_tail"].strip()[:200],
        "scan_runs_after_mixed_refusal": record["unregistered_root"][
            "mixed_cli_counts"].get("scan_runs"),
        "deny_byte_entry_point_statuses": [
            item["status"] for item in deny.get("byte_entry_point", {}).get("measured", [])],
    }
    record["invariants"] = {
        "production_catalog_unchanged": (
            record["pre"]["production_catalog"] == record["post"]["production_catalog"]),
        "production_wal_untouched": (
            record["pre"]["production_catalog"].get("catalog.sqlite3-wal")
            == record["post"]["production_catalog"].get("catalog.sqlite3-wal")),
        "repos_unchanged_during_run": all(
            record["pre"]["repos"][name]["porcelain"] == record["post"]["repos"][name]["porcelain"]
            for name in REPOS),
        "heads_unchanged": all(
            record["pre"]["repos"][name]["head"] == record["post"]["repos"][name]["head"]
            for name in REPOS),
        "product_source_unchanged": (
            record["pre"]["wiki_src"] == record["post"]["wiki_src"]),
        "fifth_root_registered": record["summary"]["fifth_root_registered"],
        "four_stand_in_roots_absent_from_roots_table": [
            row["root_id"] for row in record["roots_rows"]
            if row["root_id"] in STAND_IN_ROOTS] == [],
    }
    record["ran_at_utc"] = datetime.now(UTC).isoformat()
    for leg in record["legs"]:
        text = leg.get("stdout") or ""
        if len(text) > 20000:
            leg["stdout"] = text[:20000]
            leg["stdout_truncated"] = True
    if not args.keep:
        work_note = "isolated tree removed after the run"
    else:
        work_note = f"isolated tree kept at {work}"
    record["workdir_note"] = work_note
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(f"wrote {args.out}")
    print(json.dumps(record["invariants"], indent=2))
    failed = [name for name, ok in record["invariants"].items() if not ok]
    print("INVARIANTS FAILED: " + ", ".join(failed) if failed else "all invariants hold")
    if not args.keep:
        shutil.rmtree(work, ignore_errors=True)
    return 1 if failed else 0


def verify(out_path: Path) -> int:
    """Re-check a recorded run: the production snapshots must still hold."""
    record = json.loads(out_path.read_text(encoding="utf-8"))
    live = {
        "production_catalog": _catalog_snapshot(),
        "repos": _repos_snapshot(),
        "wiki_src": _tree_fingerprint(WIKI / "src"),
    }
    checks = {
        "production_catalog_still_post": live["production_catalog"]
        == record["post"]["production_catalog"],
        "production_catalog_still_pre": live["production_catalog"]
        == record["pre"]["production_catalog"],
        "wiki_src_still_post": live["wiki_src"] == record["post"]["wiki_src"],
        "heads_still_post": all(live["repos"][name]["head"]
                                == record["post"]["repos"][name]["head"] for name in REPOS),
    }
    # The working tree is NOT a pass/fail check here: this run's own deliverables
    # (the evidence files) appear as untracked paths after the in-run snapshot, and the
    # record itself is written after that snapshot.  The in-run invariant
    # `repos_unchanged_during_run` already proves nothing moved while the harness ran.
    repo_diff = {
        name: [line for line in live["repos"][name]["porcelain"].splitlines()
               if line not in record["post"]["repos"][name]["porcelain"].splitlines()]
        for name in REPOS
    }
    print(json.dumps({"checks": checks, "repo_paths_added_since_post": repo_diff,
                      "live": {"production_catalog": live["production_catalog"],
                               "wiki_src": live["wiki_src"]}},
                     ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - a crash must be visible, not silent
        traceback.print_exc()
        raise SystemExit(2)
