"""B10 mutation proof: every guard in tests/contract/test_b10_read_chain.py must KILL a mutant.

A gate whose refusals cannot be shown to fire is not a gate (the B08 lesson), and a test
whose mutant survives is not a test (the B05 lesson).  Each mutant below changes ONE thing,
the named test is run, and the change is reverted - then the revert is verified by sha256,
so a failed revert cannot be mistaken for a passing run.

INCIDENT THAT SHAPED THIS VERSION (2026-09-16): the first version mutated the REPOSITORY
working tree in place.  It restored everything correctly, but it ran while the revenue
repository's pre-push gate was executing the wiki tests, so the gate read a half-mutated
tree: it reported `SyntaxError: expected 'except' or 'finally' block` from section_query.py
and blocked the push.  Nothing was corrupted, and the gate was RIGHT to refuse - but a
verifier must not be able to break an unrelated reader of the same tree.  This version
mutates a COPY under the system temp directory and never writes inside a repository, so it
is safe to run concurrently and the "restore" question disappears.

    python b10_mutations.py [--repo PATH] [--out PATH]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_REPO = HERE.parents[4] / "company-wiki"
TEST_REL = "tests/contract/test_b10_read_chain.py"
PACKAGE_REL = "src/company_wiki"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _make_copy(repo: Path, work: Path) -> Path:
    """A temp copy carrying only what the gate test needs: the package, the test, pytest.ini."""
    root = work / "repo"
    if root.exists():
        shutil.rmtree(root)
    (root / "tests" / "contract").mkdir(parents=True)
    shutil.copytree(repo / PACKAGE_REL, root / PACKAGE_REL)
    shutil.copy2(repo / TEST_REL, root / TEST_REL)
    ini = repo / "pytest.ini"
    if ini.is_file():
        shutil.copy2(ini, root / "pytest.ini")
    return root


MUTANTS: list[dict] = [
    {
        "id": "M1",
        "file": "src/company_wiki/source_catalog/service.py",
        "test": "test_b10_v1_adapter_delegates_to_the_single_chain",
        "why": "the v1 adapter goes back to its own parse (the second implementation)",
        "replace": ("    return metadata_object(raw)",
                    "    try:\n        payload = json.loads(raw or \"{}\")\n"
                    "    except (TypeError, ValueError, RecursionError):\n        return {}\n"
                    "    return payload if isinstance(payload, dict) else {}"),
    },
    {
        "id": "M2",
        "file": "src/company_wiki/source_catalog/section_query.py",
        "test": "test_b10_no_new_confirmed_direct_reader",
        "why": "a NEW direct reader appears in a symbol that is not in the baseline",
        "replace": ("        meta = json.loads(row[\"metadata_json\"] or \"{}\")",
                    "        meta = json.loads(row[\"metadata_json\"] or \"{}\")\n"
                    "        extra = json.loads(row[\"metadata_json\"] or \"{}\")\n"
                    "        meta = {**meta, **extra}"),
    },
    {
        "id": "M3",
        "file": "src/company_wiki/source_catalog/normalizer.py",
        "test": "test_b10_baseline_has_no_stale_entry",
        "why": ("a DEFERRED baselined site (normalizer.py::normalize_catalog, failure-path "
                "semantics) is converged without lowering the baseline - the stale-entry test "
                "must catch the un-lowered entry.  Retargeted after batch 1 converged the "
                "original artifact_backfill site for real."),
        "replace": ("        metadata = json.loads(document[\"metadata_json\"])",
                    "        metadata = metadata_object(document[\"metadata_json\"])"),
    },
    {
        "id": "M4",
        "file": "src/company_wiki/source_catalog/reader.py",
        "test": "test_b10_claim_level_adapters_never_read_bytes",
        "why": "the claim-level adapter starts reading bytes instead of the claim",
        "replace": ("        document = self.document(document_id)\n"
                    "        if document is None:\n            return None\n"
                    "        handle: dict[str, Any] = dict(document)",
                    "        document = self.document(document_id)\n"
                    "        if document is None:\n            return None\n"
                    "        _ = Path(str(document[\"document_id\"])).read_bytes()\n"
                    "        handle: dict[str, Any] = dict(document)"),
    },
    {
        "id": "M5",
        "file": "src/company_wiki/source_catalog/read_chain.py",
        "test": "test_b10_registered_adapters_are_complete_and_importable",
        "why": "a registered adapter loses its removal condition",
        "replace": ("        \"version\": \"1\",\n"
                    "        \"semantics\": \"same contract as the single chain; "
                    "name kept as the v1 adapter\",",
                    "        \"version\": \"1\","),
    },
    {
        "id": "M6",
        "file": "src/company_wiki/source_catalog/read_chain.py",
        "test": "test_b10_registered_adapters_are_complete_and_importable",
        "why": "the registry points at a symbol that does not exist",
        "replace": ("    \"company_wiki.source_catalog.reader.ReadOnlyCatalogReader.bundle\": {",
                    "    \"company_wiki.source_catalog.reader.ReadOnlyCatalogReader."
                    "bundle_typo\": {"),
    },
    {
        "id": "M7",
        "file": "src/company_wiki/source_catalog/adapters/parity.py",
        "test": "test_b10_no_new_confirmed_direct_reader",
        "why": ("a NEW direct reader appears in the adapters/ SUBDIRECTORY - the case the "
                "first non-recursive scan could not see"),
        "append": ("\n\ndef _b10_mutation_probe(row):\n"
                   "    \"\"\"Only exists while this mutant is in place.\"\"\"\n"
                   "    return json.loads(row[\"metadata_json\"] or \"{}\")\n"),
    },
    {
        "id": "M8",
        "file": "src/company_wiki/source_catalog/adapters/parity.py",
        "test": "test_b10_no_new_column_value_handoff",
        "why": ("the parse-by-helper BYPASS: a generic helper plus a call site that names the "
                "column - the shape the json.loads scan cannot see (measured: the gate passed "
                "on exactly this probe before the handoff ratchet existed)"),
        "append": ("\n\ndef _b10_vr_parse(raw):\n"
                   "    \"\"\"Generic parameter: the loads scan sees no column here.\"\"\"\n"
                   "    return json.loads(raw or \"{}\")\n\n\n"
                   "def _b10_vr_classify(row):\n"
                   "    \"\"\"Only exists while this mutant is in place.\"\"\"\n"
                   "    return _b10_vr_parse(row[\"metadata_json\"]).get(\"document_kind\")\n"),
    },
]


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--out", type=Path, default=HERE / "b10-mutations.json")
    args = parser.parse_args(argv)

    status_before = _git_status(args.repo)
    fingerprint_before = _repo_fingerprint(args.repo)
    results: list[dict] = []
    with tempfile.TemporaryDirectory(prefix="b10-mut-") as tmp:
        copy = _make_copy(args.repo, Path(tmp))
        for mutant in MUTANTS:
            path = copy / mutant["file"]
            text = path.read_text(encoding="utf-8")
            if "append" in mutant:
                # Appending needs no anchor and works on files whose content is unknown to
                # this harness - which is what makes the adapters/ mutant expressible.
                mutated = text + mutant["append"]
                applied = True
            else:
                old, new = mutant["replace"]
                applied = text.count(old) == 1
                mutated = text.replace(old, new)
            if not applied:
                results.append({"id": mutant["id"], "applied": False,
                                "detail": f"anchor found {text.count(mutant['replace'][0])} times",
                                "killed": None})
                continue
            path.write_text(mutated, encoding="utf-8", newline="")
            proc = subprocess.run(
                [sys.executable, "-m", "pytest", TEST_REL, "-q", "-k", mutant["test"],
                 "-p", "no:cacheprovider"],
                cwd=str(copy), capture_output=True, text=True, encoding="utf-8",
                errors="replace",
                env={**__import__("os").environ, "PYTHONPATH": str(copy / "src")},
            )
            tail = (proc.stdout or "").strip().splitlines()[-1][:120] if proc.stdout else ""
            results.append({
                "id": mutant["id"], "applied": True, "killed": proc.returncode != 0,
                # A kill by COLLECTION ERROR is not a kill by assertion.  pytest's exit code
                # says which: 1 = tests failed, 2 = interrupted/collection error.  The first
                # version of this harness matched on the words in the output line, which is a
                # weaker signal than the code itself.
                "killed_by": ("assertion" if proc.returncode == 1 else
                              "collection_or_other_error" if proc.returncode != 0 else "-"),
                "pytest_exit_code": proc.returncode,
                "test": mutant["test"], "why": mutant["why"],
                "exit_code": proc.returncode, "tail": tail,
            })
            path.write_text(text, encoding="utf-8", newline="")
        base = subprocess.run(
            [sys.executable, "-m", "pytest", TEST_REL, "-q", "-p", "no:cacheprovider"],
            cwd=str(copy), capture_output=True, text=True, encoding="utf-8", errors="replace",
            env={**__import__("os").environ, "PYTHONPATH": str(copy / "src")},
        )
    status_after = _git_status(args.repo)
    fingerprint_after = _repo_fingerprint(args.repo)
    payload = {
        "tool": "b10_mutations.py",
        "note": ("each mutant changes ONE thing in a TEMP COPY of the package; the named test "
                 "must FAIL while it is in place. The repository is never written to, which is "
                 "verified two ways: `git status --porcelain` identical before/after (primary), "
                 "and a line-ending-insensitive fingerprint of every .py under src/."),
        "mutants": results,
        "all_killed": all(item.get("killed") for item in results),
        "repository_untouched": (status_before == status_after
                                 and fingerprint_before == fingerprint_after),
        "git_status_unchanged": status_before == status_after,
        "git_status_before": status_before[:400],
        "git_status_after": status_after[:400],
        "repository_fingerprint_sha256_16": fingerprint_before,
        "fingerprint_note": ("line-ending insensitive (B-VR-B10-08): CRLF is normalised to LF "
                            "before hashing, so the value is comparable across checkouts"),
        "baseline_in_copy": {
            "exit_code": base.returncode,
            "tail": (base.stdout or "").strip().splitlines()[-1][:120] if base.stdout else "",
        },
    }
    args.out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8", newline="")
    print(json.dumps({key: payload[key] for key in
                      ("all_killed", "repository_untouched", "baseline_in_copy")},
                     ensure_ascii=True, indent=2))
    for item in results:
        print(f'  {item["id"]}: killed={item.get("killed")} by={item.get("killed_by", "-")} '
              f'{item.get("tail", item.get("detail", ""))}')
    print(f"wrote {args.out.name}")
    return 0 if (payload["all_killed"] and payload["repository_untouched"]
                 and base.returncode == 0) else 1


def _repo_fingerprint(repo: Path) -> str:
    """sha256 over `path  size  normalized-sha256` of every .py under src/.

    B-VR-B10-08: the first version hashed RAW bytes, so the value depended on the checkout's
    line endings (LF vs CRLF) and could not be reproduced from git.  Content is normalised
    to \n before hashing, which keeps the comparison meaningful across checkouts; and the
    primary untouched-criterion in `main()` is now `git status --porcelain` anyway.
    """
    digest = hashlib.sha256()
    for path in sorted((repo / "src").rglob("*.py")):
        content = path.read_bytes().replace(b"\r\n", b"\n")
        digest.update(f"{path.relative_to(repo)} {len(content)} "
                      f"{hashlib.sha256(content).hexdigest()}\n".encode("utf-8"))
    return digest.hexdigest()[:16]


def _git_status(repo: Path) -> str:
    proc = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                          capture_output=True, text=True, encoding="utf-8", errors="replace")
    return (proc.stdout or "").strip()


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
