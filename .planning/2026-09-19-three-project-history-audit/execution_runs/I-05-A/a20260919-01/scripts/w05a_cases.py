"""W05A case harness: default producer -> sections/summary -> bundle -> query.

Run with the iso venv interpreter and PYTHONPATH pointing at the isolated
company-wiki src copy.  Every case builds its OWN catalog under scratch/,
runs the REAL default producers, then applies exactly one mutation through a
raw SQL/filesystem write and asks the section query what it can consume.

Expected values live in EXPECT_* tables below and are copied verbatim from
oracle.md (frozen before this file was first run).  Nothing in this harness
derives an expectation by calling the code under test.

  <py> -X utf8 -B scripts/w05a_cases.py before   -> before/case_results.json
  <py> -X utf8 -B scripts/w05a_cases.py after    -> after/case_results.json
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SAMPLES = ATTEMPT / "samples"
# Case catalogs live under %TEMP%: the real derived-artifact layout
# (derived/<2>/<64>/sections/<role>.md) plus the repository path already
# exceeds the Windows 260-character limit inside the attempt directory
# (measured: 261 > 259 fails, 250 succeeds, LongPathsEnabled=0), so keeping
# the per-case catalogs in the short %TEMP% root is the same MAX_PATH
# compromise I-02-E recorded.  Every path is bound in binding.json.
SCRATCH = Path(os.environ.get("W05A_SCRATCH", r"C:\Users\郑曾波\AppData\Local\Temp\w05a")) / "a20260919-01"
CW_SRC = Path(os.environ["W05A_CW_SRC"])  # isolated company-wiki src root

if str(CW_SRC) not in sys.path:
    sys.path.insert(0, str(CW_SRC))

from company_wiki.source_catalog.artifact_handle import (  # noqa: E402
    ARTIFACT_HANDLE_SCHEMA_VERSION,
    validate_artifact,
)
from company_wiki.source_catalog.models import CatalogConfig, RootSpec  # noqa: E402
from company_wiki.source_catalog.models import (  # noqa: E402
    NORMALIZER_VERSION,
    SECTION_EXTRACTOR_VERSION,
)
from company_wiki.source_catalog.section_extractor import (  # noqa: E402
    SECTION_EXTRACTOR_NAME,
    extract_sections_catalog,
)
from company_wiki.source_catalog.service import (  # noqa: E402
    SourceCatalog,
)
from company_wiki.source_catalog.source_bundle import (  # noqa: E402
    GENERATOR_REGISTRY,
    KNOWN_ARTIFACT_ROLES,
    build_source_bundle,
)

GENERATOR_REGISTRY_ROLES = sorted(KNOWN_ARTIFACT_ROLES)
from company_wiki.source_catalog.store import CatalogStore, canonical_json  # noqa: E402
from company_wiki.source_catalog.summarizer import summarize_catalog  # noqa: E402

# The module under test is imported through the ISOLATED package (it uses
# package-relative imports), and PYTHONDONTWRITEBYTECODE=1 keeps a before/after
# run from sharing a stale bytecode cache.
SECTION_QUERY_PATH = CW_SRC / "company_wiki" / "source_catalog" / "section_query.py"
from company_wiki.source_catalog import section_query as _sq  # noqa: E402
from company_wiki.source_catalog.section_query import (  # noqa: E402
    SectionQueryError,
    SectionQueryService,
)

assert Path(_sq.__file__).resolve() == SECTION_QUERY_PATH.resolve(), _sq.__file__

SAMPLE = json.loads((SAMPLES / "sample.json").read_text(encoding="utf-8"))

# --------------------------------------------------------------------------
# Frozen expectations (verbatim from oracle.md; never produced by the code
# under test).
# --------------------------------------------------------------------------
EXPECT_ROLES = ["business_overview", "mda"]
EXPECT_TITLES = ["公司业务概要", "经营情况讨论与分析"]
EXPECT_SECTION_COUNT = 2
EXPECT_ABSENT_ROLES = ["consumer_analysis", "markdown", "summary"]
# reason codes frozen for each mutation; "(pass)" = the query must return a
# usable result for that case.
EXPECT_REASON = {
    "c0": "(pass)",
    "c1": "sections_status_not_completed",
    "c2": "sections_binding_error",
    "c3": "sections_binding_error",
    "c4": "sections_file_missing",
    "c5": "sections_binding_error",
    "c6": "sections_binding_error",
    "c7": "sections_span_unbound",
    "c8": "sections_span_unbound",
}


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def utc_now() -> str:
    import datetime as _dt

    return _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# --------------------------------------------------------------------------
# fixture construction (real producers)
# --------------------------------------------------------------------------


def build_catalog(case_dir: Path) -> dict:
    """Seed the fixed sample, run the REAL default producers, return facts."""
    if case_dir.exists():
        shutil.rmtree(case_dir)
    catalog_dir = case_dir / "catalog"
    roots_dir = case_dir / "roots"
    raw_dir = roots_dir / "emerald" / "annual"
    raw_dir.mkdir(parents=True, exist_ok=True)
    source_file = raw_dir / "annual_report.txt"
    shutil.copyfile(SAMPLES / "annual_source.txt", source_file)

    normalized = (SAMPLES / "annual_normalized.md").read_text(encoding="utf-8")
    norm_bytes = normalized.encode("utf-8")
    norm_sha = hashlib.sha256(norm_bytes).hexdigest()

    config = CatalogConfig(
        project_root=case_dir,
        catalog_dir=catalog_dir,
        roots=(
            RootSpec(
                root_id="emerald-raw",
                path=roots_dir,
                kind="company_raw",
                priority=10,
            ),
        ),
    )
    store = CatalogStore(config.database_path)
    source_id = SAMPLE["source_id"]
    document_id = SAMPLE["document_id"]
    source_sha = SAMPLE["source_sha256"]
    source_size = source_file.stat().st_size
    root_path = str(roots_dir.resolve())

    with store.transaction() as connection:
        connection.execute(
            "INSERT INTO roots(root_id,path,kind,priority) VALUES(?,?,?,?)",
            ("emerald-raw", root_path, "company_raw", 10),
        )
        connection.execute(
            "INSERT INTO sources(source_id,content_sha256,byte_size,mime_type,"
            "first_seen_at) VALUES(?,?,?,?,?)",
            (source_id, source_sha, source_size, "text/plain", "2026-09-19T00:00:00Z"),
        )
        connection.execute(
            "INSERT INTO documents(document_id,primary_source_id,title,source_type,"
            "document_kind,published_date,source_status,metadata_priority,"
            "metadata_json,first_seen_at,last_seen_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (
                document_id,
                source_id,
                SAMPLE["title"],
                "regulatory_filing",
                "annual_report",
                SAMPLE["published_date"],
                "active",
                100,
                canonical_json({"entity": "翡翠矿业", "fiscal_year": 2025}),
                "2026-09-19T00:00:00Z",
                "2026-09-19T00:00:00Z",
            ),
        )
        connection.execute(
            "INSERT INTO locations(location_id,root_id,relative_path,absolute_path,"
            "source_id,document_id,role,location_status,last_seen_run,metadata_json) "
            "VALUES(?,?,?,?,?,?,?,?,?,?)",
            (
                "loc-emerald-1",
                "emerald-raw",
                "emerald/annual/annual_report.txt",
                str(source_file.resolve()),
                source_id,
                document_id,
                "original_primary",
                "active",
                "run-w05a",
                canonical_json({}),
            ),
        )
        # The normalized artifact: derived file + row, written exactly the way
        # normalizer.normalize_catalog writes it (verified bytes).
        derived = config.derived_dir / norm_sha[:2] / norm_sha / "normalized.md"
        derived.parent.mkdir(parents=True, exist_ok=True)
        derived.write_bytes(norm_bytes)
        connection.execute(
            "INSERT INTO artifacts(artifact_id,document_id,source_id,artifact_role,"
            "path,content_sha256,byte_size,mime_type,generator_name,generator_version,"
            "status,error,schema_version,source_sha256,metadata_json,created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "urn:cw:artifact:sha256:"
                + hashlib.sha256(
                    (document_id + "\0normalized\0" + NORMALIZER_VERSION).encode()
                ).hexdigest(),
                document_id,
                source_id,
                "normalized",
                str(derived.resolve()),
                norm_sha,
                len(norm_bytes),
                "text/markdown",
                "source_catalog_normalizer",
                NORMALIZER_VERSION,
                "completed",
                None,
                ARTIFACT_HANDLE_SCHEMA_VERSION,
                source_sha,
                canonical_json(
                    {
                        "schema_version": ARTIFACT_HANDLE_SCHEMA_VERSION,
                        "parser_name": "sample-parser",
                        "parser_version": "1.0.0",
                        "quality_flags": [],
                        "span_count": 3,
                    }
                ),
                "2026-09-19T00:00:00Z",
            ),
        )
        # evidence spans: two on page 1 (the only page in the fixed sample)
        for index, (span_id, page) in enumerate(
            (("span-emerald-1", 1), ("span-emerald-2", 1)), start=1
        ):
            connection.execute(
                "INSERT INTO evidence_spans(span_id,document_id,source_id,locator,"
                "page_number,paragraph_index,table_index,raw_text,span_json,"
                "parser_name,parser_version,parse_status) "
                "VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (
                    span_id,
                    document_id,
                    source_id,
                    f"p{page}#para{index}",
                    page,
                    index,
                    None,
                    "fixture span text",
                    canonical_json({"span_id": span_id, "page": page}),
                    "sample-parser",
                    "1.0.0",
                    "parsed",
                ),
            )

    # ---- REAL producers -------------------------------------------------
    # The production loop reaches these directories through real runs only
    # after the derived tree already exists; create the two paths the
    # producers write into so the fixture does not depend on that history.
    (config.derived_dir / norm_sha[:2] / norm_sha / "sections").mkdir(
        parents=True, exist_ok=True
    )
    sections_report = extract_sections_catalog(config, store)
    summary_report = summarize_catalog(config, store)

    return {
        "case_dir": case_dir,
        "config": config,
        "store": store,
        "sections_report": sections_report,
        "summary_report": summary_report,
    }


def seed_catalog_only(case_dir: Path) -> dict:
    """Seed sources/documents/normalized ONLY - no sections producer run.

    This is the state W05A-N2 is about: the document is eligible for section
    extraction (normalized is present) while the only sections row is a
    failed/stale one from an earlier attempt or an earlier generator.
    """
    if case_dir.exists():
        shutil.rmtree(case_dir)
    catalog_dir = case_dir / "catalog"
    roots_dir = case_dir / "roots"
    raw_dir = roots_dir / "emerald" / "annual"
    raw_dir.mkdir(parents=True, exist_ok=True)
    source_file = raw_dir / "annual_report.txt"
    shutil.copyfile(SAMPLES / "annual_source.txt", source_file)
    normalized = (SAMPLES / "annual_normalized.md").read_text(encoding="utf-8")
    norm_bytes = normalized.encode("utf-8")
    norm_sha = hashlib.sha256(norm_bytes).hexdigest()
    config = CatalogConfig(
        project_root=case_dir,
        catalog_dir=catalog_dir,
        roots=(
            RootSpec(root_id="emerald-raw", path=roots_dir, kind="company_raw", priority=10),
        ),
    )
    store = CatalogStore(config.database_path)
    document_id = SAMPLE["document_id"]
    with store.transaction() as connection:
        connection.execute(
            "INSERT INTO roots(root_id,path,kind,priority) VALUES(?,?,?,?)",
            ("emerald-raw", str(roots_dir.resolve()), "company_raw", 10),
        )
        connection.execute(
            "INSERT INTO sources(source_id,content_sha256,byte_size,mime_type,"
            "first_seen_at) VALUES(?,?,?,?,?)",
            (SAMPLE["source_id"], SAMPLE["source_sha256"], source_file.stat().st_size,
             "text/plain", "2026-09-19T00:00:00Z"),
        )
        connection.execute(
            "INSERT INTO documents(document_id,primary_source_id,title,source_type,"
            "document_kind,published_date,source_status,metadata_priority,"
            "metadata_json,first_seen_at,last_seen_at) VALUES(?,?,?,?,?,?,?,?,?,?,?)",
            (document_id, SAMPLE["source_id"], SAMPLE["title"], "regulatory_filing",
             "annual_report", SAMPLE["published_date"], "active", 100,
             canonical_json({"entity": "翡翠矿业", "fiscal_year": 2025}),
             "2026-09-19T00:00:00Z", "2026-09-19T00:00:00Z"),
        )
        derived = config.derived_dir / norm_sha[:2] / norm_sha / "normalized.md"
        derived.parent.mkdir(parents=True, exist_ok=True)
        derived.write_bytes(norm_bytes)
        (config.derived_dir / norm_sha[:2] / norm_sha / "sections").mkdir(
            parents=True, exist_ok=True
        )
        connection.execute(
            "INSERT INTO artifacts(artifact_id,document_id,source_id,artifact_role,"
            "path,content_sha256,byte_size,mime_type,generator_name,generator_version,"
            "status,error,schema_version,source_sha256,metadata_json,created_at) "
            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (
                "urn:cw:artifact:sha256:"
                + hashlib.sha256(
                    (document_id + "\0normalized\0" + NORMALIZER_VERSION).encode()
                ).hexdigest(),
                document_id, SAMPLE["source_id"], "normalized", str(derived.resolve()),
                norm_sha, len(norm_bytes), "text/markdown", "source_catalog_normalizer",
                NORMALIZER_VERSION, "completed", None, ARTIFACT_HANDLE_SCHEMA_VERSION,
                SAMPLE["source_sha256"],
                canonical_json({"schema_version": ARTIFACT_HANDLE_SCHEMA_VERSION,
                                "parser_name": "sample-parser", "parser_version": "1.0.0",
                                "quality_flags": [], "span_count": 2}),
                "2026-09-19T00:00:00Z",
            ),
        )
        for index, (span_id, page) in enumerate(
            (("span-emerald-1", 1), ("span-emerald-2", 1)), start=1
        ):
            connection.execute(
                "INSERT INTO evidence_spans(span_id,document_id,source_id,locator,"
                "page_number,paragraph_index,table_index,raw_text,span_json,"
                "parser_name,parser_version,parse_status) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (span_id, document_id, SAMPLE["source_id"], f"p{page}#para{index}", page,
                 index, None, "fixture span text",
                 canonical_json({"span_id": span_id, "page": page}),
                 "sample-parser", "1.0.0", "parsed"),
            )
    return {"case_dir": case_dir, "config": config, "store": store}


def raw_rows(db_path: Path) -> list[dict]:
    """ALL sections rows, unfiltered, read with a plain read-only connection."""
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        rows = [
            dict(row)
            for row in connection.execute(
                "SELECT artifact_id,artifact_role,generator_name,generator_version,"
                "status,path,content_sha256,source_sha256,schema_version,created_at,"
                "metadata_json FROM artifacts WHERE artifact_role='sections' "
                "ORDER BY created_at,artifact_id"
            )
        ]
    finally:
        connection.close()
    return rows


def raw_exec(db_path: Path, sql: str, params: tuple = ()) -> None:
    connection = sqlite3.connect(str(db_path))
    try:
        connection.execute(sql, params)
        connection.commit()
    finally:
        connection.close()


def query_once(db_path: Path) -> dict:
    """Ask the code under test; classify the outcome without judging it."""
    try:
        result = SectionQueryService(db_path).list_sections(
            document_id=SAMPLE["document_id"]
        )
    except SectionQueryError as exc:
        return {"outcome": "error", "error_type": type(exc).__name__, "message": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {
            "outcome": "unexpected_error",
            "error_type": type(exc).__name__,
            "message": str(exc),
        }
    return {"outcome": "returned", **result.to_dict()}


def classify(result: dict, expected_reason: str) -> dict:
    """Verdict against the frozen expectation, plus the raw independent facts."""
    returned = result.get("outcome") == "returned"
    if expected_reason == "(pass)":
        verdict = "PASS" if returned else "counterexample"
        return {
            "verdict": verdict,
            "usable_content_returned": returned,
            "reason_reported": None,
        }
    reason_reported = None
    if result.get("outcome") in ("error", "unexpected_error"):
        message = result.get("message") or ""
        reason_reported = message.split(":")[0].strip() or None
        if message.startswith("sections unusable: "):
            head = message[len("sections unusable: "):]
            reason_reported = head.split(" (")[0].strip()
    blocked = not returned and reason_reported == expected_reason
    return {
        "verdict": "PASS" if blocked else "counterexample",
        "usable_content_returned": returned,
        "reason_reported": reason_reported,
        "expected_reason": expected_reason,
    }


# --------------------------------------------------------------------------
# independent evidence (never derived from the code under test)
# --------------------------------------------------------------------------


def independent_index_facts(config: CatalogConfig) -> dict:
    db_path = config.database_path
    rows = raw_rows(db_path)
    if len(rows) != 1:
        return {"error": f"expected exactly 1 sections row, found {len(rows)}"}
    row = rows[0]
    index_path = Path(row["path"])
    facts: dict = {
        "sections_row_count": len(rows),
        "row": {
            key: row[key]
            for key in (
                "artifact_id",
                "generator_name",
                "generator_version",
                "status",
                "path",
                "content_sha256",
                "source_sha256",
                "schema_version",
                "created_at",
            )
        },
        "index_exists": index_path.is_file(),
    }
    if not facts["index_exists"]:
        return facts
    index_bytes = index_path.read_bytes()
    facts["index_sha256_recomputed"] = hashlib.sha256(index_bytes).hexdigest()
    facts["index_sha256_matches_row"] = (
        facts["index_sha256_recomputed"] == row["content_sha256"]
    )
    entries = json.loads(index_bytes.decode("utf-8"))
    facts["entry_count"] = len(entries)
    section_files = []
    for entry in entries:
        path = Path(entry["path"])
        exists = path.is_file()
        text = path.read_text(encoding="utf-8") if exists else ""
        section_files.append(
            {
                "role": entry["role"],
                "title": entry["title"],
                "path": str(path),
                "exists": exists,
                "char_start": entry["char_start"],
                "char_end": entry["char_end"],
                "file_char_count": len(text),
                "char_span_fits_file": bool(
                    exists
                    and entry["char_end"] <= len(text)
                    and entry["char_start"] >= 0
                    and entry["char_end"] > entry["char_start"]
                ),
                # The index records body-relative offsets; the per-section
                # file holds exactly that slice.  The file's own length IS
                # the slice length, so this is the check that does not need
                # the normalized body at all.  (char_span_fits_file above is
                # body-relative and does NOT apply to the slice file - it is
                # kept only as raw evidence.)
                "file_length_equals_span": bool(
                    exists and len(text) == entry["char_end"] - entry["char_start"]
                ),
                "page_start": entry.get("page_start"),
                "page_end": entry.get("page_end"),
                "span_ids": list(entry.get("span_ids") or []),
                "span_rows_in_db": [],
                "span_ids_all_present": None,
            }
        )
    connection = sqlite3.connect(f"file:{db_path}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        for item in section_files:
            present = []
            for span_id in item["span_ids"]:
                found = connection.execute(
                    "SELECT count(*) AS n FROM evidence_spans WHERE span_id=? "
                    "AND document_id=?",
                    (span_id, SAMPLE["document_id"]),
                ).fetchone()["n"]
                present.append({"span_id": span_id, "rows": found})
            item["span_rows_in_db"] = present
            item["span_ids_all_present"] = all(p["rows"] > 0 for p in present)
    finally:
        connection.close()
    facts["section_files"] = section_files
    return facts


def bundle_facts(config: CatalogConfig, store: CatalogStore) -> dict:
    source = {
        "document_id": SAMPLE["document_id"],
        "primary_source_id": SAMPLE["source_id"],
        "source_sha256": SAMPLE["source_sha256"],
        "as_of_date": SAMPLE["published_date"],
    }
    artifacts = [
        dict(row)
        for row in store.fetchall(
            "SELECT artifact_id,artifact_role,source_id,path,content_sha256,byte_size,"
            "mime_type,generator_name,generator_version,status,error,schema_version,"
            "source_sha256,created_at FROM artifacts WHERE document_id=? "
            "ORDER BY artifact_role,created_at,artifact_id",
            (SAMPLE["document_id"],),
        )
    ]
    bundle = build_source_bundle(
        source=source,
        artifacts=artifacts,
        registry=GENERATOR_REGISTRY,
        allowed_roots=tuple(root.path for root in config.roots)
        + (config.derived_dir,),
        now=utc_now(),
    )
    as_dict = bundle.to_dict()
    # Cross-check every valid handle against the validator, computed here with
    # the artifact row and the on-disk bytes only.
    handle_checks = {}
    for role, handle in as_dict["valid_handles"].items():
        path = Path(handle["path"])
        handle_checks[role] = {
            "path_exists": path.is_file(),
            "sha256_recomputed": sha256_file(path) if path.is_file() else None,
            "sha256_matches_handle": bool(
                path.is_file() and sha256_file(path) == handle["content_sha256"]
            ),
        }
    return {
        "valid_roles": sorted(as_dict["valid_handles"]),
        "invalid_roles": sorted(as_dict["invalid"]),
        "absent_roles": sorted(
            set(GENERATOR_REGISTRY_ROLES) - set(as_dict["valid_handles"])
            - set(as_dict["invalid"])
        ),
        "invalid_reasons": {
            role: entry["reason"] for role, entry in as_dict["invalid"].items()
        },
        "bundle_hash": as_dict["bundle_hash"],
        "handle_checks": handle_checks,
        "artifact_rows": [
            {
                "artifact_role": row["artifact_role"],
                "generator_name": row["generator_name"],
                "status": row["status"],
                "schema_version": row["schema_version"],
            }
            for row in artifacts
        ],
    }


def validator_verdict(config: CatalogConfig, store: CatalogStore) -> dict:
    """What validate_artifact says about the sections row, computed here."""
    row = raw_rows(config.database_path)
    if len(row) != 1:
        return {"error": f"expected 1 sections row, found {len(row)}"}
    artifact = dict(row[0])
    metadata = json.loads(artifact["metadata_json"] or "{}")
    artifact["schema_version"] = metadata.get("schema_version")
    handle = validate_artifact(
        artifact,
        source={
            "document_id": SAMPLE["document_id"],
            "primary_source_id": SAMPLE["source_id"],
            "source_sha256": SAMPLE["source_sha256"],
            "as_of_date": SAMPLE["published_date"],
        },
        registry=GENERATOR_REGISTRY,
        allowed_roots=tuple(root.path for root in config.roots)
        + (config.derived_dir,),
        now=utc_now(),
    )
    return {"reusable": handle.reusable, "reason": handle.reason}


# --------------------------------------------------------------------------
# the value-replacement mutation (item 5 of the audit attack list)
# --------------------------------------------------------------------------


def swap_sections_index_hash(config: CatalogConfig, new_bytes: bytes) -> dict:
    """Replace the sections index bytes AND update the row hash consistently.

    This is the "rewrite the value, keep the binding consistent" attack: every
    status/schema/source/hash/path gate still passes, so only a content check
    (index bytes vs. the section files and evidence spans they claim) can
    catch it.
    """
    rows = raw_rows(config.database_path)
    index_path = Path(rows[0]["path"])
    original = index_path.read_bytes()
    original_entries = json.loads(original.decode("utf-8"))
    index_path.write_bytes(new_bytes)
    new_sha = hashlib.sha256(new_bytes).hexdigest()
    new_entries = json.loads(new_bytes.decode("utf-8"))
    # r3: the row metadata is kept CONSISTENT with the new index, so the
    # F-I05A-01 reconciliation is not what refuses the case - the intended
    # gate (span ownership) is.
    raw_exec(
        config.database_path,
        "UPDATE artifacts SET content_sha256=?, byte_size=?, metadata_json=? "
        "WHERE artifact_role='sections'",
        (
            new_sha,
            len(new_bytes),
            canonical_json(
                {"schema_version": "1.0", "sections": new_entries,
                 "count": len(new_entries)}
            ),
        ),
    )
    return {
        "attack": "consistent value replacement",
        "old_index_sha256": hashlib.sha256(original).hexdigest(),
        "new_index_sha256": new_sha,
        "row_hash_updated": True,
        "metadata_kept_consistent": True,
        "old_entry_count": len(original_entries),
        "new_entry_count": len(new_entries),
        "old_span_ids": [
            list(entry.get("span_ids") or []) for entry in original_entries
        ],
        "new_span_ids": [
            list(entry.get("span_ids") or [])
            for entry in json.loads(new_bytes.decode("utf-8"))
        ],
    }


def tampered_index_with_foreign_span(config: CatalogConfig) -> dict:
    entries = json.loads(
        Path(raw_rows(config.database_path)[0]["path"]).read_text(encoding="utf-8")
    )
    for entry in entries:
        entry["span_ids"] = ["span-not-in-catalog"]
    return swap_sections_index_hash(
        config, json.dumps(entries, ensure_ascii=False, indent=2).encode("utf-8")
    )


# --------------------------------------------------------------------------
# cases
# --------------------------------------------------------------------------


def case_matrix() -> dict:
    results = {}
    verdicts = {}

    # V0: untouched default producer output.
    built = build_catalog(SCRATCH / "c0")
    config = built["config"]
    store = built["store"]
    facts = independent_index_facts(config)
    result = query_once(config.database_path)
    verdict = classify(result, EXPECT_REASON["c0"])
    roles = sorted({entry["role"] for entry in result.get("sections", [])})
    titles = [entry["title"] for entry in result.get("sections", [])]
    order_ok = titles == EXPECT_TITLES
    verdict["roles_ok"] = roles == EXPECT_ROLES
    verdict["titles_ok"] = order_ok
    verdict["count_ok"] = result.get("count") == EXPECT_SECTION_COUNT
    verdict["index_hash_ok"] = facts.get("index_sha256_matches_row") is True
    verdict["span_ids_all_present"] = all(
        item["span_ids_all_present"] for item in facts.get("section_files", [])
    )
    if not (
        verdict["verdict"] == "PASS"
        and verdict["roles_ok"]
        and verdict["titles_ok"]
        and verdict["count_ok"]
        and verdict["index_hash_ok"]
        and verdict["span_ids_all_present"]
    ):
        verdict["verdict"] = "counterexample"
    results["c0"] = {
        "expectation": "usable; roles/titles/count as frozen; index hash == row hash",
        "returned": result,
        "independent": facts,
        "check": verdict,
    }
    verdicts["c0"] = verdict

    # published reports
    sections_report = built["sections_report"]
    summary_report = built["summary_report"]
    results["c0"]["producer_reports"] = {
        "extract_sections": {
            "operation": sections_report.operation,
            "completed": sections_report.completed,
            "skipped": sections_report.skipped,
            "failed": sections_report.failed,
            "eligible": sections_report.eligible,
        },
        "summarize": {
            "operation": summary_report.operation,
            "completed": summary_report.completed,
            "skipped": summary_report.skipped,
            "partial": summary_report.partial,
            "failed": summary_report.failed,
        },
    }
    results["c0"]["bundle"] = bundle_facts(config, store)

    # V1..V8: one mutation each, on a fresh catalog.
    def fresh_case(name: str) -> tuple[dict, dict]:
        built = build_catalog(SCRATCH / name)
        return built, independent_index_facts(built["config"])

    # V1 status=failed
    built, _ = fresh_case("c1")
    raw_exec(
        built["config"].database_path,
        "UPDATE artifacts SET status='failed' WHERE artifact_role='sections'",
    )
    result = query_once(built["config"].database_path)
    results["c1"] = {
        "mutation": "UPDATE artifacts SET status='failed' WHERE artifact_role='sections'",
        "mutation_verified": raw_rows(built["config"].database_path)[0]["status"],
        "returned": result,
        "check": classify(result, EXPECT_REASON["c1"]),
    }
    verdicts["c1"] = results["c1"]["check"]

    # V2 schema_version missing
    built, _ = fresh_case("c2")
    rows = raw_rows(built["config"].database_path)
    meta = json.loads(rows[0]["metadata_json"]); meta.pop("schema_version", None)
    raw_exec(
        built["config"].database_path,
        "UPDATE artifacts SET metadata_json=?, schema_version=NULL "
        "WHERE artifact_role='sections'",
        (canonical_json(meta),),
    )
    result = query_once(built["config"].database_path)
    results["c2"] = {
        "mutation": "drop schema_version from the sections row (column NULL + metadata)",
        "mutation_verified": raw_rows(built["config"].database_path)[0]["schema_version"],
        "returned": result,
        "check": classify(result, EXPECT_REASON["c2"]),
    }
    verdicts["c2"] = results["c2"]["check"]

    # V3 source_sha mismatch (artifact derived from other bytes)
    built, _ = fresh_case("c3")
    raw_exec(
        built["config"].database_path,
        "UPDATE artifacts SET source_sha256=? WHERE artifact_role='sections'",
        ("0" * 64,),
    )
    result = query_once(built["config"].database_path)
    results["c3"] = {
        "mutation": "UPDATE artifacts SET source_sha256='0'*64",
        "mutation_verified": raw_rows(built["config"].database_path)[0]["source_sha256"],
        "returned": result,
        "check": classify(result, EXPECT_REASON["c3"]),
    }
    verdicts["c3"] = results["c3"]["check"]

    # V4 index file deleted from disk (row untouched)
    built, _ = fresh_case("c4")
    index_path = Path(raw_rows(built["config"].database_path)[0]["path"])
    index_path.unlink()
    result = query_once(built["config"].database_path)
    results["c4"] = {
        "mutation": "delete the sections index.json from disk (row untouched)",
        "mutation_verified": {"index_exists": index_path.is_file()},
        "returned": result,
        "check": classify(result, EXPECT_REASON["c4"]),
    }
    verdicts["c4"] = results["c4"]["check"]

    # V5 index bytes tampered but the hash stays "valid" only if it is not
    # recomputed: the row hash is NOT updated, so this is the cheap tamper.
    built, _ = fresh_case("c5")
    index_path = Path(raw_rows(built["config"].database_path)[0]["path"])
    entries = json.loads(index_path.read_text(encoding="utf-8"))
    entries[0]["title"] = "TAMPERED"
    index_path.write_text(
        json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8", newline="\n"
    )
    result = query_once(built["config"].database_path)
    results["c5"] = {
        "mutation": "rewrite index.json content without updating the row hash",
        "mutation_verified": {
            "index_sha_now": sha256_file(index_path),
            "row_sha": raw_rows(built["config"].database_path)[0]["content_sha256"],
        },
        "returned": result,
        "check": classify(result, EXPECT_REASON["c5"]),
    }
    verdicts["c5"] = results["c5"]["check"]

    # V6 created_at in the future
    built, _ = fresh_case("c6")
    raw_exec(
        built["config"].database_path,
        "UPDATE artifacts SET created_at='2099-01-01T00:00:00Z' "
        "WHERE artifact_role='sections'",
    )
    result = query_once(built["config"].database_path)
    results["c6"] = {
        "mutation": "UPDATE artifacts SET created_at='2099-01-01T00:00:00Z'",
        "mutation_verified": raw_rows(built["config"].database_path)[0]["created_at"],
        "returned": result,
        "check": classify(result, EXPECT_REASON["c6"]),
    }
    verdicts["c6"] = results["c6"]["check"]

    # V7 index rewritten consistently but claiming a span that does not exist.
    built, _ = fresh_case("c7")
    attack = tampered_index_with_foreign_span(built["config"])
    result = query_once(built["config"].database_path)
    results["c7"] = {
        "mutation": "replace the index with span_ids=['span-not-in-catalog'] and "
        "update the row hash so every validator gate still passes",
        "mutation_verified": attack,
        "validator": validator_verdict(built["config"], built["store"]),
        "returned": result,
        "check": classify(result, EXPECT_REASON["c7"]),
    }
    verdicts["c7"] = results["c7"]["check"]

    # V8 the span row was pruned: index still names it, catalog no longer has it.
    built, _ = fresh_case("c8")
    raw_exec(
        built["config"].database_path,
        "DELETE FROM evidence_spans WHERE document_id=?",
        (SAMPLE["document_id"],),
    )
    result = query_once(built["config"].database_path)
    results["c8"] = {
        "mutation": "DELETE FROM evidence_spans (index still names the spans)",
        "mutation_verified": {
            "span_rows_left": built["store"].fetchone(
                "SELECT count(*) AS n FROM evidence_spans"
            )["n"]
        },
        "returned": result,
        "check": classify(result, EXPECT_REASON["c8"]),
    }
    verdicts["c8"] = results["c8"]["check"]

    return {"cases": results, "verdicts": verdicts}


def _recompute_case(
    name: str,
    *,
    generator_version: str,
    status: str,
    created_at: str,
    index_source: Path | None = None,
) -> dict:
    """One "existing sections row vs. recompute eligibility" sub-case.

    n2a: a FAILED row is the only sections row -> the producer must not treat
         it as "already done".
    n2b: a COMPLETED row from an OLDER generator version is the only sections
         row -> this producer's own output version does not exist yet, so it
         must not be treated as "already done" either.
    n2c: control - a COMPLETED row at THIS generator version must keep being
         skipped (no needless rewrite), and the consumer must still be able to
         read what that row points at.

    ``index_source`` (n2c only) supplies a REAL producer-written index.json so
    the control case is a fully usable artifact rather than a fabricated
    broken row.
    """
    built = seed_catalog_only(SCRATCH / name)
    config = built["config"]
    if index_source is not None:
        # Re-home the reference index INSIDE this case's own catalog: after
        # F-I05A-04 every entry path is containment-checked against THIS
        # catalog's derived root, so a control row pointing at another case's
        # tree would be (correctly) refused.
        reference_entries = json.loads(index_source.read_text(encoding="utf-8"))
        target_dir = config.derived_dir / "control"
        target_dir.mkdir(parents=True, exist_ok=True)
        entries = []
        for entry in reference_entries:
            source_slice = Path(entry["path"])
            target_slice = target_dir / source_slice.name
            shutil.copyfile(source_slice, target_slice)
            relocated = dict(entry)
            relocated["path"] = str(target_slice)
            entries.append(relocated)
        index_path = target_dir / "index.json"
        index_path.write_text(
            json.dumps(entries, ensure_ascii=False, indent=2),
            encoding="utf-8",
            newline="\n",
        )
        metadata = {
            "schema_version": "1.0",
            "sections": entries,
            "count": len(entries),
        }
        content_sha = hashlib.sha256(index_path.read_bytes()).hexdigest()
        byte_size = index_path.stat().st_size
    else:
        index_path = None
        metadata = {"schema_version": "1.0", "sections": [], "count": 0}
        content_sha = "1" * 64
        byte_size = 10
    raw_exec(
        config.database_path,
        "INSERT INTO artifacts(artifact_id,document_id,source_id,artifact_role,path,"
        "content_sha256,byte_size,mime_type,generator_name,generator_version,status,"
        "error,schema_version,source_sha256,metadata_json,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            f"urn:cw:artifact:sha256:seed-{name}",
            SAMPLE["document_id"],
            SAMPLE["source_id"],
            "sections",
            str(index_path or (Path(config.derived_dir) / "stale" / "index.json")),
            content_sha,
            byte_size,
            "application/json",
            SECTION_EXTRACTOR_NAME,
            generator_version,
            status,
            None if status == "completed" else "previous attempt failed",
            "1.0",
            SAMPLE["source_sha256"],
            canonical_json(metadata),
            created_at,
        ),
    )
    before_rows = raw_rows(config.database_path)
    report = extract_sections_catalog(config, built["store"])
    after_rows = raw_rows(config.database_path)
    result = query_once(config.database_path)
    return {
        "case": name,
        "seed": {
            "generator_version": generator_version,
            "status": status,
            "created_at": created_at,
            "index_source": str(index_source) if index_source else None,
        },
        "independent": {
            "rows_before": [
                {"generator_version": r["generator_version"], "status": r["status"]}
                for r in before_rows
            ],
            "rows_after": [
                {"generator_version": r["generator_version"], "status": r["status"]}
                for r in after_rows
            ],
            "completed_rows_for_current_version": sum(
                1
                for r in after_rows
                if r["status"] == "completed"
                and r["generator_version"] == SECTION_EXTRACTOR_VERSION
            ),
        },
        "producer_report": {
            "completed": report.completed,
            "skipped": report.skipped,
            "failed": report.failed,
            "eligible": report.eligible,
        },
        "returned": result,
        "check": None,
    }


def case_stale_failed_row(control_index: Path, producer_row: dict) -> dict:
    """W05A-N2: old failed/stale sections rows must not block the recompute.

    ``control_index`` is the index.json the c0 (untouched producer) case
    wrote; the n2c control row points at those exact bytes so it is a real,
    usable artifact rather than a fabricated broken one.
    """
    n2a = _recompute_case(
        "n2a", generator_version="0.9.0", status="failed",
        created_at="2020-01-01T00:00:00Z",
    )
    n2a["check"] = {
        "expectation": (
            "a FAILED sections row is not 'already done': the producer must "
            "recompute (completed>=1) and the consumer MUST then serve the "
            "fresh COMPLETED row (the failed row never becomes the served one)"
        ),
        "producer_completed": n2a["producer_report"]["completed"],
        "consumer_returned_usable": n2a["returned"].get("outcome") == "returned",
        "fresh_completed_row_exists": (
            n2a["independent"]["completed_rows_for_current_version"] >= 1
        ),
        "served_title": [
            entry.get("title") for entry in n2a["returned"].get("sections", [])
        ],
    }
    n2a["check"]["verdict"] = (
        "PASS"
        if (
            n2a["check"]["producer_completed"] >= 1
            and n2a["check"]["consumer_returned_usable"]
            and n2a["check"]["fresh_completed_row_exists"]
            and n2a["check"]["served_title"] == EXPECT_TITLES
        )
        else "counterexample"
    )

    n2b = _recompute_case(
        "n2b", generator_version="0.9.0", status="completed",
        created_at="2020-01-01T00:00:00Z",
    )
    n2b["check"] = {
        "expectation": (
            "OBSERVATION (card W05A-N3-adjacent, frozen as a NON-requirement "
            "for this attempt): a COMPLETED row from an OLDER generator version "
            "still counts as 'already done' for the recompute filter. The "
            "no-version rule is the deliberate scope of the minimal fix (see "
            "decision.md OPEN-1 / the scope note in section_extractor.py); this "
            "case records the resulting state instead of pretending it was "
            "fixed. It is NOT scored as pass/fail."
        ),
        "producer_completed": n2b["producer_report"]["completed"],
        "fresh_completed_row_exists": (
            n2b["independent"]["completed_rows_for_current_version"] >= 1
        ),
        "consumer_outcome": n2b["returned"].get("outcome"),
        "verdict": "observation",
    }

    n2c = _recompute_case(
        "n2c", generator_version=producer_row["generator_version"],
        status="completed",
        created_at="2026-01-01T00:00:00Z",
        index_source=control_index,
    )
    n2c["check"] = {
        "expectation": (
            "control: a COMPLETED row at the version the producer actually "
            "writes keeps being skipped (completed==0, no needless rewrite) "
            "and the consumer still reads what that row points at"
        ),
        "seeded_generator_version": producer_row["generator_version"],
        "producer_completed": n2c["producer_report"]["completed"],
        "consumer_returned_usable": n2c["returned"].get("outcome") == "returned",
        "served_titles": [
            entry.get("title") for entry in n2c["returned"].get("sections", [])
        ],
    }
    n2c["check"]["verdict"] = (
        "PASS"
        if (
            n2c["check"]["producer_completed"] == 0
            and n2c["check"]["consumer_returned_usable"]
            and n2c["check"]["served_titles"] == EXPECT_TITLES
        )
        else "counterexample"
    )

    return {"case": "n2", "subcases": {"n2a": n2a, "n2b": n2b, "n2c": n2c}}


def case_summary_not_forced() -> dict:
    """P2: no summary exists -> the bundle must not fake one and sections
    must stay consumable on its own."""
    built = build_catalog(SCRATCH / "p2")
    config = built["config"]
    store = built["store"]
    # remove the extractive summary artifact the producer created: the "this
    # document has no summary" state (raw-only / not applicable)
    row = store.fetchone(
        "SELECT path FROM artifacts WHERE artifact_role='summary' LIMIT 1"
    )
    removed_path = row["path"] if row is not None else None
    raw_exec(
        config.database_path,
        "DELETE FROM artifacts WHERE artifact_role='summary'",
    )
    facts = bundle_facts(config, store)
    result = query_once(config.database_path)
    check = {
        "expectation": (
            "sections stays usable; a role with NO artifact row is simply "
            "absent (never a fabricated summary, never silently 'valid'); "
            "the absent roles must be visible to the consumer; no LLM "
            "client is constructed"
        ),
        "summary_removed_path": removed_path,
        "summary_in_valid": "summary" in facts["valid_roles"],
        "summary_in_invalid": "summary" in facts["invalid_roles"],
        "summary_reason": facts["invalid_reasons"].get("summary"),
        "roles_with_no_artifact_row": facts["absent_roles"],
        "markdown_not_required": "markdown" not in facts["valid_roles"],
        "sections_usable": result.get("outcome") == "returned",
        "llm_clients_constructed": 0,
    }
    check["verdict"] = (
        "PASS"
        if (
            check["sections_usable"]
            and not check["summary_in_valid"]
            and not check["summary_in_invalid"]
            and check["roles_with_no_artifact_row"] == EXPECT_ABSENT_ROLES
            and check["markdown_not_required"]
        )
        else "counterexample"
    )
    return {
        "case": "p2",
        "bundle": facts,
        "returned_keys": sorted(result.keys()),
        "returned_outcome": result.get("outcome"),
        "check": check,
    }


def case_all_failed_row() -> dict:
    """N3-observation: two sections rows for one role -- which one is served?

    The store's UNIQUE(document_id, artifact_role, generator_name,
    generator_version) allows an older row under a different generator
    version to coexist with the current one.  This case records, without
    judging, which row the query picks and whether the pick is justified by
    a version/source/status rule.
    """
    built = build_catalog(SCRATCH / "n3")
    config = built["config"]
    document_id = SAMPLE["document_id"]
    current = raw_rows(config.database_path)[0]
    # old row inserted FIRST under an older generator version, and it is
    # perfectly qualified on every non-version gate
    raw_exec(
        config.database_path,
        "INSERT INTO artifacts(artifact_id,document_id,source_id,artifact_role,path,"
        "content_sha256,byte_size,mime_type,generator_name,generator_version,status,"
        "error,schema_version,source_sha256,metadata_json,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "urn:cw:artifact:sha256:old-sections",
            document_id,
            SAMPLE["source_id"],
            "sections",
            current["path"],
            current["content_sha256"],
            len(Path(current["path"]).read_bytes()),
            "application/json",
            SECTION_EXTRACTOR_NAME,
            "0.9.0",
            "completed",
            None,
            "1.0",
            SAMPLE["source_sha256"],
            canonical_json(
                {
                    "schema_version": "1.0",
                    "sections": [
                        {
                            "role": "mda",
                            "title": "STALE-OLD-VERSION",
                            "ordinal": "",
                            "char_start": 0,
                            "char_end": 1,
                            "path": current["path"],
                            "page_start": None,
                            "page_end": None,
                            "span_ids": [],
                        }
                    ],
                    "count": 1,
                }
            ),
            "2020-01-01T00:00:00Z",
        ),
    )
    rows = raw_rows(config.database_path)
    result = query_once(config.database_path)
    served_index = result.get("index_path")
    check = {
        "rows": len(rows),
        "returned_index_matches_current_row": bool(
            served_index and Path(served_index) == Path(current["path"])
        ),
        "returned_titles": [
            entry.get("title") for entry in result.get("sections", [])
        ] if result.get("outcome") == "returned" else None,
        "expectation": (
            "the served row must be chosen by an explicit newest/valid rule, "
            "never by unordered SQLite row order; the stale older row's "
            "content (title STALE-OLD-VERSION) must never be served"
        ),
    }
    # The older row and the current row share path/content_sha256, so the two
    # are distinguished ONLY by the metadata the query reads: serving the
    # STALE-OLD-VERSION title is the observable failure.
    check["stale_title_served"] = bool(
        check["returned_titles"] and "STALE-OLD-VERSION" in check["returned_titles"]
    )
    check["verdict"] = (
        "PASS"
        if (
            result.get("outcome") == "returned"
            and not check["stale_title_served"]
            and check["returned_titles"] == EXPECT_TITLES
        )
        else "counterexample"
    )
    return {
        "case": "n3",
        "independent": {
            "row_pairs": [
                {"generator_version": r["generator_version"], "created_at": r["created_at"]}
                for r in rows
            ],
        },
        "returned": result,
        "check": check,
    }


def main() -> int:
    tag = sys.argv[1] if len(sys.argv) > 1 else "before"
    out_dir = ATTEMPT / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)

    matrix = case_matrix()
    control_index = next(
        (SCRATCH / "c0" / "catalog" / "derived").glob("*/*/sections/index.json")
    )
    producer_row = next(
        iter(
            raw_rows(SCRATCH / "c0" / "catalog" / "catalog.sqlite3")
        )
    )
    stale = case_stale_failed_row(control_index, producer_row)
    summary = case_summary_not_forced()
    two_versions = case_all_failed_row()

    section_index_span_checks = {
        "V0": matrix["cases"]["c0"]["independent"],
        "V0_query_entries": matrix["cases"]["c0"]["returned"].get(
            "sections"
        ),
        "V7_validator": matrix["cases"]["c7"]["validator"],
        "V7_mutation": matrix["cases"]["c7"]["mutation_verified"],
    }
    mutation_matrix = {
        case: {
            "expectation": data.get("expectation")
            or EXPECT_REASON.get(case, "(pass)"),
            "mutation": data.get("mutation"),
            "mutation_verified": data.get("mutation_verified"),
            "outcome": data["returned"].get("outcome"),
            "reason_reported": data["check"].get("reason_reported"),
            "expected_reason": EXPECT_REASON.get(case),
            "verdict": data["check"]["verdict"],
        }
        for case, data in matrix["cases"].items()
    }

    (out_dir / "case_results.json").write_text(
        json.dumps(
            {
                "tag": tag,
                "section_query_source": str(SECTION_QUERY_PATH),
                "section_query_source_sha256": sha256_file(SECTION_QUERY_PATH),
                "cases": matrix["cases"],
                "verdicts": matrix["verdicts"],
                "n2": stale,
                "p2": summary,
                "n3": two_versions,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (out_dir / "artifact-mutation-matrix.json").write_text(
        json.dumps(mutation_matrix, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (out_dir / "section-index-span-checks.json").write_text(
        json.dumps(section_index_span_checks, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (out_dir / "default-producer-artifacts.json").write_text(
        json.dumps(
            {
                "V0_producer_reports": matrix["cases"]["c0"][
                    "producer_reports"
                ],
                "V0_bundle": matrix["cases"]["c0"]["bundle"],
                "V0_row": matrix["cases"]["c0"]["independent"].get("row"),
                "N2_subcases": {
                    key: {
                        "producer_report": value["producer_report"],
                        "rows_after": value["independent"]["rows_after"],
                        "verdict": value["check"]["verdict"],
                    }
                    for key, value in stale["subcases"].items()
                },
                "P2_bundle": summary["bundle"],
                "N3_rows": two_versions["independent"]["row_pairs"],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "tag": tag,
                "verdicts": matrix["verdicts"],
                "N2": {
                    key: value["check"]["verdict"]
                    for key, value in stale["subcases"].items()
                },
                "P2": summary["check"]["verdict"],
                "N3": two_versions["check"],
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
