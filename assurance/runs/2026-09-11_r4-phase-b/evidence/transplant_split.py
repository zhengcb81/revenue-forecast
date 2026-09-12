"""Split the B03/B01/B06/B07 worktree changes into ONE PATCH PER STEP, so the
transplant to the main checkout keeps the "one commit per step" discipline even
though three of the steps touch the same file (resolver.py).

The worktree (`r4b06-wip`, based on f0aacbf) carries four logical changes:
  B03  containment via commonpath (review-probe edge)          -> resolver.py + test_r4b03
  B01  CFG-08: a null read_only is refused (not nullable)      -> config.py  + test_r4b01
  B06  the qualification label + S-13 response-level blocked    -> resolver.py + new test
  B07  the version policy, unknown-version refusal, no fallback -> resolver.py + new test

Hunks are classified by CONTENT SIGNATURE, and the tool refuses to run unless
every hunk matches exactly one step and the union reproduces the whole diff -
an automatic split that silently drops a hunk would be worse than no split.

Usage:
    python evidence/transplant_split.py [--worktree DIR] [--out DIR] [--check]
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_WORKTREE = Path(tempfile.gettempdir()) / "cw-b06-wt"

# step -> (signature regexes for ADDED/REMOVED lines, files it may touch)
STEPS: dict[str, tuple[tuple[str, ...], tuple[str, ...]]] = {
    "b03": (
        (r"commonpath", r"drive root", r"_inside_configured_roots",
         r"_drive_root_configured_root", r"hardlinks are NOT distinguished",
         # the B03 review dispositions (B-VR03-01/04/06/07/08)
         r"expected_content_sha256 is PINNED", r"B03_REASON_EXPECTED_VERSION_MISMATCH",
         r"TAIL GUARD", r"B03_BYTES_VERIFIED", r"B03_BYTES_SOURCE_NONE",
         r"resolved = Path\(os\.path\.realpath",
         r"caller_supplied_version_is_pinned", r"cancellation_stops_the_read_early",
         r"cancellation_inside_the_last_read_is_honoured"),
        ("src/company_wiki/source_catalog/resolver.py",
         "tests/contract/test_r4b03_stable_bytes.py"),
    ),
    "b01": (
        (r"_require_boolean", r"nullable", r"null_boolean_is_refused",
         r"must be a boolean"),
        ("src/company_wiki/source_catalog/config.py",
         "tests/contract/test_r4b01_field_owner_alignment.py"),
    ),
    "b06": (
        (r"QUALIFICATION_", r"qualification", r"_qualification_gaps",
         r"_metadata_conflict_reason", r"B06", r"B-VR06", r"qualification_is_additive",
         r"from \.scanner import R4_PROVENANCE_KEY", r"conflict_check"),
        ("src/company_wiki/source_catalog/resolver.py",
         "tests/contract/test_r4b06_qualification.py"),
    ),
    "b07": (
        (r"B07", r"B-VR07", r"accepts EXACTLY this version", r"NO directory-level fallback",
         r"belong to phase C", r"unknown versions are refused", r"unsupported_version",
         r"B03_REASON_UNSUPPORTED_VERSION", r"foreign_version"),
        ("src/company_wiki/source_catalog/resolver.py",
         "tests/contract/test_r4b07_version_contract.py"),
    ),
}

FULL_FILE_FOR_STEP = {
    "b06": "tests/contract/test_r4b06_qualification.py",
    "b07": "tests/contract/test_r4b07_version_contract.py",
}

HUNK_RE = re.compile(r"^@@ .* @@", re.M)


def run(cmd: list[str], cwd: Path) -> str:
    # encoding matters: git emits UTF-8, while this host's default text encoding
    # is GBK, which makes subprocess's reader thread fail and stdout come back
    # as None.  Ask for UTF-8 explicitly.
    result = subprocess.run(
        cmd, cwd=str(cwd), capture_output=True, text=True,
        encoding="utf-8", errors="replace",
    )
    if result.returncode != 0:
        raise SystemExit(f"{' '.join(cmd)} failed:\n{(result.stderr or '')[-1500:]}")
    return result.stdout or ""


def split_file_diff(block: str) -> tuple[str, list[str]]:
    """Return (header, [hunks]) for one file's diff block."""
    first = HUNK_RE.search(block)
    if first is None:
        return block, []
    header = block[: first.start()]
    starts = [m.start() for m in HUNK_RE.finditer(block)]
    hunks = [
        block[starts[i]: starts[i + 1] if i + 1 < len(starts) else len(block)]
        for i in range(len(starts))
    ]
    return header, hunks


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worktree", type=Path, default=DEFAULT_WORKTREE)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--check", action="store_true",
                        help="classify only; report and exit")
    parser.add_argument("--steps", default=None,
                        help="comma-separated subset of steps to consider (e.g. b06,b07); "
                             "useful once earlier steps are already committed, because their "
                             "signatures then match only as CONTEXT lines")
    args = parser.parse_args(argv)

    worktree = args.worktree
    if not (worktree / "src").is_dir():
        raise SystemExit(f"not a worktree: {worktree}")
    candidates = set(STEPS)
    if args.steps:
        candidates = {step.strip() for step in args.steps.split(",") if step.strip()}
        unknown = candidates - set(STEPS)
        if unknown:
            raise SystemExit(f"unknown step(s): {sorted(unknown)}")
    diff = run(["git", "diff", "--unified=6"], worktree)

    patches: dict[str, list[str]] = {step: [] for step in STEPS}
    classified: list[tuple[str, str, int]] = []
    unassigned: list[str] = []

    blocks = re.split(r"(?m)^(?=diff --git )", diff)
    for block in blocks:
        if not block.strip():
            continue
        header, hunks = split_file_diff(block)
        path = re.search(r"^\+\+\+ b/(.*)$", header, re.M)
        rel = path.group(1) if path else "?"
        if not hunks:
            continue
        for index, hunk in enumerate(hunks):
            matches = [
                step
                for step, (signatures, files) in STEPS.items()
                if step in candidates and rel in files
                and any(re.search(sig, hunk) for sig in signatures)
            ]
            if len(matches) != 1:
                unassigned.append(f"{rel} hunk#{index} matches={matches}")
                continue
            step = matches[0]
            patches[step].append(header + hunk)
            classified.append((step, rel, index))

    report = {
        "worktree": str(worktree),
        "hunks_total": len(classified) + len(unassigned),
        "hunks_classified": len(classified),
        "per_step": {step: sum(1 for s, _, _ in classified if s == step) for step in STEPS},
        "unassigned": unassigned,
    }
    if unassigned:
        print("UNASSIGNED HUNKS - fix the signatures before transplanting:")
        for item in unassigned:
            print("  ", item)
        return 2

    out = args.out or Path(tempfile.gettempdir()) / "b-transplant-patches"
    out.mkdir(parents=True, exist_ok=True)
    for step, parts in patches.items():
        if not parts:
            continue
        # newline="" is load-bearing: Path.write_text would translate "\n" into
        # the platform separator, and a patch whose context lines end in CR no
        # longer applies to an LF file.
        with open(out / f"{step}.patch", "w", encoding="utf-8", newline="") as handle:
            handle.write("".join(parts))
        target = FULL_FILE_FOR_STEP.get(step)
        if target:
            content = (worktree / target).read_text(encoding="utf-8")
            with open(out / f"{step}-new-file.txt", "w", encoding="utf-8", newline="") as handle:
                handle.write(content)

    print(f"split {report['hunks_classified']}/{report['hunks_total']} hunks")
    for step, count in report["per_step"].items():
        extra = FULL_FILE_FOR_STEP.get(step)
        print(f"  {step}: {count} hunk(s)" + (f" + new file {extra}" if extra else ""))
    print("patches in", out)
    if args.check:
        return 0
    print("apply with: git apply <step>.patch   (in the main checkout)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
