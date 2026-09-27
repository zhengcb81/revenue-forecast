"""B02 mutation harness: are the review-driven guards actually load-bearing?

The third review round (B.VR rev3) found three mutants that survived the 27
acceptance cases (M5: the end-of-walk cancellation guard; M6: the anchor
predicate; M7: the anchor itself).  This harness lets anyone re-check them -
it applies one mutation to the product file, runs the B02 acceptance file,
reports KILLED/SURVIVED, and restores the file byte-for-byte.

Usage (Windows PowerShell):
    python evidence/b02_mutation_check.py M5 [M6 M7 ...]
    python evidence/b02_mutation_check.py --all

Exit: 0 = every requested mutant was KILLED, 1 = at least one survived,
      2 = the mutation pattern no longer exists (the code changed).

The product file is restored in a `finally` block, so a crash cannot leave a
mutated tree behind; the harness prints the restored file's sha256(16) so the
restoration is checkable.
"""

from __future__ import annotations

import argparse
import hashlib
import pathlib
import subprocess
import sys

WIKI = pathlib.Path(r"C:/Users/郑曾波/Projects/company-wiki")
TARGET = WIKI / "src/company_wiki/source_catalog/resolver.py"
TEST_FILE = "tests/contract/test_r4b02_candidate_selection.py"

MUTATIONS: dict[str, tuple[str, str, str]] = {
    # id: (what it removes, original snippet, mutated snippet)
    "M5": (
        "end-of-walk cancellation guard",
        '        if stop_status == "cancelled" or budget.cancelled:',
        '        if stop_status == "cancelled":',
    ),
    "M6": (
        "anchor predicate = legacy is_canonical",
        '        pre_b02_canonical = next(\n'
        '            (item for item in ordered if item.get("is_canonical")),',
        "        pre_b02_canonical = next(\n"
        '            (item for item in ordered if item["candidate_rank"] == 1),',
    ),
    "M7": (
        "the anchor is remembered at all",
        "            if location is pre_b02_canonical:",
        "            if location is pre_b02_canonical and False:",
    ),
}


def _run_tests() -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", TEST_FILE, "-q", "--tb=no"],
        cwd=WIKI, capture_output=True, text=True, encoding="utf-8",
        errors="replace",
    )
    tail = (proc.stdout or "").strip().splitlines()[-1:] or [""]
    return proc.returncode, tail[0]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mutation", nargs="*", help="M5 / M6 / M7")
    parser.add_argument("--all", action="store_true")
    args = parser.parse_args(argv)
    requested = list(MUTATIONS) if args.all else args.mutation
    if not requested:
        parser.error("give one or more mutation ids (or --all)")

    # Bytes in, bytes out: text-mode round-tripping would normalise CRLF/LF and
    # silently rewrite the file's line endings.  Patterns are written with LF,
    # so matching happens on an LF-normalised copy and the file's own newline
    # convention is restored on write.
    original_bytes = TARGET.read_bytes()
    uses_crlf = b"\r\n" in original_bytes
    original = original_bytes.decode("utf-8").replace("\r\n", "\n")
    before = hashlib.sha256(original_bytes).hexdigest()[:16]

    def _render(text_lf: str) -> bytes:
        if uses_crlf:
            text_lf = text_lf.replace("\n", "\r\n")
        return text_lf.encode("utf-8")

    survived: list[str] = []
    try:
        for name in requested:
            if name not in MUTATIONS:
                print(f"{name}: unknown mutation (known: {', '.join(MUTATIONS)})")
                return 2
            label, old, new = MUTATIONS[name]
            if old not in original:
                print(f"{name}: pattern NOT FOUND - the code changed, update the harness")
                return 2
            TARGET.write_bytes(_render(original.replace(old, new)))
            code, summary = _run_tests()
            verdict = "KILLED" if code != 0 else "SURVIVED"
            if verdict == "SURVIVED":
                survived.append(name)
            print(f"{name} ({label}): {verdict} | {summary}")
            TARGET.write_bytes(original_bytes)
    finally:
        TARGET.write_bytes(original_bytes)

    after = hashlib.sha256(TARGET.read_bytes()).hexdigest()[:16]
    print(f"restored {TARGET.name}: sha256(16) {before} -> {after} "
          f"({'identical' if before == after else 'MISMATCH'})")
    return 0 if not survived else 1


if __name__ == "__main__":
    raise SystemExit(main())
