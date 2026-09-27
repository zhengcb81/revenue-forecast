"""Behaviour-level probe for the normalize-side F-B10R2-MISSINGFILE fix (owner 2026-09-18).

The reviewer's finding was precise: with a document whose bytes no longer match the manifest,
`IngestService.ingest` inside the `except Exception` HANDLER raises
`SourceManifestMismatchError`, and because nothing encloses that call it escapes
`normalize_catalog` - so every document queued behind the bad row is starved, even a healthy
one.  That is a behaviour, so it gets a behaviour-level probe rather than only a unit test.

Two documents are seeded into a temp catalog, in a deterministic order:

* **doc A - the bad row.**  The file exists (so the R1 `is_file()` guard passes) but its bytes
  were REPLACED after the scan, so the manifest no longer matches; a tiny parser timeout makes
  the parse fail deterministically, which routes into the handler that ingests the empty parse
  result - the escape point.
* **doc B - the healthy row behind it.**  Manifest and bytes agree, the file is a real `.md`,
  and it must be normalized (a `normalized.md` on disk plus a `normalized` artifact row).

``WIKI_SRC`` lets the same probe run against a MUTATED COPY of the package, so the fix can be
shown to be load-bearing: pre-fix the run escapes and B is never normalized, post-fix the run
reports a per-document failure and B is normalized.

Usage::

    python barfix_normalize_probe.py [--out PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
import traceback
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "barfix-normalize-probe.json"
WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
#: Point this at a mutated copy to demonstrate the pre-fix failure (a probe that cannot fail
#: proves nothing).
WIKI_SRC = Path(os.environ.get("BARFIX_WIKI_SRC") or (WIKI / "src"))
sys.path.insert(0, str(WIKI_SRC))

from company_wiki.source_catalog.config import CatalogConfig  # noqa: E402
from company_wiki.source_catalog.models import RootSpec  # noqa: E402
from company_wiki.source_catalog.normalizer import normalize_catalog  # noqa: E402
from company_wiki.source_catalog.store import CatalogStore  # noqa: E402
from company_wiki.source_contract.source_manifest import source_id_for_sha256  # noqa: E402

ROOT = "urn:company-wiki:root:sha256:" + "r" * 64
BAD_BODY = b"# Bad Filing\n\nthis body is replaced on disk after the scan\n"
BAD_REPLACEMENT = b"# Bad Filing\n\nREPLACED BYTES (manifest no longer matches)\n"
GOOD_BODY = b"# Good Filing\n\nGood Filing body text\n"
BAD_SHA = hashlib.sha256(BAD_BODY).hexdigest()
GOOD_SHA = hashlib.sha256(GOOD_BODY).hexdigest()
BAD_DOC = "urn:company-wiki:document:sha256:" + "a" * 64
GOOD_DOC = "urn:company-wiki:document:sha256:" + "b" * 64


def _manifest(source_id: str, sha: str, size: int, path: str) -> dict:
    return {
        "schema_version": "1.0.0", "source_id": source_id, "entity_ids": ["probe-issuer"],
        "original_path": path, "content_sha256": sha, "source_type": "regulatory_filing",
        "published_date": "2026-06-18", "retrieved_at": "2026-06-18T00:00:00Z",
        "collector_name": "probe", "collector_version": "1.0.0", "mime_type": "text/markdown",
        "byte_size": size, "immutable_status": "verified",
    }


def _insert(connection, table: str, values: dict) -> None:
    have = {row[1] for row in connection.execute(f"PRAGMA table_info({table})")}
    use = {key: value for key, value in values.items() if key in have}
    connection.execute(
        f"INSERT INTO {table} ({','.join(use)}) VALUES ({','.join('?' * len(use))})",
        tuple(use.values()),
    )


def _seed(tmp: Path) -> tuple[CatalogConfig, CatalogStore, Path, Path]:
    database = tmp / "catalog.sqlite3"
    database.unlink(missing_ok=True)
    raw = tmp / "raw" / "reports"
    raw.mkdir(parents=True, exist_ok=True)
    bad_path = raw / "a_bad.md"
    good_path = raw / "b_good.md"
    bad_path.write_bytes(BAD_BODY)
    good_path.write_bytes(GOOD_BODY)
    config = CatalogConfig(
        project_root=tmp, catalog_dir=tmp / "catalog",
        roots=(RootSpec(root_id=ROOT, path=tmp / "raw", kind="company_raw", priority=1),),
    )
    store = CatalogStore(database)
    now = "2026-01-01T00:00:00Z"
    with store.transaction() as connection:
        _insert(connection, "roots", {"root_id": ROOT, "path": str(tmp / "raw"),
                                      "kind": "company_raw", "priority": 1})
        for document_id, body, sha, path, relative in (
            (BAD_DOC, BAD_BODY, BAD_SHA, bad_path, "reports/a_bad.md"),
            (GOOD_DOC, GOOD_BODY, GOOD_SHA, good_path, "reports/b_good.md"),
        ):
            source_id = source_id_for_sha256(sha)
            _insert(connection, "sources", {
                "source_id": source_id, "content_sha256": sha, "byte_size": len(body),
                "mime_type": "text/markdown", "relative_path": relative, "root_id": ROOT,
                "source_type": "regulatory_filing", "source_status": "active",
                "first_seen_at": now, "last_seen_at": now})
            _insert(connection, "documents", {
                "document_id": document_id, "primary_source_id": source_id,
                "title": Path(relative).stem, "source_type": "regulatory_filing",
                "document_kind": "annual_report", "published_date": "2026-06-18",
                "source_status": "active", "metadata_priority": 1,
                "metadata_json": "{}", "first_seen_at": now, "last_seen_at": now})
            _insert(connection, "locations", {
                "location_id": f"loc-{Path(relative).stem}", "root_id": ROOT,
                "relative_path": relative, "absolute_path": str(path),
                "source_id": source_id, "document_id": document_id,
                "role": "original_primary", "location_status": "active",
                "last_seen_run": "run-1",
                "manifest_json": json.dumps(_manifest(source_id, sha, len(body), relative)),
                "metadata_json": "{}"})
    return config, store, bad_path, good_path


def _normalized_on_disk(catalog_dir: Path) -> list[str]:
    return sorted(path.parent.name for path in catalog_dir.rglob("normalized.md"))


def run_case(label: str, tmp: Path) -> dict:
    config, store, bad_path, _good_path = _seed(tmp)
    # The bad row's file is REPLACED after the scan: it still exists (so the R1 missing-file
    # guard passes) but its bytes no longer match the manifest.
    bad_path.write_bytes(BAD_REPLACEMENT)
    outcome: dict = {"label": label, "wiki_src": str(WIKI_SRC)}
    try:
        # NO tiny parser timeout here: it is a GLOBAL run option, and the first version of
        # this probe set it to 1 ms, which failed the HEALTHY document too (measured: both
        # rows reported ValueError).  The bad row is driven purely by "the bytes on disk were
        # replaced after the scan", so the healthy row is untouched.
        report = normalize_catalog(config, store, force=True, retry_limit=3)
    except BaseException as exc:  # noqa: BLE001 - the probe reports whatever escapes
        outcome["escaped"] = True
        outcome["error"] = f"{type(exc).__name__}: {str(exc)[:160]}"
        for frame in traceback.extract_tb(sys.exc_info()[2]):
            if "normalizer.py" in frame.filename:
                outcome["raised_from"] = f"normalizer.py:{frame.lineno} {frame.line}"
    else:
        outcome["escaped"] = False
        for field in ("completed", "failed", "skipped", "unsupported"):
            outcome[field] = getattr(report, field, None)
        outcome["failure_reasons"] = dict(getattr(report, "terminal_reasons", {}) or {})
    outcome["normalized_on_disk"] = _normalized_on_disk(config.catalog_dir)
    # `normalized_on_disk` holds the derived DIRECTORY names, which are the full content
    # sha256 (derived/<sha[:2]>/<sha>/normalized.md) - the first version compared the two
    # character PREFIX against those strings and reported "not normalized" for a row whose
    # artifact row said `completed`.  Compare against the full digest.
    outcome["healthy_row_normalized"] = any(
        name == GOOD_SHA for name in outcome["normalized_on_disk"])
    with store.transaction() as connection:
        rows = connection.execute(
            "SELECT document_id, artifact_role, status FROM artifacts").fetchall()
    outcome["artifact_rows"] = [dict(row) for row in rows]
    return outcome


def prefix_mutated_case(base: Path) -> dict:
    """Run the SAME probe against a copy whose handler guard is reverted (the pre-fix shape).

    A probe that cannot fail proves nothing: this builds a temp copy of the package, replaces
    the guarded handler-ingest with the original raising call, and runs this file as a
    subprocess against it.  Pre-fix the run must ESCAPE with the healthy row starved.
    """
    import shutil
    import subprocess

    copy_root = base / "_prefix_copy"
    shutil.rmtree(copy_root, ignore_errors=True)
    (copy_root / "src").mkdir(parents=True)
    shutil.copytree(WIKI / "src" / "company_wiki", copy_root / "src" / "company_wiki")
    target = copy_root / "src" / "company_wiki" / "source_catalog" / "normalizer.py"
    text = target.read_text(encoding="utf-8")
    guarded = (
        "            bundle, ingest_problem = _ingest_without_raising(\n"
        "                primary[\"root_path\"], manifest\n"
        "            )\n"
    )
    original = (
        "            bundle = IngestService(root=Path(primary[\"root_path\"])).ingest(\n"
        "                manifest=manifest, parser_results=()\n"
        "            )\n"
    )
    if text.count(guarded) != 2:
        return {"label": "pre-fix copy", "error": "guard anchor not found twice",
                "escaped": None}
    # Revert only the GENERIC handler's call (the SECOND occurrence), which is the one this
    # probe drives: the bad row fails in the main path, the handler ingests, and pre-fix that
    # ingest re-raises SourceManifestMismatchError out of normalize_catalog.
    #
    # The first version of this mutation used rpartition and kept the LAST occurrence intact,
    # so the copy was never mutated and the "pre-fix" case passed - a mutation that does not
    # mutate is worse than none.  It is an exact index replace now, verified below.
    first = text.find(guarded)
    second = text.find(guarded, first + 1)
    mutated = text[:second] + original + text[second + len(guarded):]
    if mutated == text or mutated.count(guarded) != 1 or mutated.count(original) != 1:
        return {"label": "pre-fix copy", "escaped": None,
                "error": "mutation did not apply as intended",
                "guarded_after": mutated.count(guarded),
                "original_after": mutated.count(original)}
    target.write_text(mutated, encoding="utf-8", newline="")
    out = base / "prefix-case.json"
    env = dict(os.environ)
    env["BARFIX_WIKI_SRC"] = str(copy_root / "src")
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    # Its OWN base directory: the first version reused the parent's `case1`, whose derived
    # `normalized.md` survived `_seed` (it deletes the DATABASE, not the derived tree) and was
    # then read back as "the healthy row was normalized" - a stale-state false positive.
    prefix_base = base / "prefix_run"
    proc = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--out", str(out),
                           "--case-only", "--base", str(prefix_base)],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, timeout=900)
    if not out.is_file():
        return {"label": "pre-fix copy", "escaped": None,
                "error": f"subprocess produced no case file (exit {proc.returncode})",
                "tail": (proc.stderr or proc.stdout or "").strip().splitlines()[-3:]}
    payload = json.loads(out.read_text(encoding="utf-8"))
    case = payload["cases"][0]
    case["label"] = "pre-fix copy (handler guard reverted)"
    case["expectation"] = "escaped=true and healthy_row_normalized=false"
    case["expectation_met"] = bool(case.get("escaped")) and not case.get(
        "healthy_row_normalized")
    shutil.rmtree(copy_root, ignore_errors=True)
    return case


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--case-only", action="store_true",
                        help="run the fixed-tree case only (used by the pre-fix subprocess)")
    parser.add_argument("--base", type=Path,
                        default=Path(tempfile.gettempdir()) / "barfix-normalize-probe",
                        help="scratch root (the pre-fix subprocess gets its own)")
    args = parser.parse_args(argv)

    base = args.base
    base.mkdir(parents=True, exist_ok=True)
    record = {"artifact": "barfix-normalize-probe", "wiki_src": str(WIKI_SRC),
              "cases": [], "ran_at_utc": datetime.now(UTC).isoformat()}
    case = run_case("changed-bytes-in-the-handler", base / "case1")
    record["cases"].append(case)
    print(json.dumps(case, ensure_ascii=True, indent=2))
    record["verdict"] = {
        "escaped": case["escaped"],
        "healthy_row_normalized": case["healthy_row_normalized"],
        "failure_reasons": case.get("failure_reasons"),
        "passes_the_fix": (not case["escaped"]) and case["healthy_row_normalized"],
        "pre_fix_expected": ("a mutated copy (revert the handler guard) must show "
                             "escaped=true and healthy_row_normalized=false"),
    }
    if not args.case_only:
        pre = prefix_mutated_case(base)
        record["cases"].append(pre)
        print(json.dumps(pre, ensure_ascii=True, indent=2))
        record["verdict"]["pre_fix_copy_escaped"] = pre.get("escaped")
        record["verdict"]["pre_fix_copy_expectation_met"] = pre.get("expectation_met")
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(f"wrote {args.out}")
    print(json.dumps(record["verdict"], ensure_ascii=True, indent=2))
    ok = record["verdict"]["passes_the_fix"]
    if not args.case_only:
        ok = ok and bool(record["verdict"].get("pre_fix_copy_expectation_met"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
