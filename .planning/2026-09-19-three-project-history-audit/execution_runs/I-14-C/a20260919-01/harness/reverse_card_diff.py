"""I-14-C: reconstruct the PRE-FIX bytes of the card's edited files from the card diff.

Why not ``git show HEAD:<path>``: HEAD is NOT the pre-fix state of this working
tree.  The three modules already carried uncommitted changes before this attempt
(committed worker.py is 46991 bytes vs 48075 bytes in the pre-fix worktree), so a
HEAD-based "before" tree would exercise different code.  The reliable pre-image is
the '-' side of this card's own diff.

Method (self-verifying, no git machinery):
  1. parse ``changes.diff`` into per-file hunks,
  2. for each hunk locate its '+' block in the CURRENT worktree text and check it
     occurs exactly once -- a stale diff or drifted file is REFUSED, never guessed,
  3. replace that '+' block with the hunk's '-' block,
  4. require a POST-FIX marker to be present before replacement and absent after,
  5. hash the result against the sha256 recorded before any edit was made.

    python reverse_card_diff.py --diff <attempt>/changes.diff --cw <company-wiki> \
        --out <attempt>/before/prefix_src
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

# sha256 of the pre-edit bytes, per newline form.  The record-time hash came from
# the CRLF working tree; git speaks LF.  A file counts as reconstructed only when
# the reconstructed TEXT hashes to the recorded value in at least one newline form.
EXPECTED_PREFIX_HASHES = {
    "src/company_wiki/source_catalog/worker.py": {
        "crlf": "e83179915333eb472807b15a0580d93dcf280caadc31b0099988a3b744c469c6",
        "lf": "45776ea1806b39d120a139538f0c1852cf8e5c981fc01bef8a65fb6670558d25",
    },
    "src/company_wiki/source_catalog/observability.py": {
        "crlf": "a73826aa10c9c0bf09bb5dc73cb7466358497f9d9d8c66ba73bfe4b90ffebe5a",
        "lf": "f775a11ffbd64bdada106e2deaa5cfc21da1a4906e02ae9b3660faa58df65ceb",
    },
    "src/company_wiki/source_catalog/cli.py": {
        "crlf": "fad88c60294a7fb7fa87bbdbe2bbd7effe3ce1a2dbcc11fce96cd44afb36344b",
        "lf": "2f5c5740343697078d1e69b3a6a9ef9b0809277799c2d9c28a2d3e4048c4d512",
    },
}
# Recorded from the attempt's own sha256 pass.  cli.py is the one entry whose
# byte count is inconsistent with its digest inside binding.json (65553 recorded
# vs 64126 for HEAD's blob); the digest, not the byte count, is used here and the
# discrepancy is reported in review.md rather than smoothed over.
RECORDED_BYTE_COUNTS = {
    "src/company_wiki/source_catalog/worker.py": 48075,
    "src/company_wiki/source_catalog/observability.py": 30087,
    "src/company_wiki/source_catalog/cli.py": 65553,
}

POSTFIX_MARKERS = {
    "src/company_wiki/source_catalog/worker.py": "redact_and_truncate",
    "src/company_wiki/source_catalog/observability.py": "def redact_text",
    "src/company_wiki/source_catalog/cli.py": 'envelope["error"] = redact_text',
}


def parse_diff(text: str) -> dict[str, list[dict]]:
    files: dict[str, list[dict]] = {}
    current: str | None = None
    hunk: dict | None = None
    for line in text.splitlines():
        if line.startswith("+++ b/"):
            current = line[len("+++ b/"):]
            files.setdefault(current, [])
            hunk = None
        elif line.startswith("@@") and current is not None:
            hunk = {"header": line, "minus": [], "plus": []}
            files[current].append(hunk)
        elif hunk is not None and line.startswith("-") and not line.startswith("---"):
            hunk["minus"].append(line[1:])
        elif hunk is not None and line.startswith("+"):
            hunk["plus"].append(line[1:])
        elif hunk is not None and line.startswith(" "):
            hunk["minus"].append(line[1:])
            hunk["plus"].append(line[1:])
    return files


def splice(current: str, plus: str, minus: str) -> tuple[str, str]:
    count = current.count(plus)
    if count != 1:
        return current, f"REFUSED-anchor-count={count}"
    return current.replace(plus, minus), "spliced"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--diff", required=True)
    parser.add_argument("--cw", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    diff_text = Path(args.diff).read_text(encoding="utf-8")
    files = parse_diff(diff_text)
    cw = Path(args.cw)
    out_root = Path(args.out)
    report: dict = {"files": [], "all_ok": True}

    for rel, hunks in files.items():
        source = cw / rel
        target = out_root / rel
        if not source.is_file():
            report["files"].append({"path": rel, "status": "REFUSED-missing-source"})
            report["all_ok"] = False
            continue
        current = source.read_text(encoding="utf-8")
        marker = POSTFIX_MARKERS.get(rel)
        if marker and marker not in current:
            report["files"].append({"path": rel, "status": "REFUSED-postfix-marker-absent"})
            report["all_ok"] = False
            continue
        text = current
        status = "ok"
        for index, hunk in enumerate(hunks):
            plus_block = "\n".join(hunk["plus"])
            minus_block = "\n".join(hunk["minus"])
            text, step = splice(text, plus_block, minus_block)
            if step != "spliced":
                status = f"{step}@hunk{index}"
                break
        if status == "ok" and marker and marker in text:
            status = "REFUSED-marker-survived"
        body = text.encode("utf-8")
        digest_lf = hashlib.sha256(body).hexdigest()
        digest_crlf = hashlib.sha256(body.replace(b"\n", b"\r\n")).hexdigest()
        expected = EXPECTED_PREFIX_HASHES.get(rel, {})
        newline_form = ""
        if digest_lf == expected.get("lf"):
            newline_form = "lf"
        elif digest_crlf == expected.get("crlf"):
            newline_form = "crlf"
        else:
            status = "HASH-MISMATCH"
        if status == "ok":
            target.parent.mkdir(parents=True, exist_ok=True)
            data = body if newline_form == "lf" else body.replace(b"\n", b"\r\n")
            target.write_bytes(data)
        report["files"].append({
            "path": rel,
            "status": status,
            "newline_form": newline_form,
            "reconstructed_sha256_lf": digest_lf,
            "reconstructed_sha256_crlf": digest_crlf,
            "expected_lf": expected.get("lf"),
            "expected_crlf": expected.get("crlf"),
            "recorded_byte_count": RECORDED_BYTE_COUNTS.get(rel),
            "written_byte_count": len(data) if status == "ok" else None,
            "byte_count_agrees": (
                status == "ok" and len(data) == RECORDED_BYTE_COUNTS.get(rel)
            ),
            "target": str(target) if status == "ok" else None,
        })
        report["all_ok"] = report["all_ok"] and status == "ok"

    print(json.dumps(report, ensure_ascii=True, indent=2))
    return 0 if report["all_ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
