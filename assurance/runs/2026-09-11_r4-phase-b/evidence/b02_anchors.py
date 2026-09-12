"""Print the code anchors quoted by evidence/b02-implementation.md section 1.

Why this exists (B-VR02R4-04): the evidence quoted line anchors that were
"script-derived" without shipping the script, and one range (`resolve`) was
wrong.  Run this to re-derive every anchor from the current checkout:

    python evidence/b02_anchors.py

It prints `<file> <symbol> <line>` plus the sha256(16) of the file, so a
reader can compare against the evidence table without trusting it.
"""

from __future__ import annotations

import hashlib
import pathlib

WIKI = pathlib.Path(r"C:/Users/郑曾波/Projects/company-wiki")

TARGETS: dict[str, list[str]] = {
    "src/company_wiki/source_catalog/service.py": [
        "_REJECTIONS_SEGMENT =",
        "def _location_exclusion_reason(",
        "def _location_order_key(",
        "    def _annotate_locations(",
        "    def _duplicate_summary(",
    ],
    "src/company_wiki/source_catalog/resolver.py": [
        "_CANDIDATE_BYTES_CAP =",
        "_HYDRATION_ATTRIBUTES =",
        "def _sha256_of_file(",
        "def _needs_hydration(",
        "class _ReadBudget:",
        "def _local_copy_probe(",
        "def _verify_candidate(",
        "def _is_rejections_path(",
        "def _candidate_reason(",
        "class _Selection:",
        "    def __init__(",
        "    def resolve(self",
        "    def _select_candidate(",
        "    def _handle(",
    ],
}


def main() -> int:
    for rel, needles in TARGETS.items():
        path = WIKI / rel
        text = path.read_bytes()
        lines = text.decode("utf-8").splitlines()
        print(f"== {rel}  sha256(16)={hashlib.sha256(text).hexdigest()[:16]} "
              f"bytes={len(text)} lines={len(lines)}")
        for needle in needles:
            hits = [i for i, line in enumerate(lines, 1) if line.startswith(needle)]
            if not hits:
                print(f"   MISSING  {needle}")
                continue
            for hit in hits:
                print(f"   {hit:>5}  {needle}")
        # the resolve() body range, so the evidence can quote it exactly
        if rel.endswith("resolver.py"):
            body = [
                i for i, line in enumerate(lines, 1)
                if line.startswith("    def resolve(self")
            ]
            if body:
                start = body[0]
                end = start
                for i in range(start, len(lines)):
                    if lines[i].startswith("    @staticmethod") or (
                        lines[i].startswith("    def ") and i + 1 > start
                    ):
                        end = i
                        break
                print(f"   {start:>5}  resolve() body  ->  ends before line {end}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
