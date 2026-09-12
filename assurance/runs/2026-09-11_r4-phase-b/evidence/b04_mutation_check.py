"""B04 mutation harness: do the four acceptance cases have teeth?

The B04 review (B.VR b04) ran its own mutants and found that four of the new
cases are meaningful, but the step shipped no author-side mutation record (unlike
B02's harness).  This closes that gap: it applies a mutation to a PRODUCT file,
runs the B04 acceptance file, reports KILLED/SURVIVED, restores the file
byte-for-byte, and prints the file's sha256(16) before and after.

Usage (Windows PowerShell):
    python evidence/b04_mutation_check.py --all
    python evidence/b04_mutation_check.py M3 M7

Expected outcome (reviewer-verified, reproduced here): every mutant below is
KILLED by at least one case in test_r4b04_reference_stability.py.

Exit: 0 = all requested mutants killed, 1 = at least one survived,
      2 = a mutation pattern no longer exists (the code changed).
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

WIKI = pathlib.Path(r"C:/Users/郑曾波/Projects/company-wiki")
SRC = WIKI / "src/company_wiki/source_catalog"
TEST_FILE = "tests/contract/test_r4b04_reference_stability.py"

# id: (file, what it removes, original snippet, mutated snippet)
MUTATIONS: dict[str, tuple[str, str, str, str]] = {
    "M3": (
        "resolver.py",
        "the pre-B02 provider_document_id strong-identity gate",
        "            if request.provider_document_id and not strong_identity:",
        "            if False and request.provider_document_id and not strong_identity:",
    ),
    "M4": (
        "scanner.py",
        "location_id derived from (root_id, relative_path)",
        "_location_id(root.root_id, candidate.relative_path)",
        "_location_id(str(candidate.path.resolve()), \"\")",
    ),
    "M5": (
        "scanner.py",
        "the source of a location (a move must not create another version)",
        "                            item.source_id,\n                            document_id,",
        "                            root.root_id,\n                            document_id,",
    ),
    "M6": (
        "scanner.py",
        "marking unseen location rows as missing",
        '"UPDATE locations SET location_status=\'missing\' WHERE root_id=? AND last_seen_run<>? AND location_status<>\'missing\'"',
        '"SELECT 1 WHERE 0"',
    ),
    "M7": (
        "scanner.py",
        "the re-point of a location row to the new revision",
        "document_id=excluded.document_id,",
        "document_id=locations.document_id,",
    ),
}


def _run_tests() -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", TEST_FILE, "-q", "--tb=no"],
        cwd=WIKI, capture_output=True, text=True, encoding="utf-8",
        errors="replace", timeout=900,
    )
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    return proc.returncode, tail[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mutation", nargs="*", help="M3 / M4 / M5 / M6 / M7")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args(argv)
    requested = list(MUTATIONS) if args.all else args.mutation
    if not requested:
        parser.error("give one or more mutation ids (or --all)")

    survived: list[str] = []
    for name in requested:
        if name not in MUTATIONS:
            print(f"{name}: unknown mutation (known: {', '.join(MUTATIONS)})")
            return 2
        rel, label, old, new = MUTATIONS[name]
        target = SRC / rel
        original_bytes = target.read_bytes()
        uses_crlf = b"\r\n" in original_bytes
        original = original_bytes.decode("utf-8").replace("\r\n", "\n")
        before = hashlib.sha256(original_bytes).hexdigest()[:16]
        if old not in original:
            print(f"{name}: pattern NOT FOUND in {rel} - the code changed, update the harness")
            return 2

        def _render(text_lf: str) -> bytes:
            if uses_crlf:
                text_lf = text_lf.replace("\n", "\r\n")
            return text_lf.encode("utf-8")

        try:
            target.write_bytes(_render(original.replace(old, new, 1)))
            code, summary = _run_tests()
            verdict = "KILLED" if code != 0 else "SURVIVED"
            if verdict == "SURVIVED":
                survived.append(name)
            print(f"{name} ({rel}: {label}): {verdict} | {summary}")
        finally:
            target.write_bytes(original_bytes)
        after = hashlib.sha256(target.read_bytes()).hexdigest()[:16]
        assert before == after, f"{rel} not restored ({before} -> {after})"

    print(f"restored: all product files byte-identical")
    return 0 if not survived else 1


if __name__ == "__main__":
    raise SystemExit(main())
