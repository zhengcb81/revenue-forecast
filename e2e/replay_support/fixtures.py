"""Synthetic two-document lake for the W14 clean chain (E03/E04).

Builds a minimal company-wiki project around the synthetic fixtures in
``tests/fixtures/w14_chain`` (identity, periods, and hashes come from the
fixture manifest — nothing about a real company):

- one annual-report PDF and one quarterly-report TXT, both registered through
  the PUBLIC ``company_wiki.source_catalog.cli scan`` subprocess of the frozen
  deployment;
- a fixture security-master snapshot (two issuers sharing one alias so the
  ambiguity error path is real);
- a runtime-policy snapshot and v2 artifact/review-receipt rows written
  through the frozen company-wiki library itself (the same fail-closed writer
  production uses), mirroring the proven recipe of RF's legacy
  ``tests/e2e_support/isolated_lake.py``.

The builder imports the DEPLOYED company-wiki package (``cwp_src`` is
inserted at sys.path[0]) so catalog construction also proves the frozen code,
never the live workspace or an editable install.
"""

from __future__ import annotations

import hashlib
import json
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

AS_OF_FALLBACK = "2026-09-30"


class FixtureError(RuntimeError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_manifest(fixture_root: Path) -> dict:
    manifest_path = fixture_root / "w14_fixture_manifest.json"
    if not manifest_path.is_file():
        raise FixtureError(f"fixture manifest absent: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for key, document in manifest["documents"].items():
        path = fixture_root / document["path"]
        if not path.is_file():
            raise FixtureError(f"fixture file absent: {path}")
        data = path.read_bytes()
        if sha256_bytes(data) != document["sha256"]:
            raise FixtureError(
                f"fixture bytes diverge from manifest for {key}: {path}")
    return manifest


@dataclass
class LakeDoc:
    key: str
    rel_path: str          # wiki-root relative POSIX path
    sha256: str
    byte_size: int
    document_kind: str
    fiscal_year: int | None
    fiscal_period: str | None
    provider_document_id: str


@dataclass
class LakeBuild:
    wiki_root: Path
    catalog_path: Path
    config_path: Path
    docs: dict[str, LakeDoc]
    scan_returncode: int
    scan_stdout_tail: str
    scan_stderr_tail: str
    scan_pid: int | None = None


def _sidecar_for(document: dict, identity: dict) -> dict:
    return {
        "schema_version": "1.0",
        "canonical_entity_id": f"ent-{identity['security_id']}",
        "display_name": document["sidecar_title"],
        "market": identity["market"],
        "security_id": identity["security_id"],
        "document_kind": document["document_kind"],
        "fiscal_year": document["fiscal_year"],
        "fiscal_period": document.get("fiscal_period"),
        "period_end": document["period_end"],
        "filing_date": document["filing_date"],
        "published_date": document["published_date"],
        "retrieved_at": document["retrieved_at"],
        "form_type": document["document_kind"],
        "provider": document["provider"],
        "provider_document_id": document["provider_document_id"],
        "source_url": document["source_url"],
        "content_sha256": document["sha256"],
        "source_title": document["sidecar_title"],
    }


def _write_security_master(catalog_dir: Path, manifest: dict) -> None:
    identity = manifest["identity"]
    def _record(sec: str, name: str, aliases: list[str]) -> dict:
        return {
            "active": True, "aliases": aliases, "canonical_name": name,
            "exchange": identity["exchange"], "ticker": sec,
            "identifiers": {}, "market": identity["market"],
            "schema_version": "1.0", "security_id": sec,
            "source_name": "fixture", "source_record_id": f"fixture-{sec}",
            "source_url": "https://fixtures.invalid/w14/" + sec,
        }
    payload = {
        "schema_version": "1.0", "market": identity["market"],
        "record_count": 2, "retrieved_at": "2026-08-12T00:00:00Z",
        "sources": ["fixture"],
        "records": [
            _record(identity["security_id"], identity["canonical_name"],
                    identity["aliases"] + [identity["ambiguous_alias"]]),
            _record(identity["second_issuer_security_id"],
                    identity["second_issuer_canonical_name"],
                    [identity["ambiguous_alias"]]),
        ],
    }
    master = catalog_dir / "security_master"
    master.mkdir(parents=True, exist_ok=True)
    (master / f"{identity['market'].lower()}.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_wiki_config(wiki_root: Path, companies: Path) -> Path:
    config_dir = wiki_root / "config"
    config_dir.mkdir(parents=True, exist_ok=True)
    config = config_dir / "source_catalog.yaml"
    config.write_text("\n".join([
        'schema_version: "1.0"',
        'catalog_dir: "${PROJECT_ROOT}/.source_catalog"',
        "reusable_root_kinds: [company_raw]",
        "roots:",
        "  - root_id: company_raw",
        "    kind: company_raw",
        f'    path: "{companies.as_posix()}"',
        "    priority: 10",
    ]), encoding="utf-8")
    return config


def _write_runtime_policy(config_path: Path, cwp_src: Path) -> None:
    """CWP-valid RuntimePolicySnapshot bound to the real YAML-loaded config."""
    saved = list(sys.path)
    try:
        if str(cwp_src) not in sys.path:
            sys.path.insert(0, str(cwp_src))
        from company_wiki.source_catalog.config import load_catalog_config
        from company_wiki.source_catalog.flags import FLAGS
        from company_wiki.source_catalog.policy_2x import export_policy_2x
        from company_wiki.source_catalog.runtime_policy import build_snapshot

        conf = load_catalog_config(config_path)
        policy_hash, _ = export_policy_2x(conf)
        snapshot = build_snapshot({
            "schema_version": "1.0",
            "current_epoch": "epoch-w14-fixture",
            "active_cohorts": ["w14-fixture-cohort"],
            "flags": {name: False for name in FLAGS}
            | {"legacy_bridge_enabled": True},
            "policy_hash": policy_hash,
            "updated_at": "2026-08-10T00:00:00Z",
        })
        catalog_dir = config_path.parent.parent / ".source_catalog"
        (catalog_dir / "runtime_policy.json").write_text(
            json.dumps(snapshot, ensure_ascii=False, sort_keys=True),
            encoding="utf-8")
    finally:
        sys.path[:] = saved


def _preset_artifacts_and_receipts(
    config_path: Path, cwp_src: Path, docs: dict[str, LakeDoc],
    manifest: dict,
) -> dict:
    """v2 normalized artifacts + producer events + fail-closed review receipts.

    Written through the frozen company-wiki library (same writer contract as
    the legacy isolated lake); the receipt is a DIAGNOSTIC in the current
    reader, never an authorization gate.
    """
    saved = list(sys.path)
    try:
        if str(cwp_src) not in sys.path:
            sys.path.insert(0, str(cwp_src))
        from company_wiki.source_catalog.prompt_injection import (
            record_prompt_injection_review,
        )
        from company_wiki.source_catalog.prompt_injection_guard import (
            RULESET_HASH,
        )

        catalog_path = config_path.parent.parent / ".source_catalog" / "catalog.sqlite3"
        derived = config_path.parent.parent / "derived"
        con = sqlite3.connect(str(catalog_path))
        con.row_factory = sqlite3.Row
        evidence = {"documents": [], "artifacts": 0, "receipts": 0}
        try:
            for doc in docs.values():
                row = con.execute(
                    "SELECT d.document_id, d.primary_source_id FROM documents d "
                    "JOIN locations l ON l.document_id = d.document_id "
                    "WHERE l.root_id='company_raw' AND l.relative_path=?",
                    (doc.rel_path.split("raw/", 1)[1],),
                ).fetchone()
                if row is None:
                    row = con.execute(
                        "SELECT d.document_id, d.primary_source_id FROM documents d "
                        "JOIN locations l ON l.document_id = d.document_id "
                        "WHERE l.relative_path LIKE ?",
                        (f"%{Path(doc.rel_path).name}",),
                    ).fetchone()
                if row is None:
                    raise FixtureError(
                        f"scan did not register the fixture document: {doc.rel_path}")
                document_id = row["document_id"]
                source_id = row["primary_source_id"]
                body = (f"normalized markdown for {doc.rel_path} (w14 v2)\n").encode()
                content_sha = sha256_bytes(body)
                digest = hashlib.sha256(
                    (document_id + "\0normalized\0source_catalog_normalizer\0"
                     "1.0.0").encode()).hexdigest()
                art_id = "urn:company-wiki:artifact:sha256:" + digest
                sub = derived / digest[:2] / digest
                sub.mkdir(parents=True, exist_ok=True)
                (sub / "normalized.md").write_bytes(body)
                source_sha = con.execute(
                    "SELECT content_sha256 FROM sources WHERE source_id=?",
                    (source_id,)).fetchone()[0]
                con.execute(
                    """INSERT OR REPLACE INTO artifacts
                    (artifact_id,document_id,source_id,artifact_role,path,
                     content_sha256,byte_size,mime_type,generator_name,
                     generator_version,status,error,schema_version,source_sha256,
                     metadata_json,created_at)
                    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,strftime('%Y-%m-%dT%H:%M:%SZ','now'))""",
                    (art_id, document_id, source_id, "normalized",
                     str(sub / "normalized.md"), content_sha, len(body),
                     "text/markdown", "source_catalog_normalizer", "1.0.0",
                     "completed", None, "1.0", source_sha,
                     json.dumps({"schema_version": "1.0",
                                 "parser_name": "plain_text",
                                 "parser_version": "1.0.0",
                                 "quality_flags": [], "span_count": 0},
                                ensure_ascii=False)))
                con.execute(
                    """INSERT OR IGNORE INTO producer_events
                    (event_id,document_id,artifact_role,producer_name,
                     producer_version,event_type,created_at)
                    VALUES(?,?,?,?,?,?,datetime('now'))""",
                    (f"pe-{art_id}-w14", document_id, "normalized",
                     "source_catalog_normalizer", "1.0.0", "parser"))
                con.execute(
                    "INSERT OR IGNORE INTO document_entities"
                    "(document_id, entity_id, confidence, method) VALUES(?,?,?,?)",
                    (document_id,
                     f"company-name:{manifest['identity']['security_id']}",
                     1.0, "sidecar"))
                record_prompt_injection_review(
                    con, document_id, status="not_detected",
                    reviewer="w14-fixture-reviewer", evidence_sha256=content_sha,
                    now="2026-08-12T00:00:00Z", source_sha256=source_sha,
                    policy_hash=RULESET_HASH, evidence_payload=body)
                evidence["documents"].append(
                    {"key": doc.key, "document_id": document_id,
                     "source_id": source_id, "artifact_id": art_id})
                evidence["artifacts"] += 1
                evidence["receipts"] += 1
            con.commit()
            return evidence
        finally:
            con.close()
    finally:
        sys.path[:] = saved


def build_lake(
    wiki_root: Path, fixture_root: Path, cwp_src: Path, *, env: dict,
) -> LakeBuild:
    """Materialize the synthetic lake; registration runs the PUBLIC scan CLI."""
    manifest = load_manifest(fixture_root)
    identity = manifest["identity"]
    companies = wiki_root / "companies"
    docs: dict[str, LakeDoc] = {}
    subdir_by_kind = {"annual_report": "annual", "quarterly_report": "quarterly"}
    for key, document in manifest["documents"].items():
        kind_dir = subdir_by_kind.get(document["document_kind"])
        if kind_dir is None:
            raise FixtureError(
                f"no lake subdir mapped for kind {document['document_kind']}")
        raw_dir = companies / identity["canonical_name"] / "raw" / \
            "financial_reports" / kind_dir
        raw_dir.mkdir(parents=True, exist_ok=True)
        data = (fixture_root / document["path"]).read_bytes()
        target = raw_dir / Path(document["path"]).name
        target.write_bytes(data)
        sidecar = _sidecar_for(document, identity)
        Path(str(target) + ".source.json").write_text(
            json.dumps(sidecar, ensure_ascii=False), encoding="utf-8")
        rel = target.relative_to(wiki_root).as_posix()
        docs[key] = LakeDoc(
            key=key, rel_path=rel, sha256=document["sha256"],
            byte_size=document["byte_size"],
            document_kind=document["document_kind"],
            fiscal_year=document["fiscal_year"],
            fiscal_period=document.get("fiscal_period"),
            provider_document_id=document["provider_document_id"])

    _write_security_master(wiki_root / ".source_catalog", manifest)
    config = _write_wiki_config(wiki_root, companies)

    scan_argv = [sys.executable, "-X", "utf8", "-B",
                 "-m", "company_wiki.source_catalog.cli",
                 "--config", str(config), "scan"]
    proc = subprocess.Popen(
        scan_argv, cwd=str(wiki_root), env=env, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, encoding="utf-8",
        errors="replace")
    scan_pid = proc.pid
    try:
        out, err = proc.communicate(timeout=300)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, err = proc.communicate() or ("", "")
        raise FixtureError(
            f"public scan timed out after 300s pid={scan_pid}")
    if proc.returncode != 0:
        raise FixtureError(
            f"public scan failed rc={proc.returncode} pid={scan_pid}: "
            f"{(err or out)[-800:]}")
    _write_runtime_policy(config, cwp_src)

    evidence = _preset_artifacts_and_receipts(config, cwp_src, docs, manifest)
    catalog_path = wiki_root / ".source_catalog" / "catalog.sqlite3"
    (wiki_root / ".source_catalog" / "w14_preset.json").write_text(
        json.dumps(evidence, ensure_ascii=False, indent=1), encoding="utf-8")
    return LakeBuild(
        wiki_root=wiki_root, catalog_path=catalog_path, config_path=config,
        docs=docs, scan_returncode=proc.returncode,
        scan_stdout_tail=(out or "")[-400:],
        scan_stderr_tail=(err or "")[-400:], scan_pid=scan_pid)
