"""B.AR (B09) — re-derive identity and hash FROM THE ORIGINAL BYTES, read-only.

The A05 read-only manifest run (see a05-readonly-manifest-run.json) captured the catalog's
own claims: per document a `content_sha256`, a `byte_size`, a location list with `root_id`,
entity rows and derived `artifacts` (normalized/summary) with their own digests.  An
acceptance review must NOT take those claims on trust: it has to go back to the original
file and recompute.

This tool does exactly that, bounded and read-only:

  * groups the captured candidates by their real `root_id` (the location rows carry it),
  * samples at most --per-root documents per root (default 3) and at most --max-docs total,
  * hashes each original file (chunked) and compares with the catalog's `content_sha256`,
  * compares the on-disk size with the catalog's `byte_size`,
  * re-reads the acquisition sidecar (`<file>.source.json`) and compares the identity
    fields the catalog reports (entity/company_name, market, security_id, fiscal_year,
    form_type, document_kind),
  * hashes each derived artifact file (normalized/summary/...) and compares its digest.

Discipline:
  * NOTHING is written outside --out (default: this directory).
  * The production catalog database is NEVER opened - the input is the already-captured
    CLI stdout, and only document/artifact FILES are read.
  * Files inside a cloud-sync folder (Dropbox/OneDrive/Google Drive/iCloud) are NOT hashed:
    reading a placeholder hydrates it, which would be a real local side effect.  They are
    reported as `skipped_cloud_sync` instead of silently passing.

    python b_ar_verify_identity_hash.py [--per-root 3] [--max-docs 20] [--out PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "a05-readonly-manifest-run.json"
A05_2 = "a05-readonly-manifest-run-A05-2-stdout.txt"
A05_2B = "a05-readonly-manifest-run-A05-2b-stdout.txt"
CLOUD_MARKERS = ("dropbox", "onedrive", "google drive", "icloud")
MAX_BYTES_PER_FILE = 512 * 1024 * 1024
IDENTITY_FIELDS = ("company_name", "market", "security_id", "fiscal_year", "form_type",
                   "document_kind", "provider", "provider_document_id")


def _sha256_file(path: Path, cap: int = MAX_BYTES_PER_FILE) -> tuple[str | None, int, str]:
    """(digest, bytes_read, status).  A file above the cap is reported, never silently ok."""
    size = path.stat().st_size
    if size > cap:
        return None, size, "skipped_over_cap"
    digest = hashlib.sha256()
    read = 0
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1 << 20)
            if not chunk:
                break
            digest.update(chunk)
            read += len(chunk)
    return digest.hexdigest(), read, "hashed"


def _ascii(value: str) -> str:
    return value if all(ord(char) < 128 for char in value) else (
        f"<CJK len={len(value)} sha256_16="
        f"{hashlib.sha256(value.encode('utf-8')).hexdigest()[:16]}>"
    )


def _load_rows() -> list[dict]:
    rows: list[dict] = []
    for name in (A05_2, A05_2B):
        path = HERE / name
        if path.is_file():
            rows.extend(json.loads(path.read_text(encoding="utf-8")))
    seen: dict[str, dict] = {}
    for row in rows:
        document_id = str(row.get("document_id") or "")
        if document_id and document_id not in seen:
            seen[document_id] = row
    return list(seen.values())


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-root", type=int, default=3)
    parser.add_argument("--max-docs", type=int, default=20)
    parser.add_argument("--out", type=Path, default=HERE / "b-ar-identity-hash.json")
    args = parser.parse_args(argv)

    run = json.loads(RUN.read_text(encoding="utf-8"))
    rows = _load_rows()

    by_root: dict[str, list[dict]] = defaultdict(list)
    for row in rows:
        locations = row.get("locations") or []
        root_id = str((locations[0].get("root_id") if locations else "") or "<no location>")
        by_root[root_id].append(row)

    sampled: list[tuple[str, dict]] = []
    for root_id in sorted(by_root):
        for row in sorted(by_root[root_id], key=lambda item: str(item.get("document_id"))):
            if len(sampled) >= args.max_docs:
                break
            if sum(1 for item in sampled if item[0] == root_id) >= args.per_root:
                break
            sampled.append((root_id, row))

    checks: list[dict] = []
    totals = Counter()
    for root_id, row in sampled:
        path = Path(str(row.get("canonical_path") or ""))
        entry: dict = {
            "root_id": root_id,
            "document_id": str(row.get("document_id")),
            "document_kind": row.get("document_kind"),
            "catalog_content_sha256": str(row.get("content_sha256") or ""),
            "catalog_byte_size": row.get("byte_size"),
            "file_name_len": len(path.name) if path.name else 0,
            "file_exists": path.is_file(),
        }
        if not entry["file_exists"]:
            # A document with no location at all is not a "missing file": the catalog
            # knows no path for it (the A05 output has such rows - sidecar-only entries
            # whose title ends in `.pdf.source`).  Classified separately on purpose.
            entry["status"] = ("no_canonical_location" if not str(row.get("canonical_path") or "")
                               else "file_missing")
            totals[entry["status"]] += 1
            checks.append(entry)
            continue
        if any(marker in str(path).lower() for marker in CLOUD_MARKERS):
            entry["status"] = "skipped_cloud_sync"
            entry["note"] = "not hashed: reading a synced placeholder would hydrate it"
            totals["skipped_cloud_sync"] += 1
            checks.append(entry)
            continue
        digest, read, status = _sha256_file(path)
        entry["status"] = status
        entry["file_size_on_disk"] = read
        entry["disk_sha256"] = digest
        totals[status] += 1
        if status != "hashed":
            # An over-cap file has NO digest: it must not be tallied as a mismatch.
            entry["size_matches_catalog"] = None
            entry["digest_matches_catalog"] = None
            checks.append(entry)
            continue
        entry["bytes_read"] = read
        entry["size_matches_catalog"] = (read == entry["catalog_byte_size"])
        entry["digest_matches_catalog"] = (digest == entry["catalog_content_sha256"])
        totals["digest_match" if entry["digest_matches_catalog"] else "digest_mismatch"] += 1

        # identity: the sidecar next to the original file, not the catalog's word for it
        sidecar = path.with_name(path.name + ".source.json")
        entry["sidecar_exists"] = sidecar.is_file()
        totals["sidecar_present" if entry["sidecar_exists"] else "sidecar_absent"] += 1
        entry["identity"] = {}
        if sidecar.is_file():
            try:
                sidecar_data = json.loads(sidecar.read_text(encoding="utf-8"))
            except (OSError, ValueError) as exc:
                entry["sidecar_error"] = type(exc).__name__
                sidecar_data = {}
            acquisition = (row.get("metadata") or {}).get("acquisition") or {}
            candidate = sidecar_data.get("candidate") or {}
            for field in IDENTITY_FIELDS:
                from_sidecar = sidecar_data.get(field, candidate.get(field))
                from_catalog = acquisition.get(field, (acquisition.get("candidate") or {}).get(field))
                if from_sidecar is None and from_catalog is None:
                    continue
                entry["identity"][field] = {
                    "sidecar_sha256_16": (hashlib.sha256(str(from_sidecar).encode("utf-8"))
                                          .hexdigest()[:16] if from_sidecar is not None else None),
                    "catalog_sha256_16": (hashlib.sha256(str(from_catalog).encode("utf-8"))
                                          .hexdigest()[:16] if from_catalog is not None else None),
                    "agree": str(from_sidecar) == str(from_catalog),
                }
            totals["identity_agree" if entry["identity"] and all(
                item["agree"] for item in entry["identity"].values())
                else "identity_disagree_or_empty"] += 1
            # the sidecar's own digest for the ORIGINAL bytes must equal the file digest
            sidecar_claim = sidecar_data.get("content_sha256")
            entry["sidecar_content_sha256_matches_disk"] = (
                sidecar_claim == digest if sidecar_claim else None)
            if entry["sidecar_content_sha256_matches_disk"] is not None:
                totals["sidecar_digest_agrees" if entry["sidecar_content_sha256_matches_disk"]
                       else "sidecar_digest_disagrees"] += 1

        artifacts = []
        for artifact in row.get("artifacts") or []:
            artifact_path = Path(str(artifact.get("path") or ""))
            item = {"role": artifact.get("artifact_role"),
                    "status": artifact.get("status"),
                    "catalog_sha256": str(artifact.get("content_sha256") or "")[:16],
                    "catalog_bytes": artifact.get("byte_size"),
                    "exists": artifact_path.is_file()}
            if item["exists"]:
                artifact_digest, artifact_read, artifact_status = _sha256_file(artifact_path)
                item["status_on_disk"] = artifact_status
                item["bytes_on_disk"] = artifact_read
                item["digest_matches_catalog"] = (artifact_digest ==
                                                  str(artifact.get("content_sha256") or ""))
                totals["artifact_digest_match" if item["digest_matches_catalog"]
                       else "artifact_digest_mismatch"] += 1
            artifacts.append(item)
        entry["artifacts"] = artifacts

        entities = [str(item.get("name") or "") for item in (row.get("entities") or [])]
        entry["entity_methods"] = sorted({str(item.get("method") or "")
                                          for item in (row.get("entities") or [])})
        entry["entity_resolved"] = any(name and not name.startswith("Unresolved")
                                       for name in entities)
        totals["entity_resolved" if entry["entity_resolved"] else "entity_unresolved"] += 1
        checks.append(entry)

    payload = {
        "tool": "b_ar_verify_identity_hash.py",
        "note": ("B.AR/B09: identity and hash re-derived from the ORIGINAL files, read-only. "
                 "The production catalog database was never opened; the catalog's claims "
                 "come from the captured read-only CLI output in this directory."),
        "source_run": {"manifest_id": run.get("manifest_id"),
                       "manifest_status_at_run": run.get("manifest_status_at_run"),
                       "approval_basis": run.get("approval_basis"),
                       "ran_at_utc": run.get("ran_at_utc")},
        "sample": {"per_root": args.per_root, "max_docs": args.max_docs,
                   "candidates_seen": len(rows),
                   "candidates_per_root": {key: len(value) for key, value in sorted(by_root.items())},
                   "documents_checked": len(checks)},
        "totals": dict(sorted(totals.items())),
        "checks": checks,
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(json.dumps({"sample": payload["sample"], "totals": payload["totals"]},
                     ensure_ascii=True, indent=2))
    print(f"wrote {args.out.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
