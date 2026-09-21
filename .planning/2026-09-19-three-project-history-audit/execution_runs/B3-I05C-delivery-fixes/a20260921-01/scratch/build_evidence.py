"""Generate changes.diff, hash manifests and the provenance records."""
from __future__ import annotations

import difflib
import hashlib
import json
from pathlib import Path

ATTEMPT = Path(__file__).resolve().parents[1]
FIXED = ATTEMPT / "iso" / "fixed"
PRISTINE = ATTEMPT / "iso" / "pristine"

PAIRS = [
    ("RF:scripts/company_wiki_source.py",
     PRISTINE / "rf_scripts" / "company_wiki_source.py",
     FIXED / "rf_scripts" / "company_wiki_source.py"),
    ("CW:src/company_wiki/source_catalog/artifact_dag.py",
     PRISTINE / "cw_source_catalog" / "artifact_dag.py",
     FIXED / "cw_source_catalog" / "artifact_dag.py"),
    ("I-05-C:retry-count-vs-artifact-count.json",
     PRISTINE / "tests" / "retry-count-vs-artifact-count.json",
     FIXED / "tests" / "retry-count-vs-artifact-count.json"),
]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def main() -> int:
    diff_chunks = []
    before = {}
    after = {}
    for label, old, new in PAIRS:
        before[label] = {"sha256": sha(old), "bytes": old.stat().st_size}
        after[label] = {"sha256": sha(new), "bytes": new.stat().st_size}
        old_lines = old.read_text(encoding="utf-8").splitlines(keepends=True)
        new_lines = new.read_text(encoding="utf-8").splitlines(keepends=True)
        diff_chunks.append(f"### {label}\n")
        diff_chunks.append(f"# before {before[label]['sha256']}\n")
        diff_chunks.append(f"# after  {after[label]['sha256']}\n")
        diff_chunks.extend(difflib.unified_diff(
            old_lines, new_lines,
            fromfile=f"a/{label}", tofile=f"b/{label}", n=3))
        diff_chunks.append("\n")

    (ATTEMPT / "changes.diff").write_text(
        "".join(diff_chunks), encoding="utf-8")

    # attempt-authored files (no "before" counterpart)
    new_files = {}
    for rel in ("tests/test_w05c_minimal_production.py",
                "tests/test_fc904_artifact_selection.py",
                "tests/test_w05b_verified_artifact_read.py"):
        path = FIXED / rel
        new_files[f"B3 attempt iso/fixed/{rel}"] = {
            "sha256": sha(path), "bytes": path.stat().st_size}

    carriers = {
        "I-05-B carrier (copied verbatim)":
            ATTEMPT / "before" / "tests"
            / "test_w05b_verified_artifact_read.py",
        "I-05-C carrier (copied verbatim)":
            ATTEMPT / "before" / "tests"
            / "test_w05c_minimal_production.py",
        "production FC-904 (copied verbatim)":
            ATTEMPT / "before" / "tests"
            / "test_fc904_artifact_selection.py",
    }
    (ATTEMPT / "after").mkdir(exist_ok=True)
    (ATTEMPT / "after" / "source_hashes.json").write_text(json.dumps({
        "before": before,
        "after": after,
        "attempt_authored_files": new_files,
        "frozen_carriers_staged_before_edits": {
            k: {"sha256": sha(v), "bytes": v.stat().st_size}
            for k, v in carriers.items()},
        "production_repos_written": False,
    }, indent=2), encoding="utf-8")

    governance = {}
    for rel in ("oracle.md", "decision.md", "binding.json"):
        path = ATTEMPT / rel
        governance[rel] = {"sha256": sha(path), "bytes": path.stat().st_size}
    (ATTEMPT / "after" / "evidence_hashes.json").write_text(
        json.dumps(governance, indent=2), encoding="utf-8")

    print("changes.diff lines:",
          len((ATTEMPT / "changes.diff").read_text(encoding="utf-8").splitlines()))
    for label, meta in {**before, **after}.items():
        print(f"  {label}: {meta['sha256'][:8]} ({meta['bytes']} bytes)")
    print(json.dumps(governance, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
