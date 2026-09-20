"""W05A review-attack probes: reproduce the reviewer's F-I05A-01/02/03 bypasses.

Each probe builds a REAL producer catalog (reusing scripts/w05a_cases.build_catalog
is not possible here because that module runs its own matrix), so this file
constructs the catalog through the same helpers by importing them.

  <py> -X utf8 -B scripts/w05a_attack_probes.py <tag>
"""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ATTEMPT = HERE.parent
SAMPLES = ATTEMPT / "samples"
SCRATCH = Path(
    os.environ.get("W05A_SCRATCH", r"C:\Users\郑曾波\AppData\Local\Temp\w05a")
) / "a20260919-01"
sys.path.insert(0, str(HERE))

import w05a_cases as H  # noqa: E402

QUERY_PATH = Path(os.environ["W05A_CW_SRC"]) / "company_wiki" / "source_catalog" / "section_query.py"
sys.path.insert(0, str(Path(os.environ["W05A_CW_SRC"])))
from company_wiki.source_catalog.section_query import SectionQueryService  # noqa: E402
from company_wiki.source_catalog.section_query import SectionQueryError  # noqa: E402


def query(db: Path) -> dict:
    try:
        result = SectionQueryService(db).list_sections(
            document_id=H.SAMPLE["document_id"]
        )
    except SectionQueryError as exc:
        return {"outcome": "error", "error_type": type(exc).__name__, "message": str(exc)}
    except Exception as exc:  # noqa: BLE001
        return {"outcome": "unexpected_error", "type": type(exc).__name__, "message": str(exc)}
    return {"outcome": "returned", **result.to_dict()}


def artifact_row(db: Path) -> dict:
    connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            "SELECT artifact_id, path, content_sha256, metadata_json, status, "
            "generator_version, source_sha256 FROM artifacts "
            "WHERE artifact_role='sections'"
        ).fetchone()
    finally:
        connection.close()
    return dict(row) if row is not None else {}


def probe_m1_metadata_injection() -> dict:
    """F-I05A-01: rewrite ONLY metadata_json; index bytes and row hash intact."""
    built = H.build_catalog(SCRATCH / "m1")
    config = built["config"]
    db = config.database_path
    before = artifact_row(db)
    index_path = Path(before["path"])
    index_bytes = index_path.read_bytes()
    row_hash = before["content_sha256"]

    poison = SCRATCH / "m1_poison.md"
    poison.write_text("POISONED-CONTENT-FROM-OUTSIDE-THE-CATALOG\n", encoding="utf-8")
    entries = json.loads(index_bytes.decode("utf-8"))
    injected = [
        {
            "role": "mda",
            "title": "INJECTED-TITLE",
            "ordinal": "",
            "char_start": 0,
            "char_end": len(poison.read_text(encoding="utf-8")),
            "path": str(poison),
            "page_start": None,
            "page_end": None,
            "span_ids": [],
        }
    ]
    H.raw_exec(
        db,
        "UPDATE artifacts SET metadata_json=? WHERE artifact_role='sections'",
        (H.canonical_json({"schema_version": "1.0", "sections": injected, "count": 1}),),
    )
    after = artifact_row(db)
    result = query(db)
    served = None
    if result.get("outcome") == "returned":
        served = [
            {
                "title": entry["title"],
                "path": entry["path"],
                "char_start": entry["char_start"],
                "char_end": entry["char_end"],
                "file_reads_outside_catalog": not str(entry["path"]).startswith(
                    str(config.catalog_dir)
                ),
            }
            for entry in result.get("sections", [])
        ]
    return {
        "probe": "m1_metadata_json_injection",
        "mutation": "UPDATE artifacts SET metadata_json=<entries pointing outside the catalog>",
        "index_bytes_untouched": index_path.read_bytes() == index_bytes,
        "row_hash_untouched": after["content_sha256"] == row_hash,
        "index_sha256_still_matches_row": hashlib.sha256(index_path.read_bytes()).hexdigest()
        == after["content_sha256"],
        "outcome": result.get("outcome"),
        "reason": result.get("message"),
        "served_entries": served,
        "expectation": "must refuse (the index that was validated must be the index that is served)",
    }


def probe_m2_length_preserving_slice() -> dict:
    """F-I05A-02: replace a slice with equal-length different text."""
    built = H.build_catalog(SCRATCH / "m2")
    config = built["config"]
    db = config.database_path
    entries = json.loads(
        Path(artifact_row(db)["path"]).read_text(encoding="utf-8")
    )
    entry = entries[0]
    slice_path = Path(entry["path"])
    original = slice_path.read_text(encoding="utf-8")
    replacement = "Z" * len(original)
    slice_path.write_text(replacement, encoding="utf-8", newline="\n")
    result = query(db)
    return {
        "probe": "m2_length_preserving_slice_replacement",
        "mutation": f"overwrite {slice_path.name} with {len(original)} 'Z' characters",
        "original_length": len(original),
        "replacement_length": len(replacement),
        "index_row_hash_untouched": True,
        "outcome": result.get("outcome"),
        "reason": result.get("message"),
        "served_first_title": (
            result["sections"][0]["title"] if result.get("outcome") == "returned" else None
        ),
        "expectation": "must refuse: the slice bytes are not bound to the source window",
    }


def probe_m3_entry_path_containment() -> dict:
    """F-I05A-03: index entry path outside the catalog, row hash updated."""
    built = H.build_catalog(SCRATCH / "m3")
    config = built["config"]
    db = config.database_path
    outside_dir = SCRATCH / "outside_catalog"
    outside_dir.mkdir(parents=True, exist_ok=True)
    entries = json.loads(
        Path(artifact_row(db)["path"]).read_text(encoding="utf-8")
    )
    served_paths = []
    for entry in entries:
        # byte-for-byte copy with the SAME BASENAME, so the slice keeps its
        # length AND name; the only change is that it now lives outside the
        # catalog.  A length check therefore cannot be what refuses it.
        target = outside_dir / Path(entry["path"]).name
        shutil.copyfile(Path(entry["path"]), target)
        entry["path"] = str(target)
        served_paths.append(str(target))
    index_path = Path(artifact_row(db)["path"])
    new_bytes = json.dumps(entries, ensure_ascii=False, indent=2).encode("utf-8")
    index_path.write_bytes(new_bytes)
    H.raw_exec(
        db,
        "UPDATE artifacts SET content_sha256=?, byte_size=? WHERE artifact_role='sections'",
        (hashlib.sha256(new_bytes).hexdigest(), len(new_bytes)),
    )
    result = query(db)
    served_paths = []
    reads_outside = False
    if result.get("outcome") == "returned":
        for entry in result["sections"]:
            served_paths.append(str(entry["path"]))
            if not str(Path(entry["path"]).resolve()).startswith(
                str(config.catalog_dir.resolve())
            ):
                reads_outside = True
    return {
        "probe": "m3_entry_path_outside_catalog",
        "mutation": "point every index entry path at a byte-identical copy outside the "
        "catalog and update the row hash so every validator gate passes",
        "row_hash_updated": True,
        "outcome": result.get("outcome"),
        "reason": result.get("message"),
        "served_paths": served_paths,
        "served_paths_outside_catalog": reads_outside,
        "expectation": "must refuse (entry paths get the same containment gate)",
    }


def probe_m5_version_deadlock() -> dict:
    """F-I05A-05: a sole 0.9.0/completed row deadlocks producer and consumer."""
    built = H.seed_catalog_only(SCRATCH / "m5")
    config = built["config"]
    db = config.database_path
    real_index = Path(
        H.build_catalog(SCRATCH / "m5_ref")["config"].database_path
    )
    ref_row = raw_sections_row(real_index)
    H.raw_exec(
        db,
        "INSERT INTO artifacts(artifact_id,document_id,source_id,artifact_role,path,"
        "content_sha256,byte_size,mime_type,generator_name,generator_version,status,"
        "error,schema_version,source_sha256,metadata_json,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "urn:cw:artifact:sha256:old-090",
            H.SAMPLE["document_id"],
            H.SAMPLE["source_id"],
            "sections",
            ref_row["path"],
            ref_row["content_sha256"],
            Path(ref_row["path"]).stat().st_size,
            "application/json",
            "source_catalog_section_extractor",
            "0.9.0",
            "completed",
            None,
            "1.0",
            H.SAMPLE["source_sha256"],
            ref_row["metadata_json"],
            "2020-01-01T00:00:00Z",
        ),
    )
    from company_wiki.source_catalog.section_extractor import (
        extract_sections_catalog,
    )

    report = extract_sections_catalog(config, built["store"])
    result = query(db)
    return {
        "probe": "m5_old_version_deadlock",
        "state": "the only sections row is 0.9.0/completed",
        "producer_completed": report.completed,
        "producer_eligible": report.eligible,
        "consumer_outcome": result.get("outcome"),
        "consumer_reason": result.get("message"),
        "expectation": "the recompute filter and the qualification gate must agree on "
        "which generator versions count, otherwise the pipeline deadlocks",
    }


def probe_m6_newest_invalid_shadowing() -> dict:
    """F-I05A-06: the newest row is failed while an older row is qualified."""
    built = H.build_catalog(SCRATCH / "m6")
    config = built["config"]
    db = config.database_path
    rows = H.raw_rows(db)
    current = rows[0]
    H.raw_exec(
        db,
        "INSERT INTO artifacts(artifact_id,document_id,source_id,artifact_role,path,"
        "content_sha256,byte_size,mime_type,generator_name,generator_version,status,"
        "error,schema_version,source_sha256,metadata_json,created_at) "
        "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (
            "urn:cw:artifact:sha256:newer-failed",
            H.SAMPLE["document_id"],
            H.SAMPLE["source_id"],
            "sections",
            current["path"],
            current["content_sha256"],
            Path(current["path"]).stat().st_size,
            "application/json",
            "source_catalog_section_extractor",
            "1.0.1",
            "failed",
            "newest attempt failed",
            "1.0",
            H.SAMPLE["source_sha256"],
            current["metadata_json"],
            "2030-01-01T00:00:00Z",
        ),
    )
    result = query(db)
    return {
        "probe": "m6_newest_invalid_shadows_older_valid",
        "state": "newer row failed (created_at 2030), older row completed and qualified",
        "outcome": result.get("outcome"),
        "reason": result.get("message"),
        "served_titles": (
            [entry["title"] for entry in result.get("sections", [])]
            if result.get("outcome") == "returned"
            else None
        ),
        "expectation": "build_source_bundle serves the newest VALID row; the query must "
        "either match that contract (serve the older usable row) or the divergence must "
        "be a signed D-W05 decision",
    }


def raw_sections_row(db: Path) -> dict:
    connection = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    try:
        row = connection.execute(
            "SELECT path, content_sha256, metadata_json FROM artifacts "
            "WHERE artifact_role='sections'"
        ).fetchone()
    finally:
        connection.close()
    return dict(row)


def _set_index(config, entries, *, update_row_hash=True):
    """Rewrite the index and (optionally) keep the row hash consistent."""
    index_path = Path(artifact_row(config.database_path)["path"])
    payload = json.dumps(entries, ensure_ascii=False, indent=2).encode("utf-8")
    index_path.write_bytes(payload)
    if update_row_hash:
        H.raw_exec(
            config.database_path,
            "UPDATE artifacts SET content_sha256=?, byte_size=?, metadata_json=? "
            "WHERE artifact_role='sections'",
            (
                hashlib.sha256(payload).hexdigest(),
                len(payload),
                H.canonical_json(
                    {"schema_version": "1.0", "sections": entries, "count": len(entries)}
                ),
            ),
        )
    return index_path


def probe_m2b_recomputed_hash() -> dict:
    """A1/P1-1: replace the slice AND recompute the index's own slice hash."""
    built = H.build_catalog(SCRATCH / "m2b")
    config = built["config"]
    entries = json.loads(
        Path(artifact_row(config.database_path)["path"]).read_text(encoding="utf-8")
    )
    entry = entries[0]
    slice_path = Path(entry["path"])
    original = slice_path.read_text(encoding="utf-8")
    replacement = "\u6539" * len(original)
    slice_path.write_text(replacement, encoding="utf-8", newline="\n")
    entry["content_sha256"] = hashlib.sha256(slice_path.read_bytes()).hexdigest()
    _set_index(config, entries)
    result = query(config.database_path)
    served = result["sections"][0]["path"] if result.get("outcome") == "returned" else None
    return {
        "probe": "m2b_slice_hash_recomputed",
        "mutation": "rewrite the slice with equal-length text AND recompute the index hash",
        "outcome": result.get("outcome"),
        "reason": result.get("message"),
        "served_first_chars": (
            Path(served).read_text(encoding="utf-8")[:6] if served else None
        ),
        "expectation": "must refuse (the slice is not a window of the document source)",
    }


def probe_m2c_hash_omitted() -> dict:
    """A1/P1-1: delete the index's slice hash keys entirely."""
    built = H.build_catalog(SCRATCH / "m2c")
    config = built["config"]
    entries = json.loads(
        Path(artifact_row(config.database_path)["path"]).read_text(encoding="utf-8")
    )
    for entry in entries:
        slice_path = Path(entry["path"])
        original = slice_path.read_text(encoding="utf-8")
        slice_path.write_text(
            "\u5220" * len(original), encoding="utf-8", newline="\n"
        )
        entry.pop("content_sha256", None)
    _set_index(config, entries)
    result = query(config.database_path)
    return {
        "probe": "m2c_hash_field_omitted",
        "mutation": "equal-length rewrite with the index content_sha256 keys removed",
        "outcome": result.get("outcome"),
        "reason": result.get("message"),
        "expectation": "must refuse (no self-recorded hash may disable the binding)",
    }


def probe_m3b_inside_catalog_outside_derived() -> dict:
    """P3-1: a file inside <catalog> but outside <catalog>/derived."""
    built = H.build_catalog(SCRATCH / "m3b")
    config = built["config"]
    planted_dir = Path(config.catalog_dir) / "planted"
    planted_dir.mkdir(parents=True, exist_ok=True)
    entries = json.loads(
        Path(artifact_row(config.database_path)["path"]).read_text(encoding="utf-8")
    )
    for entry in entries:
        target = planted_dir / Path(entry["path"]).name
        shutil.copyfile(Path(entry["path"]), target)
        entry["path"] = str(target)
    _set_index(config, entries)
    result = query(config.database_path)
    return {
        "probe": "m3b_inside_catalog_outside_derived",
        "mutation": "entry paths point at <catalog>/planted/* (inside the catalog, "
        "outside derived/), row hash updated",
        "outcome": result.get("outcome"),
        "reason": result.get("message"),
        "expectation": "must refuse: slices live under derived/",
    }


def probe_m4_outside_existing() -> dict:
    """P3-2 control: outside the roots and the file EXISTS."""
    built = H.build_catalog(SCRATCH / "m4")
    config = built["config"]
    outside_dir = SCRATCH / "outside_catalog"
    outside_dir.mkdir(parents=True, exist_ok=True)
    entries = json.loads(
        Path(artifact_row(config.database_path)["path"]).read_text(encoding="utf-8")
    )
    for entry in entries:
        target = outside_dir / Path(entry["path"]).name
        shutil.copyfile(Path(entry["path"]), target)
        entry["path"] = str(target)
    _set_index(config, entries)
    result = query(config.database_path)
    return {
        "probe": "m4_outside_existing",
        "mutation": "entry paths outside the roots pointing at files that EXIST",
        "outcome": result.get("outcome"),
        "reason": result.get("message"),
        "expectation": "containment code",
    }


def probe_m4b_outside_missing() -> dict:
    """P3-2: outside the allowed roots AND the file does not exist."""
    built = H.build_catalog(SCRATCH / "m4b")
    config = built["config"]
    missing = SCRATCH / "definitely_not_here" / "x.md"
    entries = json.loads(
        Path(artifact_row(config.database_path)["path"]).read_text(encoding="utf-8")
    )
    for entry in entries:
        entry["path"] = str(missing)
    _set_index(config, entries)
    result = query(config.database_path)
    return {
        "probe": "m4b_outside_and_missing",
        "mutation": "entry paths outside the roots pointing at a NON-existent file",
        "outcome": result.get("outcome"),
        "reason": result.get("message"),
        "expectation": "must return the containment code, never sections_file_missing "
        "(otherwise the refusal is an existence oracle)",
    }


def probe_m7_metadata_uncompared() -> dict:
    """P3-3: tamper only metadata keys the first comparison skipped."""
    built = H.build_catalog(SCRATCH / "m7")
    config = built["config"]
    row = artifact_row(config.database_path)
    meta = json.loads(row["metadata_json"])
    for entry in meta["sections"]:
        entry["ordinal"] = "TAMPERED"
        entry["page_start"] = 99
        entry["span_ids"] = ["span-does-not-exist"]
    H.raw_exec(
        config.database_path,
        "UPDATE artifacts SET metadata_json=? WHERE artifact_role='sections'",
        (H.canonical_json(meta),),
    )
    result = query(config.database_path)
    return {
        "probe": "m7_metadata_uncompared_keys",
        "mutation": "metadata ordinal/page_start/span_ids changed (index untouched)",
        "outcome": result.get("outcome"),
        "reason": result.get("message"),
        "expectation": "must refuse (metadata must not contradict the index on ANY key)",
    }


def main() -> int:
    tag = sys.argv[1] if len(sys.argv) > 1 else "before"
    out_dir = ATTEMPT / tag
    out_dir.mkdir(parents=True, exist_ok=True)
    probes = {
        "m1_metadata_json_injection": probe_m1_metadata_injection(),
        "m2_length_preserving_slice": probe_m2_length_preserving_slice(),
        "m3_entry_path_outside_catalog": probe_m3_entry_path_containment(),
        "m5_old_version_deadlock": probe_m5_version_deadlock(),
        "m6_newest_invalid_shadows_older_valid": probe_m6_newest_invalid_shadowing(),
        "m2b_slice_hash_recomputed": probe_m2b_recomputed_hash(),
        "m2c_hash_field_omitted": probe_m2c_hash_omitted(),
        "m3b_inside_catalog_outside_derived": probe_m3b_inside_catalog_outside_derived(),
        "m4_outside_existing": probe_m4_outside_existing(),
        "m4b_outside_and_missing": probe_m4b_outside_missing(),
        "m7_metadata_uncompared_keys": probe_m7_metadata_uncompared(),
    }
    payload = {
        "tag": tag,
        "section_query_source": str(QUERY_PATH),
        "section_query_source_sha256": hashlib.sha256(QUERY_PATH.read_bytes()).hexdigest(),
        "probes": probes,
    }
    (out_dir / "review-attack-probes.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(
        {
            name: {
                "outcome": probe.get("outcome") or f"completed={probe.get('producer_completed')}",
                "reason": (probe.get("reason") or probe.get("consumer_reason") or "")[:70],
            }
            for name, probe in probes.items()
        },
        ensure_ascii=False,
        indent=2,
    ))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
