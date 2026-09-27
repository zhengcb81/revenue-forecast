"""R4 (B.AR residual): the CROSS-REPO end-to-end reuse call, read-only.

WHAT THIS EXERCISES
-------------------
The acceptance text asks for an end-to-end call through the REAL consumer entry point
(not the wiki's own CLI): `filing-fetch/scripts/fetch_filing.py`, whose default is
read-only reuse ("--allow-download ... default: read-only reuse", fetch_filing.py:1037-1041).
For a request that already exists in the production catalog the call must:
  * identify the company through the security-master snapshots,
  * resolve the filing through the wiki resolver,
  * come back capture-ready with `download_required: false` and zero network,
  * and leave the production catalog and every root untouched.

THE WRITE SURFACE, READ OUT OF THE CODE BEFORE RUNNING (owner's option A, 2026-09-18)
------------------------------------------------------------------------------------
CORRECTED after `B.VR-r4` F-R4-02 (P2): the first version of this table claimed the resolve
path reaches the WRITABLE store initialiser.  It does not - `cli.py:1165-1200` never touches
`get_catalog().store` (contrast `:762` for `ensure` and `:1216` for `close-gap`), it passes
`store=get_catalog().reader` (`:1193`), and the reader opens read-only (`reader.py:165/188`:
`mode=ro` + `PRAGMA query_only=ON`).  This path therefore performs NO mkdir, no WAL switch, no
additive migration and no commit; the A05/A06 analogy used before was wrong and is dropped.

| surface | reached here? | anchor |
|---|---|---|
| worker pause entries + pause owner/refcount files in the catalog dir | **NO** - the scope is only built inside `if allow_download:` (and in `_close_gap`), so on the reuse branch it is never constructed; `--no-pause-worker` is INERT for this run (it changes nothing, and the run is NOT weaker than the skill default) | fetch_filing.py:736-750, 988-999; reuse branch :758-765; files :455-457, 572, 584-585 |
| the close-gap binding temp file | **NO** - only the download/acquire path reaches it | fetch_filing.py:961-1008 |
| download / network | **NO** - `--allow-download` is absent, so `action = "resolve"` (not `ensure`) | fetch_filing.py:704-716 |
| wiki `identify` identity-cache write | **NO** - `--refresh` is not passed, so only `store.load()` runs; `write_market` is the only writer | cli.py:1080-1097, security_identity.py:319-356 (writer), :358+ (reader) |
| wiki `resolve` appending the acquisition journal | **NO** - the command reads the journal, never appends | cli.py:1183-1195 + acquisition_journal.py:128 is inside `record()` |
| any catalog write through the product store | **NO** - the resolve path hands the resolver the READ-ONLY reader; no writable store is constructed | cli.py:1193, reader.py:165/188 |
| `-shm` movement | possible; a read-only WAL reader is a sufficient cause, and on this host it also moves with no session acting - recorded, NOT attributed | phase-A boundary audit |

So the run snapshots: the production catalog triple, a full digest of every entry in the
catalog directory, the targeted files a lock/journal would appear as, the file set under
the `companies` root, the three repositories and the wiki `src` tree - before and after.

Usage::

    python run_r4_cross_repo_reuse.py [--out PATH] [--keep]
    python run_r4_cross_repo_reuse.py --verify
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import traceback
from datetime import UTC, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_OUT = HERE / "b-ar-cross-repo-reuse.json"
WIKI = Path(r"C:\Users\郑曾波\Projects\company-wiki")
FILING = Path(r"C:\Users\郑曾波\Projects\filing-fetch")
REPOS = {
    "company-wiki": WIKI,
    "revenue-forecast": Path(r"C:\Users\郑曾波\Projects\revenue-forecast"),
    "filing-fetch": FILING,
}
DEFAULT_PYTHON = Path(r"C:\Miniconda\python.exe")
FETCH = FILING / "scripts" / "fetch_filing.py"
FETCH_CONFIG = FILING / "config" / "company_wiki.json"
PRODUCTION_DB = WIKI / ".source_catalog" / "catalog.sqlite3"
CATALOG_DIR = PRODUCTION_DB.parent

# The filing B08 level 2 verified from the real bytes (4,172,424 B,
# sha256 e39fbf9c80866759b20cf005f8b1b54301e6ae2ec092aed1d774d954e44fb350).
ALIBABA = {
    "company_query": "09988",
    "market": "HK",
    "document_kind": "annual_report",
    "as_of_date": "2026-09-18",
    "expected_sha256": "e39fbf9c80866759b20cf005f8b1b54301e6ae2ec092aed1d774d954e44fb350",
    "expected_bytes": 4172424,
}
TARGET_FILES = (
    "catalog.sqlite3",
    "catalog.sqlite3-wal",
    "catalog.sqlite3-shm",
    "operation.lock",
    "runtime_policy.json",
    "acquisition_attempts.jsonl",
    "filing_fetch_pause.refcount",
    "filing_fetch_pause.owner",
    "worker_control.json",
)


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _stat_of(path: Path) -> dict:
    try:
        info = path.stat()
    except OSError as error:
        return {"exists": False, "error": f"{type(error).__name__}"}
    kind = "dir" if path.is_dir() else "file"
    return {"exists": True, "kind": kind, "size": info.st_size,
            "mtime_ns": info.st_mtime_ns}


def _dir_entries(root: Path) -> dict[str, tuple[int, int]]:
    """relative path -> (size, mtime_ns) for every entry under a directory."""
    entries: dict[str, tuple[int, int]] = {}
    if not root.is_dir():
        return entries
    for entry in sorted(root.rglob("*")):
        try:
            info = entry.stat()
        except OSError:
            entries[entry.relative_to(root).as_posix()] = (-1, -1)
            continue
        entries[entry.relative_to(root).as_posix()] = (info.st_size, info.st_mtime_ns)
    return entries


def _dir_digest(root: Path, *, entries: dict[str, tuple[int, int]] | None = None) -> dict:
    """(relative name, size, mtime_ns) digest of a directory's entries.

    Complete enough that ANY new, removed or resized entry shows up as a digest change,
    and cheap enough to run before and after on a directory holding thousands of log files.
    The harness also keeps the per-entry map in memory, so the record can NAME what moved
    instead of only saying that something did (F-R4 discipline: never report a boolean
    where the evidence can name the entry).
    """
    if not root.is_dir():
        return {"exists": False}
    materialized = _dir_entries(root) if entries is None else entries
    digest = hashlib.sha256()
    for relative, (size, mtime_ns) in sorted(materialized.items()):
        digest.update(f"{relative}\0{size}\0{mtime_ns}\n".encode())
    return {"exists": True, "entry_count": len(materialized), "digest": digest.hexdigest()}


def _diff_entries(before: dict[str, tuple[int, int]],
                  after: dict[str, tuple[int, int]], cap: int = 50) -> dict:
    """Only the differences, capped: 12k unchanged entries never enter the record."""
    changed = sorted(name for name in before.keys() & after.keys() if before[name] != after[name])
    added = sorted(after.keys() - before.keys())
    removed = sorted(before.keys() - after.keys())
    return {
        "changed": [{"path": name, "before": before[name], "after": after[name]}
                    for name in changed[:cap]],
        "changed_total": len(changed),
        "added": added[:cap],
        "added_total": len(added),
        "removed": removed[:cap],
        "removed_total": len(removed),
        "capped_at": cap,
    }


def _tree_paths_digest(root: Path, pattern: str = "**/*") -> dict:
    """Path+size digest under a root (no file hashing) - catches a new downloaded file."""
    digest = hashlib.sha256()
    count = 0
    if not root.is_dir():
        return {"exists": False}
    for entry in sorted(root.glob(pattern)):
        if not entry.is_file():
            continue
        try:
            size = entry.stat().st_size
        except OSError:
            size = -1
        digest.update(f"{entry.relative_to(root).as_posix()}\0{size}\n".encode())
        count += 1
    return {"exists": True, "file_count": count, "digest": digest.hexdigest()}


def _tree_fingerprint(root: Path) -> dict:
    files = []
    for path in sorted(root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        files.append((path.relative_to(root).as_posix(), path.stat().st_size,
                      _sha256_bytes(path.read_bytes())))
    digest = hashlib.sha256()
    for relative, size, file_digest in files:
        digest.update(f"{relative}\0{size}\0{file_digest}\n".encode())
    return {"file_count": len(files), "tree_sha256": digest.hexdigest()}


def _repos_snapshot() -> dict:
    snapshot: dict[str, dict] = {}
    for name, path in REPOS.items():
        head = subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace")
        status = subprocess.run(["git", "-C", str(path), "status", "--porcelain"],
                                capture_output=True, text=True, encoding="utf-8",
                                errors="replace")
        snapshot[name] = {"head": (head.stdout or "").strip(),
                          "porcelain": status.stdout or ""}
    return snapshot


def _pyc_digest(root: Path) -> dict:
    """(path, size, mtime_ns) digest of byte-code caches under a repo.

    F-R4-06/-07: `_tree_fingerprint` skips `__pycache__`, and the wiki children used to be
    spawned without PYTHONDONTWRITEBYTECODE, so "the source did not change" was narrower than
    it read.  The children are now spawned with that variable set AND the caches are digested,
    so the claim is established by measurement instead of by exclusion.
    """
    digest = hashlib.sha256()
    count = 0
    for path in sorted(root.rglob("*.pyc")):
        try:
            info = path.stat()
        except OSError:
            continue
        digest.update(f"{path.relative_to(root).as_posix()}\0{info.st_size}\0"
                      f"{info.st_mtime_ns}\n".encode())
        count += 1
    return {"file_count": count, "digest": digest.hexdigest()}


def snapshot() -> dict:
    entries = _dir_entries(CATALOG_DIR)
    return {
        "production_catalog": {name: _stat_of(CATALOG_DIR / name) for name in TARGET_FILES},
        "catalog_dir": _dir_digest(CATALOG_DIR, entries=entries),
        # Kept for the in-process diff only; removed before the record is written.
        "_catalog_dir_entries": entries,
        "companies_root": _tree_paths_digest(WIKI / "companies"),
        "pyc_caches": {name: _pyc_digest(path) for name, path in REPOS.items()},
        "repos": _repos_snapshot(),
        "wiki_src": _tree_fingerprint(WIKI / "src"),
    }


def run_fetch(python: Path, request: dict, work: Path, timeout: int = 600) -> dict:
    request_path = work / f"request-{_sha256_bytes(json.dumps(request, sort_keys=True).encode())[:8]}.json"
    request_path.write_text(json.dumps(request, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8", newline="")
    env = dict(os.environ)
    # F-R4-07: the children import company_wiki; without this they write __pycache__ into the
    # measured tree, which would make "the source did not change" depend on an unmeasured
    # directory.  Set here AND digested by the snapshot.
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    proc = subprocess.run(
        [str(python), "-B", str(FETCH), "--no-pause-worker", "--request-file",
         str(request_path)],
        cwd=str(FILING), capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=timeout, env=env,
    )
    stdout = proc.stdout or ""
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError:
        payload = None
    return {
        "mode": "cli",
        "argv": ["python", "scripts/fetch_filing.py", "--no-pause-worker",
                 "--request-file", request_path.name],
        "request": request,
        "exit_code": proc.returncode,
        "stdout_bytes": len(stdout.encode("utf-8")),
        "stdout_sha256": _sha256_bytes(stdout.encode("utf-8")),
        "stdout": stdout,
        "stderr_tail": (proc.stderr or "")[-1500:],
        "payload": payload,
    }


def summarise(leg: dict) -> dict:
    """The fields a reviewer can check without reading the whole envelope."""
    payload = leg.get("payload")
    if not isinstance(payload, dict):
        return {"parsed": False}
    handle = payload.get("handle") or {}
    envelope = handle.get("resolution_envelope") or {}
    identity = handle.get("company_identity") or {}
    bundle = envelope.get("bundle") or {}
    invalid = bundle.get("invalid") or {}
    return {
        "parsed": True,
        "status": payload.get("status"),
        "error_type": payload.get("error_type"),
        "error": payload.get("error"),
        "calls": payload.get("calls"),
        "downloads": payload.get("downloads"),
        "request_id": handle.get("request_id") or payload.get("request_id"),
        "identity": identity.get("canonical_name") or payload.get("identity"),
        "identity_security_id": identity.get("security_id"),
        "identity_match_basis": identity.get("match_basis"),
        "identity_verified": identity.get("verified"),
        "identity_active": identity.get("active"),
        "identity_source_name": identity.get("source_name"),
        "document_id": handle.get("document_id") or payload.get("document_id"),
        "canonical_path": handle.get("canonical_path") or payload.get("canonical_path"),
        "content_sha256": handle.get("content_sha256") or payload.get("content_sha256"),
        "byte_size": handle.get("byte_size") or payload.get("byte_size"),
        "fiscal_year": handle.get("fiscal_year"),
        "capture_ready": handle.get("capture_ready"),
        "missing_capture_fields": handle.get("missing_capture_fields"),
        "source_status": handle.get("source_status"),
        "https_url": handle.get("https_url"),
        # The envelope is where the wiki states WHAT it decided and on which policy.
        "outcome": envelope.get("outcome"),
        # `bundle_status` sits on the ENVELOPE, while `bundle` carries the hashes and the
        # per-artifact verdicts (measured: an earlier version read it from the wrong level).
        "bundle_status": envelope.get("bundle_status"),
        "bundle_hash": envelope.get("bundle_hash") or bundle.get("bundle_hash"),
        "valid_handles": sorted((bundle.get("valid_handles") or {}).keys()),
        "policy_hash": envelope.get("policy_hash"),
        "activation_epoch": envelope.get("activation_epoch"),
        "cohorts": envelope.get("cohorts"),
        "qualification_label": (envelope.get("qualification") or {}).get("label"),
        "download_events": envelope.get("download_events"),
        "journal_llm_calls": envelope.get("llm_calls"),
        "journal_parser_calls": envelope.get("parser_calls"),
        "candidate_exclusion_trace": envelope.get("candidate_exclusion_trace"),
        "invalid_artifacts": {role: item.get("reason") for role, item in invalid.items()},
        "top_level_keys": sorted(payload)[:20],
        "handle_keys": sorted(handle)[:40],
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--python", type=Path, default=DEFAULT_PYTHON)
    parser.add_argument("--workdir", type=Path,
                        default=Path(tempfile.gettempdir()) / "r4-cross-repo")
    parser.add_argument("--keep", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)

    if args.verify:
        return verify(args.out)
    for required in (FETCH, FETCH_CONFIG, PRODUCTION_DB):
        if not required.exists():
            raise SystemExit(f"missing required path: {required}")

    work = args.workdir
    if work.exists():
        shutil.rmtree(work)
    work.mkdir(parents=True)

    record: dict = {
        "artifact": "r4-cross-repo-reuse",
        "run_id": "2026-09-11_r4-phase-b",
        "purpose": ("R4: the B.AR cross-repo half - the REAL consumer entry point "
                    "(filing-fetch) resolves an already-indexed filing from the production "
                    "catalog read-only, with no download and no worker control"),
        "authorisation_basis": ("owner choice 2026-09-18 (option A): run "
                               "fetch_filing.py --no-pause-worker after the write surface has "
                               "been read out of the code and reported; production catalog "
                               "writes remain forbidden"),
        "entry_point": {"path": str(FETCH), "config": str(FETCH_CONFIG),
                        "python": str(args.python), "cwd": str(FILING),
                        "worker_pause": False, "allow_download": False},
        "write_surface": {
            "worker_pause_files": ("NOT REACHED: the scope is only built inside "
                                   "`if allow_download:` / `_close_gap`, so the reuse branch "
                                   "never constructs it and `--no-pause-worker` is inert here "
                                   "(fetch_filing.py:736-750, 988-999, 758-765)"),
            "binding_temp_file": "NOT REACHED (close-gap/download path only; :961-1008)",
            "download_or_network": "NOT REACHED (--allow-download absent => action=resolve; :704-716)",
            "identity_cache_write": "NOT REACHED (no --refresh; security_identity.py:319-356)",
            "acquisition_journal_append": "NOT REACHED (resolve reads it; cli.py:1183-1195)",
            "catalog_write_through_product_store": (
                "NOT REACHED: the resolve path passes the READ-ONLY reader "
                "(cli.py:1193) which opens mode=ro with PRAGMA query_only=ON "
                "(reader.py:165/188); no writable store is constructed, so there is no mkdir, "
                "WAL switch, additive migration or commit on this path "
                "(corrected per B.VR-r4 F-R4-02)"),
            "shm_note": ("may advance; a read-only WAL reader is a sufficient cause, so it is "
                         "recorded and not attributed"),
        },
        "legs": [],
        "workdir": str(work),
    }

    print("pre-snapshot ...")
    record["pre"] = snapshot()
    print(f"  catalog_dir entries={record['pre']['catalog_dir']['entry_count']} "
          f"companies_files={record['pre']['companies_root']['file_count']}")

    # L1 - the reuse hit, exact mode with no fiscal_year (any-year, the legacy behaviour).
    print("leg L1 (exact, any year) ...")
    l1 = run_fetch(args.python, {"schema_version": "1.1",
                                 "company_query": ALIBABA["company_query"],
                                 "market": ALIBABA["market"],
                                 "document_kind": ALIBABA["document_kind"],
                                 "as_of_date": ALIBABA["as_of_date"]}, work)
    l1.update({"id": "L1-reuse-any-year",
               "purpose": "the cross-repo reuse call for an already-indexed filing"})
    l1["summary"] = summarise(l1)
    record["legs"].append(l1)
    print(f"  exit={l1['exit_code']} status={l1['summary'].get('status')} "
          f"doc={str(l1['summary'].get('document_id'))[-12:]} "
          f"fy={l1['summary'].get('fiscal_year')}")

    discovered_year = l1["summary"].get("fiscal_year")
    if discovered_year:
        print(f"leg L2 (exact, fiscal_year={discovered_year}) ...")
        l2 = run_fetch(args.python, {"schema_version": "1.1",
                                     "company_query": ALIBABA["company_query"],
                                     "market": ALIBABA["market"],
                                     "document_kind": ALIBABA["document_kind"],
                                     "fiscal_year": discovered_year,
                                     "as_of_date": ALIBABA["as_of_date"]}, work)
        l2.update({"id": f"L2-reuse-exact-FY{discovered_year}",
                   "purpose": ("the same call pinned to the fiscal year the first response "
                               "reported (a reproducible request)")})
        l2["summary"] = summarise(l2)
        record["legs"].append(l2)
        print(f"  exit={l2['exit_code']} status={l2['summary'].get('status')}")

    # L3 - control: a year that cannot be indexed. Must not download, must not serve.
    print("leg L3 (exact, fiscal_year=2019 control) ...")
    l3 = run_fetch(args.python, {"schema_version": "1.1",
                                 "company_query": ALIBABA["company_query"],
                                 "market": ALIBABA["market"],
                                 "document_kind": ALIBABA["document_kind"],
                                 "fiscal_year": 2019,
                                 "as_of_date": ALIBABA["as_of_date"]}, work)
    l3.update({"id": "L3-control-missing-FY2019",
               "purpose": "a filing that is NOT indexed: reuse-only must refuse, not fetch"})
    l3["summary"] = summarise(l3)
    record["legs"].append(l3)
    print(f"  exit={l3['exit_code']} status={l3['summary'].get('status')} "
          f"error_type={l3['summary'].get('error_type')}")

    # L4 - control: an unknown company query must fail at identity, before resolution.
    print("leg L4 (unknown company control) ...")
    l4 = run_fetch(args.python, {"schema_version": "1.1",
                                 "company_query": "zzz-no-such-issuer-zzz",
                                 "market": ALIBABA["market"],
                                 "document_kind": ALIBABA["document_kind"],
                                 "as_of_date": ALIBABA["as_of_date"]}, work)
    l4.update({"id": "L4-control-unknown-company",
               "purpose": "identity must fail closed before any resolution"})
    l4["summary"] = summarise(l4)
    record["legs"].append(l4)
    print(f"  exit={l4['exit_code']} status={l4['summary'].get('status')} "
          f"error_type={l4['summary'].get('error_type')}")

    print("post-snapshot ...")
    record["post"] = snapshot()

    l1_summary = record["legs"][0]["summary"]
    # The CONSUMER's vocabulary is `capture_ready` (filing-fetch maps the wiki's
    # resolution onto it), so count that, and keep the wiki-side outcome separately.
    consumer_status = {"capture_ready", "reused_exact", "reused_equivalent", "verified_input"}
    reused = [leg["summary"] for leg in record["legs"]
              if leg["summary"].get("status") in consumer_status]
    record["summary"] = {
        "L1_status": l1_summary.get("status"),
        "L1_canonical_path": l1_summary.get("canonical_path"),
        "L1_content_sha256": l1_summary.get("content_sha256"),
        "L1_digest_is_the_verified_one": l1_summary.get("content_sha256")
        == ALIBABA["expected_sha256"],
        "L1_byte_size": l1_summary.get("byte_size"),
        "L1_bytes_match_b08_level2": l1_summary.get("byte_size") == ALIBABA["expected_bytes"],
        "L1_wiki_side_outcome": l1_summary.get("outcome"),
        "L1_wiki_side_qualification": l1_summary.get("qualification_label"),
        "L1_wiki_calls": l1_summary.get("calls"),
        "L1_downloads": l1_summary.get("downloads"),
        "L1_invalid_artifacts": l1_summary.get("invalid_artifacts"),
        "reuse_legs": len(reused),
        # F-R4-01 (B.VR-r4, P2): the first version asserted an invariant on
        # `summary['download_required']`, a key summarise() never emits - a vacuous check.
        # These are the decidable facts instead, plus the note that `downloads` is the
        # consumer's initialised counter (fetch_filing.py:1106) rather than proof on its own.
        "per_leg_downloads": {leg["id"]: leg["summary"].get("downloads")
                              for leg in record["legs"]},
        "allow_download_flag_passed": False,
        "control_statuses": {leg["id"]: leg["summary"].get("status")
                             for leg in record["legs"] if "control" in leg["id"]},
        "unknown_company_error_type": [leg["summary"].get("error_type")
                                       for leg in record["legs"]
                                       if leg["id"] == "L4-control-unknown-company"],
    }
    post = record["post"]
    pre = record["pre"]
    pre_entries = pre.pop("_catalog_dir_entries")
    post_entries = post.pop("_catalog_dir_entries")
    dir_diff = _diff_entries(pre_entries, post_entries)
    dir_diff["catalog_dir_changed"] = bool(
        pre["catalog_dir"].get("digest") != post["catalog_dir"].get("digest"))
    record["invariants"] = {
        "production_db_unchanged": (pre["production_catalog"]["catalog.sqlite3"]
                                    == post["production_catalog"]["catalog.sqlite3"]),
        "production_wal_unchanged": (pre["production_catalog"]["catalog.sqlite3-wal"]
                                     == post["production_catalog"]["catalog.sqlite3-wal"]),
        "no_pause_files": (not post["production_catalog"]["filing_fetch_pause.refcount"]["exists"]
                           and not post["production_catalog"]["filing_fetch_pause.owner"]["exists"]),
        # Scope stated: path + size over files (F-R4-08), so a same-size overwrite at an
        # existing path would not show up - what it DOES establish is that no new file (a
        # download) landed anywhere under the root.
        "no_new_file_under_companies": (pre["companies_root"].get("digest")
                                        == post["companies_root"].get("digest")),
        "companies_digest_scope": "relative path + size for every file (not content)",
        "repos_unchanged_during_run": all(
            pre["repos"][name]["porcelain"] == post["repos"][name]["porcelain"]
            for name in REPOS),
        "heads_unchanged": all(pre["repos"][name]["head"] == post["repos"][name]["head"]
                               for name in REPOS),
        "product_source_unchanged": pre["wiki_src"] == post["wiki_src"],
        "pyc_caches_unchanged": pre["pyc_caches"] == post["pyc_caches"],
        # Decidable replacements for the vacuous key (F-R4-01): every leg must report zero
        # downloads AND the run must never have passed --allow-download.
        "every_leg_reports_zero_downloads": all(
            (leg["summary"].get("downloads") or 0) == 0 for leg in record["legs"]),
        "allow_download_never_passed": all(
            "--allow-download" not in leg["argv"] for leg in record["legs"]),
    }
    record["catalog_dir_diff"] = dir_diff
    record["ran_at_utc"] = datetime.now(UTC).isoformat()
    for leg in record["legs"]:
        side = args.out.with_name(f"{args.out.stem}-{leg['id']}-stdout.txt")
        side.write_text(leg.get("stdout") or "", encoding="utf-8", newline="")
        leg["stdout_file"] = side.name
        leg["stdout"] = (leg.get("stdout") or "")[:2000]
    args.out.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(f"wrote {args.out}")
    print(json.dumps(record["summary"], ensure_ascii=False, indent=2))
    print(json.dumps(record["invariants"], indent=2))
    print(f"catalog_dir changed: {dir_diff['catalog_dir_changed']} "
          f"(changed={dir_diff['changed_total']} added={dir_diff['added_total']} "
          f"removed={dir_diff['removed_total']})")
    for item in dir_diff["changed"][:10]:
        print(f"    changed: {item['path']} {item['before']} -> {item['after']}")
    for name in dir_diff["added"][:10]:
        print(f"    added:   {name}")
    for name in dir_diff["removed"][:10]:
        print(f"    removed: {name}")
    failed = [name for name, ok in record["invariants"].items() if not ok]
    print("INVARIANTS FAILED: " + ", ".join(failed) if failed else "all invariants hold")
    if not args.keep:
        shutil.rmtree(work, ignore_errors=True)
    return 1 if failed else 0


def verify(out_path: Path) -> int:
    record = json.loads(out_path.read_text(encoding="utf-8"))
    live = snapshot()
    checks = {
        "production_db_still_matches": (live["production_catalog"]["catalog.sqlite3"]
                                        == record["post"]["production_catalog"]["catalog.sqlite3"]),
        "production_wal_still_matches": (live["production_catalog"]["catalog.sqlite3-wal"]
                                         == record["post"]["production_catalog"]["catalog.sqlite3-wal"]),
        "companies_root_still_matches": (live["companies_root"].get("digest")
                                         == record["post"]["companies_root"].get("digest")),
        "heads_still_match": all(live["repos"][name]["head"]
                                 == record["post"]["repos"][name]["head"] for name in REPOS),
        "wiki_src_still_matches": live["wiki_src"] == record["post"]["wiki_src"],
    }
    print(json.dumps({"checks": checks, "live": {
        "production_catalog": live["production_catalog"]["catalog.sqlite3"],
        "catalog_dir": {k: v for k, v in live["catalog_dir"].items() if k != "digest"},
    }}, ensure_ascii=False, indent=2))
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except Exception:  # noqa: BLE001 - a crash must be visible
        traceback.print_exc()
        raise SystemExit(2)
