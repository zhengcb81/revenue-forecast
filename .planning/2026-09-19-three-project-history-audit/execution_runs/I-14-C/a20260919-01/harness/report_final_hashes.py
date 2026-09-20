"""I-14-C r5: regenerate the hash snapshot (r4 review finding F-I14C-R4-07).

What r4's snapshot was missing and r5 restores:

* the attempt-directory ``git status --porcelain`` summary (entry set + per-directory roll-up),
  so the reviewer can see which files the attempt added or modified without running git;
* hashes for ``iso/product_r3`` (the r3 specimen used to demonstrate F-I14C-08) and for
  ``iso/product_swapped`` (the E4a order-swap control);
* ``iso/venv`` evidence - ``python.exe``, ``pyvenv.cfg``, the three distributions' ``RECORD``
  files and a captured ``pip list`` - so the binding's pinned versions are checkable;
* the r4 -> r5 before/after hashes of the six card documents in one place.

It also records the resolution of the r4 hash-form question with three independent git views of
each anchored production module (``ls-files --eol``, the ``HEAD`` blob, and ``hash-object`` with
and without filters) next to the sha256 of the on-disk bytes.

    python report_final_hashes.py --attempt <attempt> --repo <revenue-forecast> --python <iso-python>
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

MODULES = {
    "worker.py": "src/company_wiki/source_catalog/worker.py",
    "observability.py": "src/company_wiki/source_catalog/observability.py",
    "cli.py": "src/company_wiki/source_catalog/cli.py",
    "prune_retired_evidence.py": "src/company_wiki/source_catalog/prune_retired_evidence.py",
    "archive_retired_evidence.py": "src/company_wiki/source_catalog/archive_retired_evidence.py",
    "store.py": "src/company_wiki/source_catalog/store.py",
    "error_taxonomy.py": "src/company_wiki/source_catalog/error_taxonomy.py",
    "identity_cli.py": "src/company_wiki/source_catalog/identity_cli.py",
}
ISO_TREES = ("product", "product_r1", "product_r2", "product_r3", "product_fixed", "product_swapped")
DOCUMENTS = ("binding.json", "oracle.md", "commands.json", "decision.md", "review.md",
             "handoff.json")
HARNESS = (
    "apply_card_diff.py", "bench_redact.py", "build_prefix_tree.py", "drive_real_exit.py",
    "make_posix_diff.py", "materialize_prefix.py", "probe_rule.py", "redact_variants.py",
    "report_counts.py", "repro_rc2.py", "reverse_card_diff.py", "run_diagnostic_table.py",
    "run_exit_probe.py", "run_flake_evidence.py", "run_flake_frequency.py", "run_guard.py",
    "run_guard_matrix.py", "run_r5_commands.py", "run_real_cli_exit.py", "run_rule_table.py",
    "verify_git_apply.py", "analyze_compat_control.py", "copy_frequency_captures.py",
    "report_final_hashes.py", "sync_commands_json.py",
    "tests/test_i14c_real_exit_redaction.py",
)
# Key r5 evidence, so a reviewer can pin the artefacts without walking the tree.
R5_EVIDENCE = (
    "r5/counts.json",
    "r5/commands-r5-rc.json",
    "r5/commands-r5-run.stdout.txt",
    "r5/compat-control-analysis.json",
    "r5/git_apply_verification.json",
    "r5/guard/matrix.json",
    "r5/flake-evidence/summary.json",
    "r5/flake-evidence/short-basetemp/summary.json",
    "r5/flake-evidence/frequency-child_without_runtime.json",
    "r5/flake-evidence/frequency-captures.stdout.txt",
    "r5/review-append-r5.md",
    "evidence/I-14-C/qualification.json",
    "evidence/I-14-C/verdict_transcription_r5.json",
)
PIP_PACKAGES = ("pytest", "PyYAML", "requests")
CATALOG = Path(r"C:\Users\郑曾波\Projects\company-wiki\.source_catalog\catalog.sqlite3")


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_lf(path: Path) -> str | None:
    if not path.is_file():
        return None
    data = path.read_bytes().replace(b"\r\n", b"\n")
    return hashlib.sha256(data).hexdigest()


def git(repo: Path, *argv: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *argv], capture_output=True,
                          text=True, encoding="utf-8", errors="replace")
    return proc.stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--attempt", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--company-wiki", default=r"C:\Users\郑曾波\Projects\company-wiki")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    attempt = Path(args.attempt).resolve()
    repo = Path(args.repo).resolve()
    python = Path(args.python).resolve()
    cw = Path(args.company_wiki).resolve()

    r5_documents = {name: sha256_file(attempt / name) for name in DOCUMENTS}
    for extra in ("changes.diff", "r2-changes.diff", "r3-changes.diff", "r4-changes.diff",
                  "r5-changes.diff"):
        r5_documents[extra] = sha256_file(attempt / extra)

    r4_snapshot = attempt / "r4" / "final_hashes.json"
    r4_reference = json.loads(r4_snapshot.read_text(encoding="utf-8")) if r4_snapshot.is_file() else {}
    # The previous snapshot of THIS file (if any) is the pre-append state - read it before the
    # file is overwritten, so the review-append chain (r5 -> r5 + reviewer verdict) is recorded
    # the same way r4 -> r5 is.
    out_path = Path(args.out)
    previous_reference: dict = {}
    if out_path.is_file():
        try:
            previous_reference = json.loads(out_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            previous_reference = {}
    previous_documents = previous_reference.get("r5_documents", {})
    documents_previous_to_current = {
        name: {
            "previous": previous_documents.get(name),
            "current": r5_documents.get(name),
            "changed": bool(previous_documents.get(name)) and
                       previous_documents.get(name) != r5_documents.get(name),
        }
        for name in DOCUMENTS
    }
    before_after = {
        name: {
            "r4": r4_reference.get("r4_documents", {}).get(name),
            "r5": r5_documents.get(name),
            "changed": r4_reference.get("r4_documents", {}).get(name) != r5_documents.get(name),
        }
        for name in DOCUMENTS
    }

    harness = {name: sha256_file(attempt / "harness" / name) for name in HARNESS}
    iso_trees = {
        tree: {name: sha256_file(attempt / "iso" / tree / "src" / "company_wiki" /
                                 "source_catalog" / name) for name in MODULES}
        for tree in ISO_TREES
    }

    venv = attempt / "iso" / "venv"
    pip_list = subprocess.run([str(python), "-m", "pip", "list"], capture_output=True,
                              text=True, encoding="utf-8", errors="replace")
    (attempt / "r5" / "iso-venv-pip-list.txt").write_text(pip_list.stdout, encoding="utf-8")
    records = {}
    for package in PIP_PACKAGES:
        matches = sorted((venv / "Lib" / "site-packages").glob(f"{package}-*.dist-info/RECORD"))
        records[package] = {
            "dist_info": matches[0].parent.name if matches else None,
            "RECORD_sha256": sha256_file(matches[0]) if matches else None,
        }
    iso_venv = {
        "python_exe": str(venv / "Scripts" / "python.exe"),
        "python_exe_sha256": sha256_file(venv / "Scripts" / "python.exe"),
        "pyvenv_cfg_sha256": sha256_file(venv / "pyvenv.cfg"),
        "dist_records": records,
        "pip_list_evidence": "r5/iso-venv-pip-list.txt",
        "pip_list_lines": [ln for ln in pip_list.stdout.splitlines()
                           if ln.split(" ")[0].lower() in {p.lower() for p in PIP_PACKAGES}],
    }

    production: dict[str, object] = {}
    for name, rel in MODULES.items():
        path = cw / rel.replace("/", "\\")
        blob = git(cw, "rev-parse", f"HEAD:{rel}")
        production[name] = {
            "raw_sha256": sha256_file(path),
            "lf_normalised_sha256": sha256_lf(path),
            "git_blob_hash_HEAD": blob,
            "git_hash_object_filtered": git(cw, "hash-object", rel),
            "git_hash_object_no_filters": git(cw, "hash-object", "--no-filters", rel),
            "git_ls_files_eol": git(cw, "ls-files", "--eol", "--", rel),
            "worktree_matches_HEAD_blob_after_filters":
                git(cw, "hash-object", rel) == blob,
        }
    git_views = {
        "core_autocrlf": git(cw, "config", "--get", "core.autocrlf"),
        "note": (
            "blob hashes and sha256 live in different domains: with core.autocrlf=true the "
            "worktree bytes are CRLF while the HEAD blob is LF, so 'hash-object <path>' "
            "(filters applied) equals the HEAD blob hash even though the on-disk bytes differ. "
            "Compare like with like: raw_sha256 for bytes, git_* for blobs."
        ),
        "modules": production,
    }

    porcelain = {}
    for name in ("company-wiki", "revenue-forecast", "filing-fetch"):
        target = Path(r"C:\Users\郑曾波\Projects") / name
        porcelain[name] = git(target, "status", "--porcelain").splitlines()

    attempt_entries = git(repo, "status", "--porcelain", "--", str(attempt)).splitlines()
    by_directory: dict[str, int] = {}
    # git reports paths relative to the REPO root, so locate the attempt's own directory name in
    # the path instead of assuming a prefix: that also survives quoted paths.
    marker = attempt.name + "/"
    for entry in attempt_entries:
        path = entry[3:].strip().strip('"')
        index = path.find(marker)
        rel = path[index + len(marker):] if index >= 0 else path
        head = rel.split("/")[0] if "/" in rel else "(attempt root)"
        by_directory[head] = by_directory.get(head, 0) + 1
    catalog = {
        "path": str(CATALOG),
        "size": CATALOG.stat().st_size if CATALOG.is_file() else None,
        "mtime_utc": None,
        "wal": (CATALOG.parent / "catalog.sqlite3-wal").stat().st_size
        if (CATALOG.parent / "catalog.sqlite3-wal").is_file() else 0,
        "shm": (CATALOG.parent / "catalog.sqlite3-shm").stat().st_size
        if (CATALOG.parent / "catalog.sqlite3-shm").is_file() else 0,
        "shm_mtime_utc": None,
    }
    if CATALOG.is_file():
        import datetime
        catalog["mtime_utc"] = datetime.datetime.fromtimestamp(
            CATALOG.stat().st_mtime, datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    shm = CATALOG.parent / "catalog.sqlite3-shm"
    if shm.is_file():
        import datetime
        catalog["shm_mtime_utc"] = datetime.datetime.fromtimestamp(
            shm.stat().st_mtime, datetime.timezone.utc).isoformat().replace("+00:00", "Z")
    control = CATALOG.parent / "worker_control.json"

    # The review-append transition (pre-append -> post-append) is recorded here as well, so this
    # file carries both transitions: r4 -> r5 and r5 -> r5 + transcribed reviewer verdict.
    proof_path = attempt / "evidence" / "I-14-C" / "verdict_transcription_r5.json"
    append_transition: dict = {"proof_file": "evidence/I-14-C/verdict_transcription_r5.json"}
    if proof_path.is_file():
        proof = json.loads(proof_path.read_text(encoding="utf-8"))
        append_transition.update({
            "before": proof.get("review_md_before_append"),
            "after": proof.get("review_md_after_append"),
            "append_block": proof.get("append_block"),
            "prefix_check": proof.get("prefix_check"),
            "reviewer_source": proof.get("reviewer_source"),
        })

    payload = {
        "generated_by": "harness/report_final_hashes.py",
        "attempt": str(attempt),
        "documents_r4_to_r5": before_after,
        "documents_previous_snapshot_to_current": documents_previous_to_current,
        "review_append_transition": append_transition,
        "previous_snapshot_note": (
            "'previous' is the r5_documents map of the final_hashes.json that this run replaced "
            "(the pre-review-append state), so the review-append chain is recorded the same way "
            "r4 -> r5 is"
        ),
        "r5_documents": r5_documents,
        "r4_reference": r4_reference.get("r4_documents", {}),
        "r5_harness": harness,
        "r5_evidence": {name: sha256_file(attempt / name) for name in R5_EVIDENCE},
        "iso_trees": iso_trees,
        "iso_venv": iso_venv,
        "production_modules": git_views,
        "porcelain": porcelain,
        "attempt_porcelain": {
            "command": f"git -C {repo} status --porcelain -- {attempt}",
            "entry_count": len(attempt_entries),
            "by_first_path_component": dict(sorted(by_directory.items())),
            "entries": attempt_entries[:200],
            "entries_truncated": len(attempt_entries) > 200,
        },
        "production_catalog": catalog,
        "worker_control_sha256": sha256_file(control),
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    print("documents r4->r5 changed:",
          [k for k, v in before_after.items() if v["changed"]])
    print("documents changed since the previous snapshot:",
          [k for k, v in documents_previous_to_current.items() if v["changed"]])
    print("attempt porcelain entries:", len(attempt_entries))
    print("production worker raw sha256:", production["worker.py"]["raw_sha256"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
